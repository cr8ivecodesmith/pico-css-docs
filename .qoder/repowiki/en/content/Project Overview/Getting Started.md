# Getting Started

<cite>
**Referenced Files in This Document**
- [README.md](file://README.md)
- [Makefile](file://Makefile)
- [pyproject.toml](file://pyproject.toml)
- [src/pico_doc_scraper/__main__.py](file://src/pico_doc_scraper/__main__.py)
- [src/pico_doc_scraper/scraper.py](file://src/pico_doc_scraper/scraper.py)
- [src/pico_doc_scraper/utils.py](file://src/pico_doc_scraper/utils.py)
- [src/pico_doc_scraper/settings.py](file://src/pico_doc_scraper/settings.py)
- [.env](file://.env)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Basic Usage](#basic-usage)
5. [Operation Modes](#operation-modes)
6. [Output and Next Steps](#output-and-next-steps)
7. [Troubleshooting](#troubleshooting)

## Introduction
The Pico CSS Documentation Scraper is a resilient web scraper that converts the official Pico.css documentation website into well-formatted Markdown files. It’s designed to help you access the documentation offline, resume interrupted scrapes automatically, retry failed URLs, and manage state efficiently. The tool focuses only on the documentation domain, respects robots.txt, and uses polite delays to avoid overloading the server.

Why it’s useful:
- Access Pico.css documentation offline for reliable reference
- Resume scraping from where you left off if interrupted
- Retry only the URLs that failed in the previous run
- Start fresh with a clean slate when needed
- Automatic cleanup of state files and organized output

**Section sources**
- [README.md](file://README.md#L1-L15)

## Prerequisites
- Python 3.12 or newer
- A modern terminal or command prompt
- Network connectivity to access the Pico.css documentation website
- Optional: uv for virtual environment and dependency management (recommended)

**Section sources**
- [pyproject.toml](file://pyproject.toml#L7-L7)
- [.env](file://.env#L2-L3)

## Installation
Follow these steps to prepare your environment and install the scraper:

1. Open a terminal in the project root.
2. Run the setup command to create a virtual environment and install development dependencies:
   - Command: make setup
   - This creates a virtual environment and installs the project in editable mode along with dev dependencies.

After setup completes, you can run the scraper using either:
- make scrape (runs the main module)
- python -m pico_doc_scraper

Notes:
- The project requires Python 3.12+ as per the project configuration.
- The Makefile uses uv to manage the virtual environment and dependencies.

**Section sources**
- [README.md](file://README.md#L16-L21)
- [Makefile](file://Makefile#L56-L59)
- [pyproject.toml](file://pyproject.toml#L7-L7)
- [.env](file://.env#L2-L3)

## Basic Usage
There are two primary ways to start scraping:

Option A: Using the Makefile target
- Command: make scrape
- This runs the scraper in normal mode, resuming from previous state if available.

Option B: Using the Python module
- Command: python -m pico_doc_scraper
- This is equivalent to the Makefile target and supports the same CLI options.

Both approaches will:
- Load existing state (if any) and continue from where it left off
- Respect domain restrictions and politeness delays
- Save output to the scraped/ directory as Markdown files

**Section sources**
- [README.md](file://README.md#L23-L33)
- [Makefile](file://Makefile#L115-L117)
- [src/pico_doc_scraper/__main__.py](file://src/pico_doc_scraper/__main__.py#L1-L7)

## Operation Modes
The scraper supports three distinct operational modes. Choose the one that fits your needs:

### Mode 1: Basic Scraping (Resume)
- Description: Starts or resumes scraping from the last known state.
- When to use: First-time run or continuing after an interruption.
- Commands:
  - make scrape
  - python -m pico_doc_scraper

What happens:
- Loads discovered and processed URLs from data/ files
- Skips already processed URLs
- Discovers new links from each page and adds them to the queue
- Saves incremental state after each URL

**Section sources**
- [README.md](file://README.md#L25-L33)
- [Makefile](file://Makefile#L115-L117)
- [src/pico_doc_scraper/scraper.py](file://src/pico_doc_scraper/scraper.py#L287-L359)

### Mode 2: Retry Failed URLs
- Description: Retries only the URLs that failed in the previous run.
- When to use: After encountering network errors or timeouts.
- Commands:
  - make scrape-retry
  - python -m pico_doc_scraper --retry

What happens:
- Loads failed URLs from data/failed_urls.txt
- Ignores discovered/processed state
- Processes only the failed URLs
- Clears the failed file after successful completion

**Section sources**
- [README.md](file://README.md#L35-L43)
- [Makefile](file://Makefile#L119-L121)
- [src/pico_doc_scraper/scraper.py](file://src/pico_doc_scraper/scraper.py#L231-L284)

### Mode 3: Fresh Start
- Description: Clears all state and starts scraping from scratch.
- When to use: When you want to rebuild the entire documentation set.
- Commands:
  - make scrape-fresh
  - python -m pico_doc_scraper --force-fresh

What happens:
- Deletes discovered_urls.txt and processed_urls.txt
- Starts with the base documentation URL
- Discovers and processes all pages from the beginning

**Section sources**
- [README.md](file://README.md#L45-L53)
- [Makefile](file://Makefile#L123-L125)
- [src/pico_doc_scraper/scraper.py](file://src/pico_doc_scraper/scraper.py#L243-L247)

## Output and Next Steps
Where to find the generated files:
- Output directory: scraped/
- Each page becomes a Markdown file named after its URL path
- Example: /docs/button becomes button.md; /docs/forms/input becomes forms_input.md
- Special handling: the root docs URL becomes index.md

What to do next:
- Explore the scraped/ directory to review the downloaded content
- Use the Markdown files offline in your preferred editor or documentation tool
- If you encounter missing pages, run make scrape-retry to reprocess failed URLs
- To rebuild everything, run make scrape-fresh

How state is tracked:
- data/discovered_urls.txt: All URLs found during crawling
- data/processed_urls.txt: Successfully processed URLs
- data/failed_urls.txt: URLs that failed to scrape (auto-generated after runs)

**Section sources**
- [README.md](file://README.md#L77-L79)
- [src/pico_doc_scraper/scraper.py](file://src/pico_doc_scraper/scraper.py#L164-L177)
- [src/pico_doc_scraper/utils.py](file://src/pico_doc_scraper/utils.py#L130-L158)
- [src/pico_doc_scraper/settings.py](file://src/pico_doc_scraper/settings.py#L14-L17)

## Troubleshooting
Common issues and resolutions:

- Python version mismatch:
  - Symptom: Installation or runtime errors indicating incompatible Python version.
  - Resolution: Ensure Python 3.12+ is installed and configured. The project enforces this requirement.

- Virtual environment not found:
  - Symptom: Commands fail because the virtual environment is missing.
  - Resolution: Run make setup to create the environment and install dependencies.

- No failed URLs to retry:
  - Symptom: Running retry mode produces “Nothing to retry!”
  - Resolution: Verify that data/failed_urls.txt exists and contains entries, or run a normal scrape first.

- Interrupted scraping:
  - Symptom: You stopped the process mid-run.
  - Resolution: Re-run make scrape or python -m pico_doc_scraper; the scraper will resume from the last saved state.

- Domain or path filtering:
  - Symptom: Some links are missing from the output.
  - Resolution: The scraper only scrapes the allowed domain and /docs paths. This is by design.

- Network errors:
  - Symptom: Pages fail to load.
  - Resolution: Retry failed URLs using make scrape-retry or python -m pico_doc_scraper --retry.

**Section sources**
- [pyproject.toml](file://pyproject.toml#L7-L7)
- [Makefile](file://Makefile#L56-L59)
- [src/pico_doc_scraper/scraper.py](file://src/pico_doc_scraper/scraper.py#L254-L262)
- [src/pico_doc_scraper/scraper.py](file://src/pico_doc_scraper/scraper.py#L350-L356)