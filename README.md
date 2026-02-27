# Pico.css Documentation Scraper

A resilient web scraper for the [Pico.css documentation](https://picocss.com/docs) that converts HTML pages to well-formatted Markdown.

## Features

- 🔄 **Automatic Resume**: Picks up where it left off if interrupted
- 📂 **State Tracking**: Tracks discovered, processed, and failed URLs
- 🔁 **Retry Failed URLs**: Easily retry only the URLs that failed
- 🆕 **Fresh Start Option**: Clear all state and start from scratch
- 🌐 **Domain Restriction**: Only scrapes pages from the target domain
- 📝 **HTML to Markdown**: Proper conversion using markdownify
- 🛡️ **Graceful Error Handling**: Continues scraping even if some pages fail
- ⚡ **Polite Scraping**: Configurable delays between requests
- 🌟 **JS-Aware Scraping**: Optional Playwright-based scraper for JavaScript-rendered content
- 💻 **Code Block Extraction**: Preserves code examples from documentation
- 🎯 **Single Target Mode**: Test on individual URLs without affecting scrape state

## Installation

### Basic Installation

```bash
# Set up the virtual environment and install dependencies
make setup
```

### With Browser Support (Recommended)

For JavaScript-rendered content and better code block extraction:

```bash
# Install with browser extra
uv pip install ".[browser]"

# Install Playwright browser binaries
uv run playwright install
uv run playwright install-deps
```

## Usage

### Basic Scraping

Start scraping or resume from previous state:

```bash
make scrape
# or
python -m pico_doc_scraper
```

### JS-Aware Scraping (Recommended)

For better code block extraction from JavaScript-rendered pages:

```bash
python -m pico_doc_scraper.browser_scraper
```

### Single Target Testing

Test scraping on a single URL without affecting state:

```bash
# Basic scraper
python -m pico_doc_scraper --target "https://picocss.com/docs/button"

# JS-aware scraper (recommended for code blocks)
python -m pico_doc_scraper.browser_scraper --target "https://picocss.com/docs/nav"
```

### Retry Failed URLs

Retry only URLs that failed in the previous run:

```bash
make scrape-retry
# or
python -m pico_doc_scraper --retry

# For browser scraper
python -m pico_doc_scraper.browser_scraper --retry
```

### Fresh Start

Clear all state and start from scratch:

```bash
make scrape-fresh
# or
python -m pico_doc_scraper --force-fresh

# For browser scraper
python -m pico_doc_scraper.browser_scraper --force-fresh
```

### CLI Options

**Basic Scraper:**
```bash
python -m pico_doc_scraper --help
```

Options:
- `-r, --retry`: Retry only failed URLs from previous scrape
- `-f, --force-fresh`: Start a fresh scrape, clearing all existing state
- `-t, --target URL`: Scrape a single target URL for testing (forces fresh, no state tracking)

**Browser Scraper:**
```bash
python -m pico_doc_scraper.browser_scraper --help
```

Same options as basic scraper, but uses Playwright for JavaScript rendering

## How It Works

### State Persistence

The scraper maintains three state files in the `data/` directory:

- `discovered_urls.txt`: All URLs found during crawling
- `processed_urls.txt`: Successfully processed URLs
- `failed_urls.txt`: URLs that failed to scrape

State is saved incrementally after each URL, so you can interrupt the scraper at any time (Ctrl+C) and resume later.

### Output

Scraped content is saved to the `scraped/` directory as Markdown files.

## Development

### Running Tests

```bash
make test
```

### Linting

```bash
make lint
```

### Type Checking

```bash
make type-check
```

## Configuration

Settings can be adjusted in `src/pico_doc_scraper/settings.py`:

- `PICO_DOCS_BASE_URL`: Starting URL for scraping
- `ALLOWED_DOMAIN`: Domain restriction for scraping
- `REQUEST_TIMEOUT`: HTTP request timeout in seconds
- `MAX_RETRIES`: Number of retry attempts for failed requests
- `DELAY_BETWEEN_REQUESTS`: Polite delay between requests in seconds

## Tech Stack

### Core
- **Python 3.12+**
- **httpx**: Modern HTTP client with retry logic
- **beautifulsoup4**: HTML parsing
- **markdownify**: HTML to Markdown conversion
- **click**: CLI framework

### Browser Support (Optional)
- **playwright**: Headless browser for JS-rendered content

## Project Structure

```
pico-css-docs/
├── src/pico_doc_scraper/
│   ├── __init__.py
│   ├── __main__.py          # Entry point
│   ├── scraper.py           # Main scraping logic (HTTPX-based)
│   ├── browser_scraper.py   # JS-aware scraping (Playwright-based)
│   ├── settings.py          # Configuration
│   └── utils.py             # Helper functions
├── data/                    # State tracking files (auto-generated)
├── scraped/                 # Output directory (auto-generated)
├── pyproject.toml           # Project configuration
├── Makefile                 # Development commands
└── README.md
```

## Architecture

### Decoupled Scraper Design

The project uses a pluggable architecture that separates concerns:

- **Core scraping logic** (`scraper.py`): Handles parsing, state management, and markdown conversion
- **Fetch functions**: Pluggable HTTP/browser fetchers that can be swapped
  - `fetch_page()`: HTTPX-based for static content
  - `_make_browser_fetcher()`: Playwright-based for JS-rendered content

This design makes it easy to:
- Add new scraping strategies (e.g., Selenium, requests)
- Reuse the parsing/state logic across different fetch methods
- Test individual components in isolation

### Code Block Extraction

The scraper uses a multi-step process to preserve code examples:

1. **Extract**: Find all `<pre><code>` blocks and replace with placeholders
2. **Convert**: Run markdownify on the cleaned HTML
3. **Restore**: Replace placeholders with properly fenced code blocks

This ensures code examples survive the HTML-to-Markdown conversion intact.