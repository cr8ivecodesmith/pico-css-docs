# Installation and Setup

<cite>
**Referenced Files in This Document**
- [README.md](file://README.md)
- [pyproject.toml](file://pyproject.toml)
- [Makefile](file://Makefile)
- [src/pico_doc_scraper/__init__.py](file://src/pico_doc_scraper/__init__.py)
- [src/pico_doc_scraper/settings.py](file://src/pico_doc_scraper/settings.py)
- [src/pico_doc_scraper/scraper.py](file://src/pico_doc_scraper/scraper.py)
- [src/pico_doc_scraper/utils.py](file://src/pico_doc_scraper/utils.py)
- [.env](file://.env)
- [.envrc](file://.envrc)
- [uv.lock](file://uv.lock)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Installation Process](#installation-process)
4. [Virtual Environment Setup](#virtual-environment-setup)
5. [Dependency Management](#dependency-management)
6. [Project Structure](#project-structure)
7. [Configuration](#configuration)
8. [Verification Steps](#verification-steps)
9. [Development Workflow](#development-workflow)
10. [Troubleshooting](#troubleshooting)
11. [Best Practices](#best-practices)

## Introduction

The Pico CSS Documentation Scraper is a resilient web scraper designed to convert Pico.css documentation pages from HTML to well-formatted Markdown. This tool provides automatic resume capabilities, state tracking, retry functionality, and domain restriction to ensure reliable and efficient scraping of documentation content.

## Prerequisites

### Python Version Requirements

The project requires **Python 3.12 or higher**. This specific version requirement is enforced at the project level and affects dependency compatibility:

- **Project Requirement**: Python >= 3.12 (enforced in pyproject.toml)
- **Development Tools**: Python 3.12+ for consistent development experience
- **Dependency Compatibility**: Many development dependencies require Python 3.12+ for optimal performance

The Python 3.12 requirement ensures compatibility with modern development tools and libraries, particularly the type checking and linting tools used in this project.

**Section sources**
- [pyproject.toml](file://pyproject.toml#L7-L7)
- [uv.lock](file://uv.lock#L3-L3)

## Installation Process

### Quick Setup

The fastest way to set up the project is using the provided Makefile target:

```bash
make setup
```

This command performs two essential tasks:
1. Creates a virtual environment named `.venv`
2. Installs all development dependencies with editable installation

### Alternative Installation Methods

If you prefer manual installation, you can use pip directly:

```bash
# Install in development mode with all dependencies
pip install -e ".[dev]"

# Or install only runtime dependencies
pip install -e .
```

### Development Dependencies

The project uses a comprehensive set of development dependencies managed through the `[dev]` extra:

- **Testing**: pytest, pytest-mock, responses
- **Linting**: ruff (Python linter)
- **Type Checking**: mypy (static type analysis)
- **Packaging**: build (wheel distribution creation)

**Section sources**
- [Makefile](file://Makefile#L56-L59)
- [pyproject.toml](file://pyproject.toml#L16-L24)

## Virtual Environment Setup

### Using Makefile (Recommended)

The project provides a streamlined approach to virtual environment management:

```bash
# Create virtual environment and install dependencies
make setup

# Activate the virtual environment
source .venv/bin/activate  # On Unix/MacOS
# or
.venv\Scripts\activate     # On Windows
```

### Manual Virtual Environment Creation

If you prefer manual setup:

```bash
# Create virtual environment
python3.12 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On Unix/MacOS
# or
.venv\Scripts\activate     # On Windows

# Install dependencies
pip install -e ".[dev]"
```

### Environment Configuration

The project includes environment configuration files:

- **.env**: Sets VIRTUAL_ENV=.venv and UV_PYTHON=python3.12
- **.envrc**: Uses direnv to automatically activate the virtual environment

These configurations ensure consistent development environments across team members.

**Section sources**
- [.env](file://.env#L1-L3)
- [.envrc](file://.envrc#L1-L2)

## Dependency Management

### Runtime Dependencies

The scraper requires four core packages:

| Package | Version | Purpose |
|---------|---------|---------|
| httpx | >=0.27.0 | Modern HTTP client with retry logic |
| beautifulsoup4 | >=4.12.0 | HTML parsing and manipulation |
| markdownify | >=0.11.0 | HTML to Markdown conversion |
| click | >=8.1.0 | Command-line interface framework |

### Development Dependencies

Additional development tools enhance the development experience:

| Tool | Purpose | Version |
|------|---------|---------|
| pytest | Testing framework | >=6.0 |
| ruff | Fast Python linter | >=0.9 |
| mypy | Static type checker | >=1.0 |
| build | Wheel packaging | >=0.10 |

### Dependency Resolution

The project uses uv for dependency resolution and installation, ensuring consistent dependency trees across different platforms and Python versions.

**Section sources**
- [pyproject.toml](file://pyproject.toml#L9-L14)
- [pyproject.toml](file://pyproject.toml#L16-L24)
- [uv.lock](file://uv.lock#L1-L546)

## Project Structure

The project follows a clear directory structure that separates concerns effectively:

```
pico-css-docs/
├── src/pico_doc_scraper/           # Main package
│   ├── __init__.py                # Package initialization
│   ├── __main__.py               # Module entry point
│   ├── scraper.py               # Core scraping logic
│   ├── settings.py              # Configuration constants
│   └── utils.py                 # Utility functions
├── data/                         # State tracking files
├── scraped/                      # Output Markdown files
├── pyproject.toml               # Project configuration
├── Makefile                     # Development commands
├── README.md                    # Documentation
└── uv.lock                     # Dependency lock file
```

### Directory Purposes

- **src/pico_doc_scraper/**: Contains all source code organized by functionality
- **data/**: Stores state tracking files (discovered_urls.txt, processed_urls.txt, failed_urls.txt)
- **scraped/**: Contains the final Markdown output files
- **pyproject.toml**: Defines project metadata, dependencies, and build configuration
- **Makefile**: Provides convenient development commands

**Section sources**
- [README.md](file://README.md#L119-L134)

## Configuration

### Settings Module

The settings module centralizes all configuration parameters:

```python
# Base URLs
PICO_DOCS_BASE_URL = "https://picocss.com/docs"
ALLOWED_DOMAIN = "picocss.com"

# Output directories
OUTPUT_DIR = Path(__file__).parent.parent.parent / "scraped"
DATA_DIR = Path(__file__).parent.parent.parent / "data"

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
```

### Configuration Impact

These settings control:
- **Domain Restriction**: Only scrapes pages from picocss.com
- **Output Format**: Generates Markdown files
- **Rate Limiting**: 1-second delay between requests
- **State Persistence**: Automatic resume capability

**Section sources**
- [src/pico_doc_scraper/settings.py](file://src/pico_doc_scraper/settings.py#L1-L33)

## Verification Steps

### Post-Installation Verification

After completing the installation, verify everything works correctly:

```bash
# Check Python version
python --version

# Verify virtual environment activation
which python

# Test the scraper module
python -m pico_doc_scraper --help

# Run basic tests
make test
```

### Expected Behavior

Successful installation should produce:
- Python 3.12+ interpreter
- Active virtual environment
- Accessible command-line interface
- Working test suite

### Common Verification Issues

- **Python version mismatch**: Ensure Python 3.12+ is installed
- **Virtual environment not activated**: Check that `.venv/bin/activate` is sourced
- **Dependencies missing**: Run `make setup` to reinstall dependencies

**Section sources**
- [README.md](file://README.md#L16-L21)
- [Makefile](file://Makefile#L56-L59)

## Development Workflow

### Available Make Commands

The Makefile provides comprehensive development commands:

```bash
# Development setup
make setup                    # Create venv and install dev dependencies
make install                  # Install runtime dependencies
make install-dev              # Install development dependencies

# Testing and quality assurance
make test                     # Run full test suite
make test-all                 # Run all tests
make test-unit                # Run unit tests only
make test-integration         # Run integration tests
make lint                     # Run ruff linter
make type-check               # Run mypy type checker

# Scraping operations
make scrape                   # Run scraper normally
make scrape-retry             # Retry failed URLs
make scrape-fresh             # Start fresh scrape

# Cleanup and maintenance
make package                  # Build wheel distribution
make package-install          # Install built wheel
make clean                    # Clean build artifacts
```

### Development Environment Best Practices

1. **Always work in the virtual environment**
2. **Run tests before committing changes**
3. **Use linting to maintain code quality**
4. **Keep dependencies updated regularly**

**Section sources**
- [Makefile](file://Makefile#L14-L126)

## Troubleshooting

### Common Installation Issues

#### Issue: Python version error
**Problem**: Installation fails due to incompatible Python version
**Solution**: Ensure Python 3.12+ is installed and available
```bash
python3.12 --version
# If not available, install Python 3.12 from python.org
```

#### Issue: Virtual environment creation fails
**Problem**: Cannot create .venv directory
**Solution**: Check permissions and available disk space
```bash
ls -la
mkdir .venv  # Test write permissions
```

#### Issue: Dependencies fail to install
**Problem**: pip install fails with dependency conflicts
**Solution**: Use the provided Makefile or uv for dependency resolution
```bash
make setup
# or
uv pip install -e ".[dev]"
```

#### Issue: Module not found error
**Problem**: Cannot import pico_doc_scraper
**Solution**: Ensure editable installation and proper PYTHONPATH
```bash
pip install -e .
python -c "import pico_doc_scraper"
```

### Development Environment Issues

#### Issue: Make commands not found
**Problem**: make command not recognized
**Solution**: Install GNU Make or use Python alternatives
```bash
# On Windows, use PowerShell or Command Prompt
python -m make setup  # Alternative approach
```

#### Issue: Linting or type checking errors
**Problem**: Ruff or mypy reports issues
**Solution**: Fix reported issues or temporarily disable checks
```bash
make lint  # Fix reported issues
make type-check  # Address type annotations
```

### Scraping-Specific Issues

#### Issue: Rate limiting or blocking
**Problem**: Website blocks scraping attempts
**Solution**: Adjust DELAY_BETWEEN_REQUESTS setting and respect robots.txt
```python
# In settings.py, increase delay
DELAY_BETWEEN_REQUESTS = 2.0  # seconds
```

#### Issue: State file corruption
**Problem**: Previous scrape state prevents new runs
**Solution**: Clear state files or use fresh start option
```bash
make scrape-fresh
# or manually delete files in data/ directory
```

**Section sources**
- [src/pico_doc_scraper/settings.py](file://src/pico_doc_scraper/settings.py#L28-L29)
- [src/pico_doc_scraper/utils.py](file://src/pico_doc_scraper/utils.py#L161-L175)

## Best Practices

### Environment Management

1. **Always use virtual environments** for project isolation
2. **Pin Python versions** to ensure consistency across team members
3. **Regularly update dependencies** while maintaining compatibility
4. **Use editable installs** during development for easy testing

### Development Workflow

1. **Run tests frequently** to catch issues early
2. **Use linting and type checking** to maintain code quality
3. **Write clear commit messages** describing changes
4. **Document configuration changes** in settings.py

### Scraping Ethics

1. **Respect robots.txt** and website terms of service
2. **Implement appropriate delays** between requests
3. **Handle errors gracefully** and log issues appropriately
4. **Clean up state files** when starting fresh

### Project Maintenance

1. **Keep README updated** with installation and usage instructions
2. **Regular dependency audits** to identify security vulnerabilities
3. **Version control best practices** for configuration files
4. **Documentation updates** for breaking changes

**Section sources**
- [README.md](file://README.md#L1-L134)
- [src/pico_doc_scraper/settings.py](file://src/pico_doc_scraper/settings.py#L24-L29)