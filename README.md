# GermanLegalTexts

A Python package for downloading, parsing, and working with German legal texts and court judgements from official German government sources.

## Description

GermanLegalTexts provides tools to programmatically access and work with German legal texts and court judgements. It allows you to:

- **Law Books (Gesetzbücher)**: Download and parse legal codes from [Gesetze im Internet](https://www.gesetze-im-internet.de/)
  - Download individual law books by abbreviation (e.g., "bgb" for Bürgerliches Gesetzbuch)
  - Download all available German legal texts
  - Access specific paragraphs, sections, and other elements
  
- **Court Judgements (Rechtsprechung)**: Download and parse court decisions from [Rechtsprechung im Internet](https://www.rechtsprechung-im-internet.de/)
  - Download individual judgements
  - Browse and filter judgement index
  - Download first n judgements or all available judgements
  - Access structured judgement data (facts, reasoning, decision)

The package handles the complexities of downloading, extracting, and parsing the XML files provided by the official German legal repositories.

## Installation

Requires Python 3.12 or higher.


## Usage

### Law Books (Gesetzbücher)

#### Downloading a Single Law Book

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

### Court Judgements (Rechtsprechung)

#### Downloading a Single Judgement

```python
from germanlegaltexts.GermanJudgementDownloader import GermanJudgementDownloader

# Create a downloader instance
downloader = GermanJudgementDownloader()

# Download a spechierarchical data models to represent German legal documents:

### Law Books (Gesetzbuch)

- `Gesetzbuch`: The top-level container for a law book
- `Norm`: Represents a legal norm/section
- `Metadaten`: Contains metadata about a norm
- `Textdaten`: Contains the actual text content
- Supporting classes for specific elements (Fundstelle, Standangabe, etc.)

### Court Judgements (Rechtsprechung)

- `Rechtsprechung`: The top-level container for a court judgement
- `RIIIndexItem`: Metadata from the judgement index
- Content clas: 
  - [Gesetze im Internet](https://www.gesetze-im-internet.de/) (Law books)
  - [Rechtsprechung im Internet](https://www.rechtsprechung-im-internet.de/) (Court judgements
  - `Titelzeile`: Title line
  - `Leitsatz`: Headnote/summary
  - `Tenor`: Operative part of the decision
  - `Tatbestand`: Facts of the case
  - `Gruende`: Legal reasoning
  - `Entscheidungsgruende`: Decision grounds
- `Region`: Regional jurisdiction information
print(f"Case number: {judgement.aktenzeichen}")
print(f"Decision type: {judgement.doktyp}")
```

#### Working with Judgement Content

```python
# Access structured content
if judgement.titelzeile:
    print(f"Title: {judgement.titelzeile.content}")

if judgement.tenor:
    print(f"Decision: {judgement.tenor.content}")

if judgement.gruende:
    print(f"Reasoning: {judgement.gruende.content}")

# Access metadata
print(f"Referenced norms: {judgement.norm}")
print(f"Court body: {judgement.spruchkoerper}")
```

#### Browsing Available Judgements

```python
# Get index of all judgements
index_items = downloader.get_all_judgement_index_items()
print(f"Total available judgements: {len(index_items)}")

# Browse index
for item in index_items[:5]:
    print(f"{item.aktenzeichen} - {item.gericht} - {item.entsch_datum}")

# Get total count
count = downloader.get_judgement_count()
print(f"Available judgements: {count}")
```

#### Downloading Multiple Judgements

```python
# Download first n judgements
judgements = downloader.download_first_n_judgements(10)
print(f"Downloaded {len(judgements)} judgements")

# WARNING: This downloads ALL judgements (may take very long)
all_judgements = downloader.download_all_judgements()
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
