# GermanLegalTexts

A Python package for downloading, parsing, and working with German legal texts from the official [Gesetze im Internet](https://www.gesetze-im-internet.de/) website.

## Description

GermanLegalTexts provides tools to programmatically access and work with German legal texts. It allows you to:

- Download individual German law books by their abbreviation (e.g., "bgb" for Bürgerliches Gesetzbuch)
- Download all available German legal texts
- Parse the XML content into structured Python objects
- Access specific paragraphs, sections, and other elements of legal texts
- Work with the content in a structured, object-oriented way

The package handles the complexities of downloading, extracting, and parsing the XML files provided by the official German legal text repository.

## Installation

Requires Python 3.12 or higher.

```bash
pip install germanlegaltexts
```

## Usage

### Downloading a Single Law Book

```python
from germanlegaltexts.GermanLegalTextDownloader import GermanLegalTextDownloader

# Create a downloader instance
downloader = GermanLegalTextDownloader()

# Download a specific law book by URL
url = "https://www.gesetze-im-internet.de/bgb/xml.zip"
bgb = downloader.download_law_book(url)

# Access metadata
print(f"Title: {bgb.norms[0].metadaten.titel}")
print(f"Abbreviation: {bgb.norms[0].metadaten.amtabk}")
```

### Working with Law Content

```python
# Get a specific paragraph
paragraph = bgb.get_paragraph("§ 1")
if paragraph:
    print(f"Title: {paragraph.metadaten.titel}")
    print(f"Content: {paragraph.textdaten.text.content.text}")

# Get all paragraphs
all_paragraphs = bgb.get_all_paragraphs()
print(f"Total paragraphs: {len(all_paragraphs)}")

# Get a specific section
section = bgb.get_section("1. Abschnitt")
for norm in section:
    print(f"Section norm: {norm.metadaten.enbez}")

# Get all sections
all_sections = bgb.get_all_sections()
print(f"Total sections: {len(all_sections)}")
```

### Downloading All Law Books

```python
# Get all available XML paths
all_xml_paths = downloader.get_all_xml_paths()
print(f"Total available law books: {len(all_xml_paths)}")

# Download all law books (this may take a long time)
all_law_books = downloader.download_all_law_books()
print(f"Successfully downloaded {len(all_law_books)} law books")
```

## Features

- **Efficient Downloading**: Downloads and extracts ZIP files containing XML data
- **Structured Data Model**: Parses XML into a hierarchical object model
- **Easy Access**: Methods to access specific paragraphs, sections, and other elements
- **Complete Coverage**: Can download all available German legal texts
- **Minimal Dependencies**: Only requires the `requests` library

## Data Structure

The package uses a hierarchical data model to represent German legal texts:

- `Gesetzbuch`: The top-level container for a law book
- `Norm`: Represents a legal norm/section
- `Metadaten`: Contains metadata about a norm
- `Textdaten`: Contains the actual text content
- Supporting classes for specific elements (Fundstelle, Standangabe, etc.)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Data source: [Gesetze im Internet](https://www.gesetze-im-internet.de/)
- Author: Malte Weber
