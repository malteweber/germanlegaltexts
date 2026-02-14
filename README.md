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

```bash
pip install germanlegaltexts
```

## Usage

### Law Books (Gesetzbücher)

```python
from germanlegaltexts.GermanLawDownloader import GermanLawDownloader

downloader = GermanLawDownloader()

url = "https://www.gesetze-im-internet.de/bgb/xml.zip"
bgb = downloader.download_law_book(url)

paragraph = bgb.get_paragraph("§ 1")
if paragraph:
    print(f"Content: {paragraph.textdaten.text.content.text}")
```

### Court Judgements (Rechtsprechung)

```python
from germanlegaltexts.GermanJudgementDownloader import GermanJudgementDownloader

downloader = GermanJudgementDownloader()

judgements = downloader.download_first_n_judgements(10)
for judgement in judgements:
    print(f"Case: {judgement.aktenzeichen} - Type: {judgement.doktyp}")
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Data source: [Gesetze im Internet](https://www.gesetze-im-internet.de/)
- Author: Malte Weber
