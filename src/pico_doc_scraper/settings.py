"""Configuration settings for the pico.css docs scraper."""

from pathlib import Path

# Base URLs
PICO_DOCS_BASE_URL = "https://picocss.com/docs"
ALLOWED_DOMAIN = "picocss.com"  # Only scrape pages from this domain

# Output directories
PROJECT_ROOT = Path(__file__).parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "scraped"
DATA_DIR = PROJECT_ROOT / "data"

# State tracking files
DISCOVERED_URLS_FILE = DATA_DIR / "discovered_urls.txt"
PROCESSED_URLS_FILE = DATA_DIR / "processed_urls.txt"
FAILED_URLS_FILE = DATA_DIR / "failed_urls.txt"

# HTTP client settings
REQUEST_TIMEOUT = 30  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds

# User agent to identify the scraper
USER_AGENT = "pico-doc-scraper/0.1.0 (Educational purposes)"

# Scraping behavior
RESPECT_ROBOTS_TXT = True
DELAY_BETWEEN_REQUESTS = 1.0  # seconds, be polite

# Output format
OUTPUT_FORMAT = "markdown"  # or "json", "html"
