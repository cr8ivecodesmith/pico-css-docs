"""Main scraping logic for pico.css documentation."""

import time
from collections.abc import Callable
from urllib.parse import urljoin, urlparse

import click
import httpx
from bs4 import BeautifulSoup
from markdownify import markdownify as md

from pico_doc_scraper import settings
from pico_doc_scraper.utils import (
    clear_state_files,
    ensure_output_dir,
    load_failed_urls,
    load_url_set,
    sanitize_filename,
    save_content,
    save_failed_urls,
    save_url_set,
)


def fetch_page(url: str) -> str:
    """Fetch a page from the given URL with retry logic.

    Args:
        url: The URL to fetch

    Returns:
        The HTML content of the page

    Raises:
        httpx.HTTPError: If the request fails after retries
    """
    headers = {"User-Agent": settings.USER_AGENT}

    for attempt in range(settings.MAX_RETRIES):
        try:
            with httpx.Client(timeout=settings.REQUEST_TIMEOUT) as client:
                response = client.get(url, headers=headers, follow_redirects=True)
                response.raise_for_status()
                return response.text
        except httpx.HTTPError as e:
            if attempt < settings.MAX_RETRIES - 1:
                print(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                time.sleep(settings.RETRY_DELAY)
            else:
                raise

    # This should never be reached due to raise above, but satisfies type checker
    raise httpx.HTTPError("All retry attempts failed")


def discover_doc_links(html: str, base_url: str) -> set[str]:
    """Discover all documentation links from a page.

    Args:
        html: Raw HTML content
        base_url: Base URL to resolve relative links

    Returns:
        Set of absolute URLs found in the documentation
    """
    soup = BeautifulSoup(html, "html.parser")
    links = set()

    # Find all links
    for link in soup.find_all("a", href=True):
        href = str(link["href"])
        # Convert relative URLs to absolute
        absolute_url = urljoin(base_url, href)
        parsed = urlparse(absolute_url)

        # Strict filtering: only allowed domain and within /docs path
        if (
            parsed.netloc == settings.ALLOWED_DOMAIN
            and parsed.path.startswith("/docs")
            and not parsed.path.endswith((".pdf", ".zip", ".tar.gz"))  # Skip downloads
        ):
            # Remove fragment and query string for consistency
            clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            links.add(clean_url)

    return links


def _extract_code_blocks(soup) -> list[tuple[str, str, str]]:
    """Extract code blocks before markdown conversion.

    Returns:
        List of tuples: (placeholder_id, language, code_content)
    """
    from bs4 import BeautifulSoup as BS

    code_blocks = []

    # Find all <pre> tags that contain <code>
    for idx, pre_tag in enumerate(soup.find_all("pre")):
        code_tag = pre_tag.find("code")
        if code_tag:
            # Extract language from code tag class (e.g., "language-html")
            code_classes = code_tag.get("class", [])
            language = "html"  # default
            for cls in code_classes:
                if isinstance(cls, str) and cls.startswith("language-"):
                    language = cls.replace("language-", "")
                    break

            # Get the clean code text (removes syntax highlighting spans)
            code_text = code_tag.get_text()

            # Create a unique placeholder
            placeholder = f"|||CODEBLOCK{idx}|||"

            # Replace the <pre> tag with a placeholder paragraph
            # We need to create a new soup fragment for the placeholder
            placeholder_html = f"<p><strong>{placeholder}</strong></p>"
            placeholder_soup = BS(placeholder_html, "html.parser")
            placeholder_tag = placeholder_soup.p
            pre_tag.replace_with(placeholder_tag)

            code_blocks.append((placeholder, language, code_text))

    return code_blocks


def _restore_code_blocks(markdown: str, code_blocks: list[tuple[str, str, str]]) -> str:
    """Restore code blocks into the markdown content.

    Args:
        markdown: Markdown content with placeholders
        code_blocks: List of (placeholder_id, language, code_content) tuples

    Returns:
        Markdown with code blocks restored as fenced code blocks
    """
    result = markdown
    for placeholder, language, code_text in code_blocks:
        fenced_block = f"\n```{language}\n{code_text}\n```\n"
        # The placeholder might be wrapped in ** markers from <strong> tags
        result = result.replace(f"**{placeholder}**", fenced_block)
        result = result.replace(placeholder, fenced_block)
    return result


def parse_documentation(html: str) -> dict:
    """Parse documentation page and extract relevant content.

    Args:
        html: Raw HTML content

    Returns:
        Dictionary containing parsed content
    """
    soup = BeautifulSoup(html, "html.parser")

    # Extract title
    h1_tag = soup.find("h1")
    title = h1_tag.get_text(strip=True) if h1_tag else "Untitled"

    # Try to extract main content area (adjust selectors based on actual site structure)
    # Common content selectors for documentation sites
    main_content = None
    content_selectors = [
        "main",
        "article",
        "[role='main']",
        ".content",
        "#content",
        ".documentation",
        ".docs-content",
    ]

    for selector in content_selectors:
        main_content = soup.select_one(selector)
        if main_content:
            break

    # If no main content found, use body or entire soup
    if not main_content:
        main_content = soup.find("body") or soup

    # Remove navigation, footer, and other non-content elements
    # BUT preserve <footer class="code"> which contains code examples
    for tag in main_content.find_all(["nav", "header"]):
        tag.decompose()

    # Remove footers that are NOT code examples
    for tag in main_content.find_all("footer"):
        classes = tag.get("class")
        if not classes or "code" not in classes:
            tag.decompose()

    # Remove common navigation classes
    for tag in main_content.find_all(class_=["navigation", "sidebar", "toc", "breadcrumb"]):
        tag.decompose()

    # Extract code blocks before markdown conversion (they'll be restored after)
    code_blocks = _extract_code_blocks(main_content)

    # Convert to markdown with code-friendly settings
    markdown_content = md(
        str(main_content),
        heading_style="ATX",
        code_language="html",
        strip=[],
    )

    # Restore code blocks as fenced code blocks
    markdown_content = _restore_code_blocks(markdown_content, code_blocks)

    result = {
        "title": title,
        "content": markdown_content,
        "raw_html": str(main_content),
    }

    return result


def process_single_page(
    url: str,
    visited_urls: set[str],
    fetch_func: Callable[[str], str] = fetch_page,
) -> tuple[bool, dict | None, list[str]]:
    """Process a single page: fetch, parse, save using the provided fetch function.

    Args:
        url: URL to process
        visited_urls: Set of already visited URLs
        fetch_func: Function to use for fetching the page HTML (default: fetch_page)

    Returns:
        Tuple of (success, parsed_data, discovered_links)
    """
    try:
        # Fetch the page
        html = fetch_func(url)
        print("  ✓ Fetched")

        # Parse the content
        parsed = parse_documentation(html)
        print(f"  ✓ Parsed: {parsed['title']}")

        # Generate filename from URL path
        parsed_url = urlparse(url)
        path = parsed_url.path.strip("/")
        if path == "docs":
            filename = "index.md"
        else:
            # Convert /docs/something to something.md
            filename = path.replace("docs/", "").replace("/", "_") + ".md"
        filename = sanitize_filename(filename)

        # Save the output
        output_file = settings.OUTPUT_DIR / filename
        save_content(output_file, parsed)
        print(f"  ✓ Saved to {output_file.name}")

        # Discover new links from this page
        discovered_links = discover_doc_links(html, url)
        new_links = list(discovered_links - visited_urls)
        if new_links:
            print(f"  ✓ Discovered {len(new_links)} new links")

        return True, parsed, new_links

    except httpx.HTTPError as e:
        print(f"  ✗ HTTP error: {e}")
        return False, None, []

    except Exception as e:
        print(f"  ✗ Error processing: {e}")
        return False, None, []


def print_summary(
    page_count: int, error_count: int, errors: list[str], failed_urls: list[str]
) -> None:
    """Print final scraping summary.

    Args:
        page_count: Number of successfully scraped pages
        error_count: Number of errors encountered
        errors: List of error messages
        failed_urls: List of URLs that failed
    """
    print(f"\n{'='*60}")
    print("SCRAPING SUMMARY")
    print(f"{'='*60}")
    print(f"✓ Successfully scraped: {page_count} pages")
    print(f"✗ Errors encountered: {error_count}")
    print(f"📁 Output directory: {settings.OUTPUT_DIR}")

    if errors:
        print("\n⚠️  Error details:")
        for i, error in enumerate(errors[:10], 1):  # Show first 10 errors
            print(f"  {i}. {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more errors")

    # Save failed URLs for retry
    if failed_urls:
        save_failed_urls(failed_urls, settings.FAILED_URLS_FILE)
        print("\n🔁 To retry failed URLs, run: make scrape-retry")
    else:
        save_failed_urls([], settings.FAILED_URLS_FILE)  # Clear the file

    print(f"{'='*60}")


def load_or_initialize_state(
    force_fresh: bool, retry_mode: bool
) -> tuple[set[str], set[str], set[str]]:
    """Load existing state or initialize fresh state.

    Args:
        force_fresh: If True, clear all existing state
        retry_mode: If True, only load failed URLs

    Returns:
        Tuple of (discovered_urls, processed_urls, initial_urls)
    """
    # Handle force fresh mode
    if force_fresh:
        print("\n🆕 FORCE FRESH MODE: Clearing all existing state")
        clear_state_files()
        print()

    # Load existing state
    discovered_urls = load_url_set(settings.DISCOVERED_URLS_FILE)
    processed_urls = load_url_set(settings.PROCESSED_URLS_FILE)
    existing_failed_urls = set(load_failed_urls(settings.FAILED_URLS_FILE))

    if retry_mode:
        print("\n🔁 RETRY MODE: Retrying failed URLs")
        retry_urls = load_failed_urls(settings.FAILED_URLS_FILE)
        if not retry_urls:
            print(f"No failed URLs found in {settings.FAILED_URLS_FILE}")
            print("Nothing to retry!")
            return set(), set(), set()
        print(f"Loaded {len(retry_urls)} URLs to retry\n")
        return discovered_urls, processed_urls, set(retry_urls)

    # Resume mode: load existing discovered URLs
    if discovered_urls and not force_fresh:
        print("\n📂 RESUME MODE: Found existing state")
        print(f"  • Discovered URLs: {len(discovered_urls)}")
        print(f"  • Processed URLs: {len(processed_urls)}")
        print(f"  • Failed URLs: {len(existing_failed_urls)}")
        print(f"  • Remaining to process: {len(discovered_urls - processed_urls)}\n")
        # Start with unprocessed URLs
        initial_urls = discovered_urls - processed_urls
        if not initial_urls:
            print("All discovered URLs have been processed!")
            print("Use --force-fresh to start over, or check failed URLs.")
            return set(), set(), set()
        return discovered_urls, processed_urls, initial_urls

    # Fresh start
    print(f"Starting scrape of {settings.PICO_DOCS_BASE_URL}")
    print(f"Restricting to domain: {settings.ALLOWED_DOMAIN}")
    print(f"Delay between requests: {settings.DELAY_BETWEEN_REQUESTS}s\n")
    initial_urls = {settings.PICO_DOCS_BASE_URL}
    return initial_urls.copy(), set(), initial_urls


def scrape_docs(retry_mode: bool = False, force_fresh: bool = False) -> None:
    """Main scraping workflow.

    Args:
        retry_mode: If True, only retry URLs from the failed URLs file
        force_fresh: If True, ignore existing state and start fresh
    """
    # Load or initialize state
    discovered_urls, processed_urls, initial_urls = load_or_initialize_state(
        force_fresh, retry_mode
    )

    # Early exit if nothing to process
    if not initial_urls:
        return

    # Ensure output directories exist
    ensure_output_dir(settings.OUTPUT_DIR)
    ensure_output_dir(settings.DATA_DIR)

    visited_urls: set[str] = processed_urls.copy()  # Start with already processed URLs
    urls_to_visit = initial_urls
    page_count = 0
    error_count = 0
    errors = []
    failed_urls: list[str] = []

    try:
        while urls_to_visit:
            url = urls_to_visit.pop()

            # Skip if already visited
            if url in visited_urls:
                continue

            # Be polite - delay between requests
            if visited_urls:  # Don't delay on first request
                time.sleep(settings.DELAY_BETWEEN_REQUESTS)

            print(f"\n[{page_count + 1}] Fetching: {url}")

            success, parsed, new_links = process_single_page(url, visited_urls)

            if success:
                page_count += 1
                # Only discover new links if not in retry mode
                if not retry_mode:
                    # Add newly discovered links
                    new_discovered = set(new_links) - discovered_urls
                    if new_discovered:
                        discovered_urls.update(new_discovered)
                        urls_to_visit.update(new_discovered)
                        # Save discovered URLs incrementally
                        save_url_set(discovered_urls, settings.DISCOVERED_URLS_FILE)
            else:
                error_count += 1
                errors.append(f"Failed to process {url}")
                failed_urls.append(url)

            visited_urls.add(url)
            # Save processed URLs incrementally
            save_url_set(visited_urls, settings.PROCESSED_URLS_FILE)

    except KeyboardInterrupt:
        print("\n\n⚠️  Scraping interrupted by user")

    except Exception as e:
        print(f"\n\n⚠️  Unexpected error in main loop: {e}")
        errors.append(f"Main loop error: {e}")

    finally:
        print_summary(page_count, error_count, errors, failed_urls)


def scrape_single_target(url: str) -> None:
    """Scrape a single target URL for testing purposes.

    Args:
        url: The URL to scrape
    """
    # Ensure output directories exist
    ensure_output_dir(settings.OUTPUT_DIR)
    ensure_output_dir(settings.DATA_DIR)

    print(f"Fetching: {url}")

    try:
        success, parsed, _ = process_single_page(url, set())

        if success and parsed:
            print("\n✓ Successfully scraped target URL")
            print(f"  Title: {parsed['title']}")
            print(f"  Output: {settings.OUTPUT_DIR}")
        else:
            print("\n✗ Failed to scrape target URL")

    except Exception as e:
        print(f"\n✗ Error: {e}")


@click.command()
@click.option(
    "--retry",
    "-r",
    is_flag=True,
    help="Retry only failed URLs from previous scrape",
)
@click.option(
    "--force-fresh",
    "-f",
    is_flag=True,
    help="Start a fresh scrape, clearing all existing state",
)
@click.option(
    "--target",
    "-t",
    type=str,
    default=None,
    help="Scrape a single target URL for testing (forces fresh, no state tracking)",
)
def main(retry: bool, force_fresh: bool, target: str | None) -> None:
    """Pico.css Documentation Scraper.

    Scrapes documentation from picocss.com and converts it to markdown.
    Automatically resumes from previous state unless --force-fresh is used.
    """
    print("=" * 60)
    print("Pico.css Documentation Scraper")
    print("=" * 60)

    if target:
        print(f"\n🎯 TARGET MODE: Scraping single URL: {target}")
        print("(State tracking disabled)\n")
        scrape_single_target(target)
    else:
        scrape_docs(retry_mode=retry, force_fresh=force_fresh)

    print("\nScraping complete!")


if __name__ == "__main__":
    main()
