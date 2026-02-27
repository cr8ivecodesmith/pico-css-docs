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

## Installation

```bash
# Set up the virtual environment and install dependencies
make setup
```

## Usage

### Basic Scraping

Start scraping or resume from previous state:

```bash
make scrape
# or
python -m pico_doc_scraper
```

### Retry Failed URLs

Retry only URLs that failed in the previous run:

```bash
make scrape-retry
# or
python -m pico_doc_scraper --retry
```

### Fresh Start

Clear all state and start from scratch:

```bash
make scrape-fresh
# or
python -m pico_doc_scraper --force-fresh
```

### CLI Options

```bash
python -m pico_doc_scraper --help
```

Options:
- `-r, --retry`: Retry only failed URLs from previous scrape
- `-f, --force-fresh`: Start a fresh scrape, clearing all existing state

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

- **Python 3.12+**
- **httpx**: Modern HTTP client with retry logic
- **beautifulsoup4**: HTML parsing
- **markdownify**: HTML to Markdown conversion
- **click**: CLI framework

## Project Structure

```
pico-css-docs/
├── src/pico_doc_scraper/
│   ├── __init__.py
│   ├── __main__.py       # Entry point
│   ├── scraper.py        # Main scraping logic
│   ├── settings.py       # Configuration
│   └── utils.py          # Helper functions
├── data/                 # State tracking files (auto-generated)
├── scraped/              # Output directory (auto-generated)
├── pyproject.toml        # Project configuration
├── Makefile              # Development commands
└── README.md
```