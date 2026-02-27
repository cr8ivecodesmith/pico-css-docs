# Scraping Engine

<cite>
**Referenced Files in This Document**
- [README.md](file://README.md)
- [Makefile](file://Makefile)
- [pyproject.toml](file://pyproject.toml)
- [src/pico_doc_scraper/__init__.py](file://src/pico_doc_scraper/__init__.py)
- [src/pico_doc_scraper/__main__.py](file://src/pico_doc_scraper/__main__.py)
- [src/pico_doc_scraper/scraper.py](file://src/pico_doc_scraper/scraper.py)
- [src/pico_doc_scraper/settings.py](file://src/pico_doc_scraper/settings.py)
- [src/pico_doc_scraper/utils.py](file://src/pico_doc_scraper/utils.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Core Components](#core-components)
4. [Architecture Overview](#architecture-overview)
5. [Detailed Component Analysis](#detailed-component-analysis)
6. [Dependency Analysis](#dependency-analysis)
7. [Performance Considerations](#performance-considerations)
8. [Troubleshooting Guide](#troubleshooting-guide)
9. [Conclusion](#conclusion)
10. [Appendices](#appendices)

## Introduction
This document explains the core scraping engine of the Pico CSS Documentation Scraper. It focuses on the main scraping workflow implemented by the scrape_docs() function, including URL discovery algorithms, HTTP request handling with retry logic, and domain restriction enforcement. It documents the state management system enabling resume capability via load_or_initialize_state(), and the URL processing pipeline orchestrated by process_single_page(). Politeness measures such as configurable delays between requests and rate limiting strategies are covered, along with practical examples, error handling mechanisms, and performance optimization techniques. The integration with external libraries and state persistence across sessions are explained in detail.

## Project Structure
The scraping engine is organized around a small set of focused modules:
- Entry point and CLI orchestration
- Core scraping logic
- Configuration and constants
- Utilities for file I/O, sanitization, and state persistence

```mermaid
graph TB
subgraph "Package: pico_doc_scraper"
INIT["__init__.py"]
MAIN["__main__.py"]
SCRAPER["scraper.py"]
SETTINGS["settings.py"]
UTILS["utils.py"]
end
MAIN --> SCRAPER
SCRAPER --> SETTINGS
SCRAPER --> UTILS
INIT -.-> SCRAPER
```

**Diagram sources**
- [src/pico_doc_scraper/__main__.py](file://src/pico_doc_scraper/__main__.py#L1-L7)
- [src/pico_doc_scraper/scraper.py](file://src/pico_doc_scraper/scraper.py#L1-L391)
- [src/pico_doc_scraper/settings.py](file://src/pico_doc_scraper/settings.py#L1-L33)
- [src/pico_doc_scraper/utils.py](file://src/pico_doc_scraper/utils.py#L1-L175)
- [src/pico_doc_scraper/__init__.py](file://src/pico_doc_scraper/__init__.py#L1-L4)

**Section sources**
- [README.md](file://README.md#L119-L134)
- [pyproject.toml](file://pyproject.toml#L1-L75)

## Core Components
- HTTP fetching with retry logic: fetch_page()
- URL discovery with domain/path restrictions: discover_doc_links()
- Content parsing and markdown conversion: parse_documentation()
- Single-page processing pipeline: process_single_page()
- State management and resume capability: load_or_initialize_state()
- Main scraping workflow: scrape_docs()
- CLI entry point: main()

Key responsibilities:
- Enforce domain restriction and path filtering to stay within the documentation site.
- Persist state incrementally to support resuming after interruptions.
- Convert HTML content to Markdown for human-readable documentation.
- Apply politeness delays and retry logic to handle transient network issues.

**Section sources**
- [src/pico_doc_scraper/scraper.py](file://src/pico_doc_scraper/scraper.py#L24-L194)
- [src/pico_doc_scraper/scraper.py](file://src/pico_doc_scraper/scraper.py#L231-L285)
- [src/pico_doc_scraper/scraper.py](file://src/pico_doc_scraper/scraper.py#L287-L387)

## Architecture Overview
The scraping engine follows a breadth-first-like traversal controlled by a queue of URLs to visit. It enforces domain and path constraints, applies retry logic on HTTP failures, and persists state to files for resilience.

```mermaid
sequenceDiagram
participant CLI as "CLI/main()"
participant Loader as "load_or_initialize_state()"
participant Engine as "scrape_docs()"
participant Page as "process_single_page()"
participant Fetch as "fetch_page()"
participant Parser as "parse_documentation()"
participant Disc as "discover_doc_links()"
participant Utils as "utils helpers"
CLI->>Loader : "Initialize state (fresh/resume/retry)"
Loader-->>Engine : "Initial sets : discovered, processed, urls_to_visit"
Engine->>Engine : "Loop until urls_to_visit empty"
Engine->>Page : "Process next URL"
Page->>Fetch : "HTTP GET with retry"
Fetch-->>Page : "HTML content"
Page->>Parser : "Convert to markdown"
Parser-->>Page : "Parsed content"
Page->>Utils : "Save content to file"
Page->>Disc : "Discover doc links"
Disc-->>Page : "New links"
Page-->>Engine : "Success + new links"
Engine->>Utils : "Persist discovered/processed"
Engine-->>CLI : "Summary"
```

**Diagram sources**
- [src/pico_doc_scraper/scraper.py](file://src/pico_doc_scraper/scraper.py#L231-L387)
- [src/pico_doc_scraper/utils.py](file://src/pico_doc_scraper/utils.py#L17-L175)

## Detailed Component Analysis

### HTTP Request Handling with Retry Logic
The fetch_page() function encapsulates HTTP fetching with:
- Configurable timeout and user-agent header
- Built-in retry loop with exponential backoff-like delay
- Graceful propagation of HTTP errors

```mermaid
flowchart TD
Start(["Call fetch_page(url)"]) --> Headers["Set headers (User-Agent)"]
Headers --> Loop["For attempt in range(MAX_RETRIES)"]
Loop --> TryReq["Send GET request<br/>follow redirects"]
TryReq --> Ok{"Status OK?"}
Ok --> |Yes| Return["Return HTML text"]
Ok --> |No| CheckLast{"Is last attempt?"}
CheckLast --> |No| Wait["Sleep(RETRY_DELAY)"] --> Loop
CheckLast --> |Yes| Raise["Raise HTTPError"]
Return --> End(["Done"])
Raise --> End
```

**Diagram sources**
- [src/pico_doc_scraper/scraper.py](file://src/pico_doc_scraper/scraper.py#L24-L52)
- [src/pico_doc_scraper/settings.py](file://src/pico_doc_scraper/settings.py#L19-L29)

**Section sources**
- [src/pico_doc_scraper/scraper.py](file://src/pico_doc_scraper/scraper.py#L24-L52)
- [src/pico_doc_scraper/settings.py](file://src/pico_doc_scraper/settings.py#L19-L29)

### URL Discovery and Domain Restriction
The discover_doc_links() function:
- Parses HTML with BeautifulSoup
- Resolves relative links to absolute URLs
- Filters by allowed domain and path prefix
- Excludes binary assets and fragments
- Normalizes URLs to a canonical form

```mermaid
flowchart TD
Start(["HTML + base_url"]) --> Parse["Parse with BeautifulSoup"]
Parse --> Iterate["Iterate <a> tags with href"]
Iterate --> Abs["Resolve absolute URL"]
Abs --> CheckDomain{"netloc == ALLOWED_DOMAIN?"}
CheckDomain --> |No| Skip["Skip"]
CheckDomain --> |Yes| CheckPath{"path starts with '/docs'?"}
CheckPath --> |No| Skip
CheckPath --> |Yes| CheckExt{"Not ending with .pdf/.zip/.tar.gz?"}
CheckExt --> |No| Skip
CheckExt --> |Yes| Canon["Build canonical URL (no fragment/query)"]
Canon --> Add["Add to set"]
Add --> Next["Next link"]
Skip --> Next
Next --> Done(["Return set of URLs"])
```

**Diagram sources**
- [src/pico_doc_scraper/scraper.py](file://src/pico_doc_scraper/scraper.py#L55-L85)
- [src/pico_doc_scraper/settings.py](file://src/pico_doc_scraper/settings.py#L5-L7)

**Section sources**
- [src/pico_doc_scraper/scraper.py](file://src/pico_doc_scraper/scraper.py#L55-L85)
- [src/pico_doc_scraper/settings.py](file://src/pico_doc_scraper/settings.py#L5-L7)

### Content Parsing and Markdown Conversion
The parse_documentation() function:
- Extracts the page title
- Attempts to locate the main content area using common selectors
- Removes navigation and non-content elements
- Converts remaining HTML to Markdown using markdownify

```mermaid
flowchart TD
Start(["HTML"]) --> Soup["BeautifulSoup parse"]
Soup --> Title["Find <h1> for title"]
Title --> Selectors["Try selectors for main content"]
Selectors --> Found{"Found?"}
Found --> |Yes| Use["Use matched element"]
Found --> |No| Fallback["Fallback to body or whole page"]
Use --> Clean["Remove nav/footer/header and common classes"]
Fallback --> Clean
Clean --> MD["Convert to Markdown"]
MD --> Build["Build result dict {title, content, raw_html}"]
Build --> Done(["Return parsed data"])
```

**Diagram sources**
- [src/pico_doc_scraper/scraper.py](file://src/pico_doc_scraper/scraper.py#L88-L142)

**Section sources**
- [src/pico_doc_scraper/scraper.py](file://src/pico_doc_scraper/scraper.py#L88-L142)

### Single-Page Processing Pipeline
The process_single_page() function orchestrates:
- Fetching HTML
- Parsing and converting to Markdown
- Determining filename from URL path
- Saving content to disk
- Discovering new links and returning them

```mermaid
sequenceDiagram
participant Caller as "scrape_docs()"
participant Proc as "process_single_page()"
participant Fetch as "fetch_page()"
participant Parse as "parse_documentation()"
participant Utils as "utils.save_content()"
participant Disc as "discover_doc_links()"
Caller->>Proc : "URL, visited_urls"
Proc->>Fetch : "Get HTML"
Fetch-->>Proc : "HTML"
Proc->>Parse : "Parse content"
Parse-->>Proc : "Parsed data"
Proc->>Utils : "Save content to file"
Proc->>Disc : "Discover links"
Disc-->>Proc : "New links"
Proc-->>Caller : "Success + new links"
```

**Diagram sources**
- [src/pico_doc_scraper/scraper.py](file://src/pico_doc_scraper/scraper.py#L145-L194)
- [src/pico_doc_scraper/utils.py](file://src/pico_doc_scraper/utils.py#L17-L48)
- [src/pico_doc_scraper/scraper.py](file://src/pico_doc_scraper/scraper.py#L55-L85)

**Section sources**
- [src/pico_doc_scraper/scraper.py](file://src/pico_doc_scraper/scraper.py#L145-L194)
- [src/pico_doc_scraper/utils.py](file://src/pico_doc_scraper/utils.py#L17-L48)

### State Management and Resume Capability
The load_or_initialize_state() function manages three modes:
- Fresh start: initializes with the base URL
- Resume: loads previously discovered and processed sets
- Retry: loads only failed URLs for targeted reprocessing

It also handles force-fresh mode to clear existing state files.

```mermaid
flowchart TD
Start(["load_or_initialize_state(force_fresh, retry_mode)"]) --> Fresh{"force_fresh?"}
Fresh --> |Yes| Clear["clear_state_files()"]
Fresh --> |No| Load["Load discovered/processed/failed sets"]
Clear --> Load
Load --> Retry{"retry_mode?"}
Retry --> |Yes| CheckFail{"Any failed URLs?"}
CheckFail --> |No| ReturnEmpty["Return empty sets"]
CheckFail --> |Yes| ReturnRetry["Return discovered, processed, failed set"]
Retry --> |No| HasDiscovered{"Has discovered URLs?"}
HasDiscovered --> |No| FreshInit["Initialize with base URL"]
HasDiscovered --> |Yes| Resume["Compute remaining URLs (discovered - processed)"]
Resume --> ReturnResume["Return discovered, processed, remaining"]
FreshInit --> ReturnFresh["Return initial sets"]
```

**Diagram sources**
- [src/pico_doc_scraper/scraper.py](file://src/pico_doc_scraper/scraper.py#L231-L285)
- [src/pico_doc_scraper/utils.py](file://src/pico_doc_scraper/utils.py#L161-L175)

**Section sources**
- [src/pico_doc_scraper/scraper.py](file://src/pico_doc_scraper/scraper.py#L231-L285)
- [src/pico_doc_scraper/utils.py](file://src/pico_doc_scraper/utils.py#L161-L175)

### Main Scraping Workflow
The scrape_docs() function coordinates the entire process:
- Loads or initializes state
- Ensures output directories exist
- Iteratively processes URLs with politeness delays
- Saves discovered and processed sets incrementally
- Aggregates errors and prints a summary

```mermaid
flowchart TD
Start(["scrape_docs(retry_mode, force_fresh)"]) --> Init["load_or_initialize_state()"]
Init --> Check{"initial_urls empty?"}
Check --> |Yes| Exit["Return"]
Check --> |No| Ensure["ensure_output_dir()"]
Ensure --> Loop{"while urls_to_visit"}
Loop --> Pop["Pop next URL"]
Pop --> Visited{"Already visited?"}
Visited --> |Yes| Loop
Visited --> |No| Delay{"First request?"}
Delay --> |No| Sleep["time.sleep(DELAY_BETWEEN_REQUESTS)"]
Delay --> |Yes| Process["process_single_page(url)"]
Sleep --> Process
Process --> Success{"Success?"}
Success --> |Yes| NewLinks{"retry_mode?"}
NewLinks --> |No| Add["Add new links to discovered/queue"]
NewLinks --> |Yes| Skip["Skip link discovery"]
Add --> SaveVisited["Save processed set"]
Skip --> SaveVisited
Success --> |No| RecordErr["Record error + failed URL"]
RecordErr --> SaveVisited
SaveVisited --> Loop
Loop --> |Empty| Summary["print_summary()"]
Summary --> End(["Done"])
```

**Diagram sources**
- [src/pico_doc_scraper/scraper.py](file://src/pico_doc_scraper/scraper.py#L287-L359)
- [src/pico_doc_scraper/settings.py](file://src/pico_doc_scraper/settings.py#L27-L29)

**Section sources**
- [src/pico_doc_scraper/scraper.py](file://src/pico_doc_scraper/scraper.py#L287-L359)
- [src/pico_doc_scraper/settings.py](file://src/pico_doc_scraper/settings.py#L27-L29)

### Politeness Measures and Rate Limiting
- Configurable delay between requests to avoid overloading the server
- Retry logic with bounded attempts and fixed delay for transient failures
- Domain and path filtering to constrain scope and reduce unnecessary traffic
- Incremental state persistence to minimize repeated work

Practical configuration keys:
- DELAY_BETWEEN_REQUESTS: seconds between requests
- MAX_RETRIES and RETRY_DELAY: retry policy for HTTP failures
- REQUEST_TIMEOUT: request timeout for responsiveness

**Section sources**
- [src/pico_doc_scraper/settings.py](file://src/pico_doc_scraper/settings.py#L19-L32)
- [src/pico_doc_scraper/scraper.py](file://src/pico_doc_scraper/scraper.py#L322-L324)
- [src/pico_doc_scraper/scraper.py](file://src/pico_doc_scraper/scraper.py#L38-L49)

### Practical Examples of the Scraping Workflow
- Basic scraping: run the module or use the Makefile target to start a scrape
- Retry failed URLs: use the retry flag or Makefile target to re-process only failed entries
- Fresh start: clear all state and restart from the base URL

Command-line usage:
- Start or resume: python -m pico_doc_scraper
- Retry only failed: python -m pico_doc_scraper --retry
- Fresh start: python -m pico_doc_scraper --force-fresh

Makefile targets:
- make scrape
- make scrape-retry
- make scrape-fresh

Output:
- Markdown files saved under scraped/
- State files under data/ for discovered, processed, and failed URLs

**Section sources**
- [README.md](file://README.md#L23-L64)
- [Makefile](file://Makefile#L115-L125)
- [src/pico_doc_scraper/__main__.py](file://src/pico_doc_scraper/__main__.py#L1-L7)

### Error Handling Mechanisms
- HTTP errors are caught and retried according to policy
- Exceptions during processing are logged and recorded as failed URLs
- Summary prints counts and details, and persists failed URLs for later retry
- KeyboardInterrupt is handled gracefully to allow clean termination

**Section sources**
- [src/pico_doc_scraper/scraper.py](file://src/pico_doc_scraper/scraper.py#L187-L194)
- [src/pico_doc_scraper/scraper.py](file://src/pico_doc_scraper/scraper.py#L350-L358)
- [src/pico_doc_scraper/scraper.py](file://src/pico_doc_scraper/scraper.py#L196-L229)

### Performance Optimization Techniques
- Incremental state persistence reduces recomputation on restart
- Politeness delays prevent server-side throttling and improve reliability
- Efficient URL deduplication using sets minimizes redundant work
- Selective link discovery avoids downloading non-documentation assets

**Section sources**
- [src/pico_doc_scraper/scraper.py](file://src/pico_doc_scraper/scraper.py#L335-L348)
- [src/pico_doc_scraper/scraper.py](file://src/pico_doc_scraper/scraper.py#L322-L324)
- [src/pico_doc_scraper/scraper.py](file://src/pico_doc_scraper/scraper.py#L65-L85)

## Dependency Analysis
External library integrations:
- httpx: HTTP client with timeouts and redirect handling
- beautifulsoup4: HTML parsing and DOM manipulation
- markdownify: HTML-to-Markdown conversion
- click: CLI argument parsing and help text

Internal dependencies:
- scraper.py depends on settings.py for configuration and utils.py for file I/O and state persistence
- __main__.py delegates to scraper.main()

```mermaid
graph LR
SCRAPER["scraper.py"] --> SETTINGS["settings.py"]
SCRAPER --> UTILS["utils.py"]
MAIN["__main__.py"] --> SCRAPER
INIT["__init__.py"] -.-> SCRAPER
```

**Diagram sources**
- [src/pico_doc_scraper/scraper.py](file://src/pico_doc_scraper/scraper.py#L1-L22)
- [src/pico_doc_scraper/__main__.py](file://src/pico_doc_scraper/__main__.py#L1-L7)
- [src/pico_doc_scraper/__init__.py](file://src/pico_doc_scraper/__init__.py#L1-L4)

**Section sources**
- [pyproject.toml](file://pyproject.toml#L9-L14)
- [src/pico_doc_scraper/scraper.py](file://src/pico_doc_scraper/scraper.py#L1-L22)

## Performance Considerations
- Adjust DELAY_BETWEEN_REQUESTS to balance speed and politeness
- Tune MAX_RETRIES and RETRY_DELAY for your network conditions
- Monitor output directory creation and incremental saves to avoid I/O bottlenecks
- Keep the URL sets small by relying on domain and path filters

[No sources needed since this section provides general guidance]

## Troubleshooting Guide
Common issues and resolutions:
- No URLs to process: verify that discovered_urls.txt contains entries or start fresh
- Failed URLs persist: use retry mode to re-run only failed entries
- Interrupted mid-run: resume automatically; state is saved incrementally
- Permission errors on data/scraped directories: ensure write permissions and correct paths

Operational tips:
- Use --force-fresh to clear stale state
- Review summary output for counts and failed URLs
- Inspect data/ files for debugging state

**Section sources**
- [src/pico_doc_scraper/scraper.py](file://src/pico_doc_scraper/scraper.py#L254-L262)
- [src/pico_doc_scraper/scraper.py](file://src/pico_doc_scraper/scraper.py#L350-L358)
- [README.md](file://README.md#L67-L76)

## Conclusion
The Pico CSS Documentation Scraper’s engine is a robust, stateful, and polite web crawler. Its design emphasizes resilience through retry logic, domain/path filtering, and incremental state persistence. The main workflow integrates fetching, parsing, saving, and link discovery into a cohesive pipeline, while CLI and Makefile targets provide flexible operational modes. By tuning configuration parameters and leveraging the built-in retry and resume capabilities, users can reliably convert the documentation site into Markdown with minimal manual intervention.

[No sources needed since this section summarizes without analyzing specific files]

## Appendices

### Configuration Reference
Key settings and their roles:
- PICO_DOCS_BASE_URL: Starting URL for scraping
- ALLOWED_DOMAIN: Domain restriction for safety
- REQUEST_TIMEOUT: Request timeout for responsiveness
- MAX_RETRIES and RETRY_DELAY: Retry policy for transient failures
- USER_AGENT: Header identifying the scraper
- DELAY_BETWEEN_REQUESTS: Politeness delay between requests
- OUTPUT_DIR and DATA_DIR: Output and state directories

**Section sources**
- [src/pico_doc_scraper/settings.py](file://src/pico_doc_scraper/settings.py#L5-L32)

### State Persistence Details
State files managed under data/:
- discovered_urls.txt: All URLs discovered during crawling
- processed_urls.txt: URLs successfully processed
- failed_urls.txt: URLs that failed to scrape

Persistence strategy:
- Incremental writes after each URL to enable safe interruption and resume
- Clearing of failed file when no failures occur

**Section sources**
- [README.md](file://README.md#L67-L76)
- [src/pico_doc_scraper/utils.py](file://src/pico_doc_scraper/utils.py#L130-L158)
- [src/pico_doc_scraper/utils.py](file://src/pico_doc_scraper/utils.py#L92-L128)