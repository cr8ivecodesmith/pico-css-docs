"""JS-aware scraping entrypoint for pico.css documentation.

This module uses Playwright to render pages with JavaScript before passing
HTML into the existing parsing and state management pipeline. It is designed
as a decoupled example for future JS-enabled scrapers.
"""

from __future__ import annotations

import time

import click

from pico_doc_scraper import settings
from pico_doc_scraper.scraper import (
    load_or_initialize_state,
    print_summary,
    process_single_page,
)
from pico_doc_scraper.utils import ensure_output_dir, save_url_set


def _make_browser_fetcher(page):
    """Create a fetch function that uses a Playwright page instance.

    The returned callable matches the signature expected by ``process_single_page``.
    """
    # Import locally so that the core package remains usable without Playwright
    from playwright.sync_api import Page

    if not isinstance(page, Page):  # pragma: no cover - defensive check
        raise TypeError("Expected a Playwright Page instance")

    def fetch(url: str) -> str:
        page.set_default_timeout(settings.REQUEST_TIMEOUT * 1000)
        page.set_extra_http_headers({"User-Agent": settings.USER_AGENT})
        page.goto(url, wait_until="networkidle")
        _reveal_code_examples(page)
        return page.content()

    return fetch


def _click_code_buttons(page) -> None:
    """Click buttons to reveal code examples."""
    try:
        from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
    except Exception:  # pragma: no cover
        PlaywrightTimeoutError = Exception  # type: ignore[misc,assignment]

    try:
        # Prefer accessible role/name when available
        buttons = page.get_by_role("button", name="Code").all()
        for button in buttons:
            try:
                button.click()
            except PlaywrightTimeoutError:
                continue
            except Exception:
                continue
    except Exception:
        pass


def _click_code_links(page) -> None:
    """Click links with 'Code' text to reveal code examples."""
    try:
        from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
    except Exception:  # pragma: no cover
        PlaywrightTimeoutError = Exception  # type: ignore[misc,assignment]

    try:
        code_links = page.get_by_text("Code").all()
        for link in code_links:
            try:
                link.click()
            except PlaywrightTimeoutError:
                continue
            except Exception:
                continue
    except Exception:
        pass


def _reveal_code_examples(page) -> None:
    """Try to reveal any code example panes before scraping HTML."""
    # Click on any buttons that are likely to toggle code views
    _click_code_buttons(page)
    _click_code_links(page)

    # Give the page a brief moment to render newly revealed code blocks
    try:
        page.wait_for_timeout(200)
    except Exception:
        pass


def scrape_docs_browser(retry_mode: bool = False, force_fresh: bool = False) -> None:
    """Scrape docs using a JS-enabled browser renderer.

    This reuses the existing state management and parsing logic, but swaps out
    the HTTPX-based fetcher for a Playwright-powered one.
    """
    from playwright.sync_api import sync_playwright

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

    visited_urls: set[str] = processed_urls.copy()
    urls_to_visit = initial_urls
    page_count = 0
    error_count = 0
    errors: list[str] = []
    failed_urls: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent=settings.USER_AGENT)
        fetch_with_browser = _make_browser_fetcher(page)

        try:
            while urls_to_visit:
                url = urls_to_visit.pop()

                # Skip if already visited
                if url in visited_urls:
                    continue

                # Be polite - delay between requests
                if visited_urls:  # Don't delay on first request
                    time.sleep(settings.DELAY_BETWEEN_REQUESTS)

                print(f"\n[{page_count + 1}] Fetching (JS): {url}")

                success, parsed, new_links = process_single_page(
                    url,
                    visited_urls,
                    fetch_func=fetch_with_browser,
                )

                if success:
                    page_count += 1
                    # Only discover new links if not in retry mode
                    if not retry_mode and new_links:
                        new_discovered = set(new_links) - discovered_urls
                        if new_discovered:
                            discovered_urls.update(new_discovered)
                            urls_to_visit.update(new_discovered)
                            save_url_set(discovered_urls, settings.DISCOVERED_URLS_FILE)
                else:
                    error_count += 1
                    errors.append(f"Failed to process {url}")
                    failed_urls.append(url)

                visited_urls.add(url)
                save_url_set(visited_urls, settings.PROCESSED_URLS_FILE)
        finally:
            browser.close()

    print_summary(page_count, error_count, errors, failed_urls)


def scrape_single_target_browser(url: str) -> None:
    """Scrape a single target URL with JS rendering for testing purposes.

    Args:
        url: The URL to scrape
    """
    from playwright.sync_api import sync_playwright

    # Ensure output directories exist
    ensure_output_dir(settings.OUTPUT_DIR)
    ensure_output_dir(settings.DATA_DIR)

    print(f"Fetching (JS): {url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent=settings.USER_AGENT)
        fetch_with_browser = _make_browser_fetcher(page)

        try:
            success, parsed, _ = process_single_page(
                url,
                set(),
                fetch_func=fetch_with_browser,
            )

            if success and parsed:
                print("\n✓ Successfully scraped target URL")
                print(f"  Title: {parsed['title']}")
                print(f"  Output: {settings.OUTPUT_DIR}")
            else:
                print("\n✗ Failed to scrape target URL")

        except Exception as e:
            print(f"\n✗ Error: {e}")
        finally:
            browser.close()


@click.command()
@click.option(
    "--retry",
    "-r",
    is_flag=True,
    help="Retry only failed URLs from previous JS scrape",
)
@click.option(
    "--force-fresh",
    "-f",
    is_flag=True,
    help="Start a fresh JS scrape, clearing all existing state",
)
@click.option(
    "--target",
    "-t",
    type=str,
    default=None,
    help="Scrape a single target URL for testing (forces fresh, no state tracking)",
)
def main(retry: bool, force_fresh: bool, target: str | None) -> None:
    """Pico.css Documentation Scraper (JS-rendered).

    Uses Playwright to render pages with JavaScript before scraping, intended
    as a decoupled example for JS-aware scrapers.
    """
    print("=" * 60)
    print("Pico.css Documentation Scraper (JS-rendered)")
    print("=" * 60)

    if target:
        print(f"\n🎯 TARGET MODE: Scraping single URL: {target}")
        print("(State tracking disabled)\n")
        scrape_single_target_browser(target)
    else:
        scrape_docs_browser(retry_mode=retry, force_fresh=force_fresh)

    print("\nJS-rendered scraping complete!")


if __name__ == "__main__":
    main()
