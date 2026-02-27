"""Utility functions for the pico.css docs scraper."""

import json
from pathlib import Path


def ensure_output_dir(directory: Path) -> None:
    """Ensure an output directory exists.

    Args:
        directory: Path to the directory to create
    """
    directory.mkdir(parents=True, exist_ok=True)
    print(f"✓ Output directory ready: {directory}")


def save_content(output_file: Path, data: dict) -> None:
    """Save scraped content to a file.

    The format is determined by the file extension:
    - .json: Save as JSON
    - .md: Save as Markdown (title + content)
    - .html: Save raw HTML

    Args:
        output_file: Path to save the content
        data: Dictionary containing the scraped data
    """
    output_file.parent.mkdir(parents=True, exist_ok=True)

    if output_file.suffix == ".json":
        with output_file.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    elif output_file.suffix == ".md":
        with output_file.open("w", encoding="utf-8") as f:
            f.write(f"# {data.get('title', 'Untitled')}\n\n")
            f.write(data.get('content', ''))

    elif output_file.suffix == ".html":
        with output_file.open("w", encoding="utf-8") as f:
            f.write(data.get('raw_html', ''))

    else:
        # Default to text format
        with output_file.open("w", encoding="utf-8") as f:
            f.write(str(data))


def sanitize_filename(filename: str) -> str:
    """Sanitize a string to be used as a filename.

    Args:
        filename: The string to sanitize

    Returns:
        A safe filename string
    """
    # Replace problematic characters
    unsafe_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    safe_filename = filename

    for char in unsafe_chars:
        safe_filename = safe_filename.replace(char, '_')

    # Remove leading/trailing spaces and dots
    safe_filename = safe_filename.strip(' .')

    # Limit length
    max_length = 200
    if len(safe_filename) > max_length:
        safe_filename = safe_filename[:max_length]

    return safe_filename or "untitled"


def format_url(base_url: str, path: str) -> str:
    """Combine base URL with a path, handling trailing slashes.

    Args:
        base_url: The base URL
        path: The path to append

    Returns:
        The combined URL
    """
    base = base_url.rstrip('/')
    path = path.lstrip('/')
    return f"{base}/{path}" if path else base


def save_failed_urls(failed_urls: list[str], file_path: Path) -> None:
    """Save failed URLs to a file.

    Args:
        failed_urls: List of URLs that failed to scrape
        file_path: Path to the file to save URLs
    """
    if not failed_urls:
        # Remove file if no failures
        if file_path.exists():
            file_path.unlink()
        return

    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", encoding="utf-8") as f:
        for url in sorted(set(failed_urls)):
            f.write(f"{url}\n")
    print(f"\n💾 Saved {len(failed_urls)} failed URLs to {file_path}")


def load_failed_urls(file_path: Path) -> list[str]:
    """Load failed URLs from a file.

    Args:
        file_path: Path to the file containing failed URLs

    Returns:
        List of URLs to retry
    """
    if not file_path.exists():
        return []

    with file_path.open("r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]

    return urls


def save_url_set(urls: set[str], file_path: Path) -> None:
    """Save a set of URLs to a file.

    Args:
        urls: Set of URLs to save
        file_path: Path to the file to save URLs
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", encoding="utf-8") as f:
        for url in sorted(urls):
            f.write(f"{url}\n")


def load_url_set(file_path: Path) -> set[str]:
    """Load a set of URLs from a file.

    Args:
        file_path: Path to the file containing URLs

    Returns:
        Set of URLs
    """
    if not file_path.exists():
        return set()

    with file_path.open("r", encoding="utf-8") as f:
        urls = {line.strip() for line in f if line.strip()}

    return urls


def clear_state_files() -> None:
    """Clear all state tracking files."""
    from pico_doc_scraper import settings

    files_to_clear = [
        settings.DISCOVERED_URLS_FILE,
        settings.PROCESSED_URLS_FILE,
        settings.FAILED_URLS_FILE,
    ]

    for file_path in files_to_clear:
        if file_path.exists():
            file_path.unlink()
            print(f"🧹 Cleared {file_path.name}")
