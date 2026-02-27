# JavaScript-Aware Browser Scraping

<cite>
**Referenced Files in This Document**
- [README.md](file://README.md)
- [pyproject.toml](file://pyproject.toml)
- [Makefile](file://Makefile)
- [.env](file://.env)
- [.envrc](file://.envrc)
- [src/pico_doc_scraper/__init__.py](file://src/pico_doc_scraper/__init__.py)
- [src/pico_doc_scraper/__main__.py](file://src/pico_doc_scraper/__main__.py)
- [src/pico_doc_scraper/settings.py](file://src/pico_doc_scraper/settings.py)
- [src/pico_doc_scraper/utils.py](file://src/pico_doc_scraper/utils.py)
- [src/pico_doc_scraper/scraper.py](file://src/pico_doc_scraper/scraper.py)
- [src/pico_doc_scraper/browser_scraper.py](file://src/pico_doc_scraper/browser_scraper.py)
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

## Introduction
This project is a resilient web scraper specifically designed for the Pico.css documentation website. It provides two distinct scraping modes: a traditional HTTP-based scraper for static content and a JavaScript-aware browser scraper powered by Playwright for dynamic, JavaScript-rendered content. The scraper automatically handles state persistence, retry mechanisms, and graceful error handling while converting HTML content to well-formatted Markdown.

The project emphasizes modularity and resilience, featuring automatic resume capabilities, domain restriction, and configurable politeness settings to respect server resources. Its architecture demonstrates clean separation of concerns, allowing for easy extension and maintenance.

## Project Structure
The project follows a well-organized structure that separates concerns across different modules:

```mermaid
graph TB
subgraph "Source Code (src/pico_doc_scraper/)"
A[__init__.py] --> B[__main__.py]
B --> C[scraper.py]
B --> D[browser_scraper.py]
E[settings.py] --> C
E --> D
F[utils.py] --> C
F --> D
end
subgraph "Configuration"
G[pyproject.toml]
H[Makefile]
I[.env]
J[.envrc]
end
subgraph "Runtime Data"
K[data/ directory]
L[scraped/ directory]
end
subgraph "External Dependencies"
M[httpx]
N[beautifulsoup4]
O[markdownify]
P[click]
Q[playwright]
end
G --> M
G --> N
G --> O
G --> P
G --> Q
C --> M
C --> N
C --> O
C --> P
D --> N
D --> O
D --> P
D --> Q
```

**Diagram sources**
- [src/pico_doc_scraper/__main__.py](file://src/pico_doc_scraper/__main__.py#L1-L7)
- [src/pico_doc_scraper/scraper.py](file://src/pico_doc_scraper/scraper.py#L1-L512)
- [src/pico_doc_scraper/browser_scraper.py](file://src/pico_doc_scraper/browser_scraper.py#L1-L254)
- [pyproject.toml](file://pyproject.toml#L1-L78)

**Section sources**
- [src/pico_doc_scraper/__init__.py](file://src/pico_doc_scraper/__init__.py#L1-L4)
- [src/pico_doc_scraper/__main__.py](file://src/pico_doc_scraper/__main__.py#L1-L7)
- [pyproject.toml](file://pyproject.toml#L1-L78)

## Core Components
The scraper consists of several interconnected components that work together to provide robust web scraping capabilities:

### Configuration Management
The settings module centralizes all configuration parameters, including base URLs, domain restrictions, timeouts, and output formatting preferences. This design enables easy customization without modifying core logic.

### State Management
The utility module provides comprehensive state persistence functionality, managing three critical state files:
- `discovered_urls.txt`: Tracks all URLs found during crawling
- `processed_urls.txt`: Records successfully processed URLs  
- `failed_urls.txt`: Maintains URLs that failed during scraping attempts

### Content Processing Pipeline
The core scraping logic implements a sophisticated content processing pipeline that handles HTML-to-Markdown conversion while preserving code examples through a three-phase extraction and restoration process.

### Browser Integration
The JavaScript-aware scraper integrates Playwright for headless browser automation, enabling dynamic content rendering and interactive element manipulation before content extraction.

**Section sources**
- [src/pico_doc_scraper/settings.py](file://src/pico_doc_scraper/settings.py#L1-L33)
- [src/pico_doc_scraper/utils.py](file://src/pico_doc_scraper/utils.py#L1-L175)
- [src/pico_doc_scraper/scraper.py](file://src/pico_doc_scraper/scraper.py#L1-L512)
- [src/pico_doc_scraper/browser_scraper.py](file://src/pico_doc_scraper/browser_scraper.py#L1-L254)

## Architecture Overview
The project employs a modular, pluggable architecture that separates scraping concerns into distinct layers:

```mermaid
graph TB
subgraph "Entry Points"
EP1[Command Line Interface]
EP2[Module Execution]
end
subgraph "Core Architecture"
CA1[Fetch Layer]
CA2[Parsing Layer]
CA3[State Management]
CA4[Output Layer]
end
subgraph "Static Scraper"
SS1[HTTPX Client]
SS2[BeautifulSoup Parser]
SS3[Markdown Converter]
end
subgraph "Browser Scraper"
BS1[Playwright Engine]
BS2[Page Automation]
BS3[Dynamic Rendering]
end
subgraph "Shared Components"
SC1[Configuration Settings]
SC2[Utility Functions]
SC3[State Persistence]
end
EP1 --> CA1
EP2 --> CA1
CA1 --> CA2
CA2 --> CA3
CA3 --> CA4
CA1 --> SS1
CA1 --> BS1
CA2 --> SS2
CA2 --> BS2
CA4 --> SS3
CA4 --> BS3
SS1 --> SC1
BS1 --> SC1
SS2 --> SC2
BS2 --> SC2
SS3 --> SC3
BS3 --> SC3
```

**Diagram sources**
- [src/pico_doc_scraper/scraper.py](file://src/pico_doc_scraper/scraper.py#L1-L512)
- [src/pico_doc_scraper/browser_scraper.py](file://src/pico_doc_scraper/browser_scraper.py#L1-L254)
- [src/pico_doc_scraper/settings.py](file://src/pico_doc_scraper/settings.py#L1-L33)
- [src/pico_doc_scraper/utils.py](file://src/pico_doc_scraper/utils.py#L1-L175)

The architecture demonstrates several key design principles:
- **Separation of Concerns**: Each component has a specific responsibility
- **Pluggable Fetchers**: The same parsing logic works with different fetch methods
- **State Persistence**: All progress is saved incrementally for resilience
- **Clean Abstraction**: Browser-specific code is isolated from core logic

## Detailed Component Analysis

### Static Scraper Implementation
The static scraper provides reliable content extraction for traditional web pages using HTTPX for requests, BeautifulSoup for HTML parsing, and markdownify for content conversion.

```mermaid
sequenceDiagram
participant User as User
participant CLI as CLI Interface
participant Scraper as Static Scraper
participant HTTPX as HTTPX Client
participant Parser as BeautifulSoup Parser
participant MD as Markdown Converter
participant FS as File System
User->>CLI : Start scraping
CLI->>Scraper : Initialize scraper
Scraper->>Scraper : Load state files
Scraper->>Scraper : Setup output directories
loop For each URL
Scraper->>HTTPX : fetch_page(url)
HTTPX-->>Scraper : HTML content
Scraper->>Parser : parse_documentation(html)
Parser->>Parser : Extract main content
Parser->>Parser : Remove navigation/footer
Parser->>Parser : Extract code blocks
Parser->>MD : Convert to markdown
MD-->>Parser : Markdown content
Parser->>Parser : Restore code blocks
Parser-->>Scraper : Parsed content
Scraper->>FS : Save content to file
Scraper->>Scraper : Update state files
end
Scraper-->>CLI : Print summary
CLI-->>User : Scraping complete
```

**Diagram sources**
- [src/pico_doc_scraper/scraper.py](file://src/pico_doc_scraper/scraper.py#L25-L512)
- [src/pico_doc_scraper/utils.py](file://src/pico_doc_scraper/utils.py#L17-L175)

The static scraper implements several sophisticated features:

#### Code Block Preservation Mechanism
The scraper employs a three-phase process to preserve code examples during HTML-to-Markdown conversion:

```mermaid
flowchart TD
Start([HTML Content]) --> Extract["Extract Code Blocks<br/>Find <pre><code> tags"]
Extract --> Replace["Replace with Placeholders<br/>Store original code"]
Replace --> Convert["Convert to Markdown<br/>Using markdownify"]
Convert --> Restore["Restore Code Blocks<br/>Replace placeholders"]
Restore --> Output([Final Markdown])
Extract --> Language["Extract Language<br/>From code class names"]
Language --> Replace
```

**Diagram sources**
- [src/pico_doc_scraper/scraper.py](file://src/pico_doc_scraper/scraper.py#L89-L146)

#### Link Discovery and Filtering
The scraper implements intelligent link discovery with strict filtering criteria:
- Domain restriction to prevent crawling external sites
- Path filtering to focus on documentation content
- Extension filtering to avoid downloading files
- Fragment and query string normalization

**Section sources**
- [src/pico_doc_scraper/scraper.py](file://src/pico_doc_scraper/scraper.py#L25-L512)

### Browser Scraper Implementation
The browser scraper extends the core functionality by adding JavaScript rendering capabilities through Playwright integration.

```mermaid
classDiagram
class BrowserScraper {
+load_or_initialize_state()
+scrape_docs_browser()
+scrape_single_target_browser()
-_make_browser_fetcher(page)
-_reveal_code_examples(page)
-_click_code_buttons(page)
-_click_code_links(page)
}
class PlaywrightPage {
+set_default_timeout()
+set_extra_http_headers()
+goto()
+content()
+get_by_role()
+get_by_text()
+click()
+wait_for_timeout()
}
class FetchFunction {
<<interface>>
+__call__(url) str
}
BrowserScraper --> PlaywrightPage : "uses"
BrowserScraper --> FetchFunction : "creates"
FetchFunction <|.. BrowserFetchFunction : "implementation"
```

**Diagram sources**
- [src/pico_doc_scraper/browser_scraper.py](file://src/pico_doc_scraper/browser_scraper.py#L23-L254)

#### Dynamic Content Interaction
The browser scraper implements sophisticated interaction with JavaScript-rendered content:

```mermaid
sequenceDiagram
participant Scraper as Browser Scraper
participant Browser as Playwright Browser
participant Page as Web Page
participant DOM as DOM Elements
Scraper->>Browser : Launch chromium browser
Scraper->>Page : Create new page with user agent
Scraper->>Scraper : Create fetch function
Scraper->>Page : goto(url, wait_until="networkidle")
Page-->>Scraper : Rendered HTML
Scraper->>DOM : Find "Code" buttons
DOM-->>Scraper : Button elements
Scraper->>DOM : Click buttons
DOM-->>Scraper : Code examples revealed
Scraper->>DOM : Find "Code" links
DOM-->>Scraper : Link elements
Scraper->>DOM : Click links
DOM-->>Scraper : Code examples revealed
Scraper->>Page : page.content()
Page-->>Scraper : Final HTML with code
```

**Diagram sources**
- [src/pico_doc_scraper/browser_scraper.py](file://src/pico_doc_scraper/browser_scraper.py#L23-L96)

**Section sources**
- [src/pico_doc_scraper/browser_scraper.py](file://src/pico_doc_scraper/browser_scraper.py#L1-L254)

### State Management System
The state management system provides comprehensive progress tracking and recovery capabilities:

```mermaid
flowchart TD
Start([Scraping Session]) --> LoadState["Load Existing State"]
LoadState --> CheckMode{"Mode"}
CheckMode --> |Resume| ResumeMode["Resume from Previous State"]
CheckMode --> |Retry| RetryMode["Retry Failed URLs Only"]
CheckMode --> |Fresh| FreshMode["Start Fresh Scrape"]
ResumeMode --> CheckProgress{"Any URLs to Process?"}
RetryMode --> LoadFailed["Load Failed URLs"]
FreshMode --> InitState["Initialize Empty State"]
CheckProgress --> |Yes| ProcessLoop["Process URLs"]
CheckProgress --> |No| Complete["Complete Session"]
LoadFailed --> ProcessLoop
InitState --> ProcessLoop
ProcessLoop --> UpdateState["Update State Files"]
UpdateState --> CheckMore{"More URLs?"}
CheckMore --> |Yes| ProcessLoop
CheckMore --> |No| Complete
Complete --> SaveSummary["Save Final Summary"]
SaveSummary --> End([Session Complete])
```

**Diagram sources**
- [src/pico_doc_scraper/scraper.py](file://src/pico_doc_scraper/scraper.py#L314-L442)
- [src/pico_doc_scraper/utils.py](file://src/pico_doc_scraper/utils.py#L92-L175)

**Section sources**
- [src/pico_doc_scraper/scraper.py](file://src/pico_doc_scraper/scraper.py#L314-L442)
- [src/pico_doc_scraper/utils.py](file://src/pico_doc_scraper/utils.py#L92-L175)

## Dependency Analysis
The project maintains a clean dependency structure with clear separation between core functionality and optional browser support:

```mermaid
graph TB
subgraph "Core Dependencies"
CD1[httpx >= 0.27.0]
CD2[beautifulsoup4 >= 4.12.0]
CD3[markdownify >= 0.11.0]
CD4[click >= 8.1.0]
end
subgraph "Development Dependencies"
DD1[pytest >= 6.0]
DD2[pytest-mock >= 3.0]
DD3[responses >= 0.18]
DD4[ruff >= 0.9]
DD5[mypy >= 1.0]
DD6[build >= 0.10]
end
subgraph "Browser Dependencies"
BD1[playwright >= 1.49.0]
end
subgraph "Project Modules"
PM1[pico_doc_scraper]
PM2[scraper.py]
PM3[browser_scraper.py]
PM4[settings.py]
PM5[utils.py]
end
CD1 --> PM2
CD2 --> PM2
CD3 --> PM2
CD4 --> PM2
CD4 --> PM3
DD1 --> PM1
DD2 --> PM1
DD3 --> PM1
DD4 --> PM1
DD5 --> PM1
DD6 --> PM1
BD1 --> PM3
PM1 --> PM2
PM1 --> PM3
PM1 --> PM4
PM1 --> PM5
```

**Diagram sources**
- [pyproject.toml](file://pyproject.toml#L9-L27)
- [src/pico_doc_scraper/scraper.py](file://src/pico_doc_scraper/scraper.py#L1-L22)
- [src/pico_doc_scraper/browser_scraper.py](file://src/pico_doc_scraper/browser_scraper.py#L1-L21)

The dependency analysis reveals several important characteristics:

### Optional Browser Support
The browser functionality is implemented as an optional dependency, allowing users to install only the core scraping functionality if JavaScript rendering is not required. This design choice reduces installation overhead for basic use cases.

### Clean Module Separation
Each module has a specific responsibility:
- `scraper.py`: Core scraping logic and HTTP-based fetching
- `browser_scraper.py`: Browser-based scraping with Playwright integration
- `settings.py`: Centralized configuration management
- `utils.py`: Shared utility functions for state management and file operations

**Section sources**
- [pyproject.toml](file://pyproject.toml#L9-L27)
- [src/pico_doc_scraper/scraper.py](file://src/pico_doc_scraper/scraper.py#L1-L22)
- [src/pico_doc_scraper/browser_scraper.py](file://src/pico_doc_scraper/browser_scraper.py#L1-L21)

## Performance Considerations
The scraper implements several performance optimization strategies:

### Polite Request Handling
- Configurable delays between requests to avoid overwhelming servers
- Respectful user agent identification for transparency
- Graceful handling of rate limiting and server-side throttling

### Memory-Efficient Processing
- Incremental state saving prevents memory accumulation
- Set-based URL tracking minimizes memory footprint
- Stream-based file writing for large content volumes

### Intelligent Retry Logic
- Exponential backoff for failed requests
- Configurable retry limits to balance persistence and efficiency
- Selective retry for failed URLs only

### Browser Optimization
- Headless browser execution for reduced resource consumption
- Efficient page lifecycle management
- Timeout configuration for responsive scraping

## Troubleshooting Guide

### Common Issues and Solutions

#### Installation Problems
**Issue**: Missing Playwright dependencies
**Solution**: Install browser dependencies using the provided commands
- Install Playwright: `uv run playwright install`
- Install system dependencies: `uv run playwright install-deps`

**Issue**: Virtual environment activation problems
**Solution**: Use the provided environment configuration
- Activate environment: `source .venv/bin/activate`
- Load environment variables: `dotenv`

#### Scraping Failures
**Issue**: HTTP timeouts or connection errors
**Solution**: Adjust timeout settings in configuration
- Increase REQUEST_TIMEOUT value
- Reduce MAX_RETRIES for faster failure detection
- Configure appropriate DELAY_BETWEEN_REQUESTS

**Issue**: JavaScript content not rendering properly
**Solution**: Verify browser installation and configuration
- Ensure Playwright browsers are installed
- Check network connectivity for browser downloads
- Verify user agent settings match target site requirements

#### State Management Issues
**Issue**: State files not updating correctly
**Solution**: Manual state file management
- Clear state files: `utils.clear_state_files()`
- Verify file permissions for data directory
- Check disk space availability

**Section sources**
- [src/pico_doc_scraper/utils.py](file://src/pico_doc_scraper/utils.py#L161-L175)
- [src/pico_doc_scraper/settings.py](file://src/pico_doc_scraper/settings.py#L19-L32)

### Debugging Strategies
The scraper provides comprehensive logging and error reporting:

1. **Verbose Logging**: Each major operation prints status updates
2. **Error Details**: Specific error messages for failed URLs
3. **State Inspection**: Progress tracking through state files
4. **Manual Verification**: Single URL testing mode for isolated debugging

## Conclusion
The JavaScript-Aware Browser Scraping project demonstrates excellent software engineering practices through its modular architecture, comprehensive error handling, and thoughtful design decisions. The dual-mode approach allows users to choose between lightweight static scraping and powerful JavaScript-aware scraping based on their specific needs.

Key strengths of the implementation include:
- **Resilient Architecture**: Automatic state persistence and incremental progress saving
- **Flexible Design**: Pluggable fetcher system enabling easy extension
- **Robust Error Handling**: Comprehensive retry mechanisms and graceful degradation
- **Clean Separation**: Well-defined boundaries between concerns
- **Developer Experience**: Comprehensive CLI interface and development tools

The project serves as an excellent foundation for web scraping applications, particularly for documentation sites with dynamic content. Its modular design makes it straightforward to adapt for other websites or extend with additional scraping strategies.