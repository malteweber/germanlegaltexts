# GermanLegalTexts

A Python package for downloading, parsing, and working with German legal texts and court judgements from official German government sources.

## Description

GermanLegalTexts provides tools to programmatically access and work with German legal texts and court judgements. It allows you to:

- **Law Books (Gesetzbücher)**: Download and parse legal codes from [Gesetze im Internet](https://www.gesetze-im-internet.de/)
  - Download individual law books by URL
  - Download all available German legal texts (sync or async)
  - Access specific paragraphs, sections, and other elements

- **Court Judgements (Rechtsprechung)**: Download and parse court decisions from [Rechtsprechung im Internet](https://www.rechtsprechung-im-internet.de/)
  - Download individual judgements
  - Browse and filter the judgement index
  - Download the first n judgements or all available judgements (sync or async)
  - Access structured judgement data (facts, reasoning, decision)

Both downloaders support an **async API** built on `httpx` that streams results as they complete, with configurable rate limiting.

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

# Download a single law book
bgb = downloader.download_law_book("https://www.gesetze-im-internet.de/bgb/xml.zip")

paragraph = bgb.get_paragraph("§ 242")
if paragraph:
    print(paragraph.metadaten.titel)
    print(paragraph.textdaten.text.content.text)
```

### Court Judgements (Rechtsprechung)

```python
from germanlegaltexts.GermanJudgementDownloader import GermanJudgementDownloader

downloader = GermanJudgementDownloader()

# Download the first 10 judgements
for judgement in downloader.download_first_n_judgements(10):
    print(f"{judgement.aktenzeichen} — {judgement.doktyp}")
```

### Async batch downloads

Both downloaders expose async generator methods that start downloads in parallel and yield results as they arrive, with a configurable rate limit (default: 1 new request per second).

```python
import asyncio
from germanlegaltexts.GermanLawDownloader import GermanLawDownloader
from germanlegaltexts.GermanJudgementDownloader import GermanJudgementDownloader

async def main():
    # Stream all law books — start 2 new downloads per second
    law_downloader = GermanLawDownloader()
    async for book in law_downloader.iter_all_law_books(max_per_second=2.0):
        print(book.norms[0].metadaten.jurabk)

    # Stream the first 100 judgements with no throttle
    judgement_downloader = GermanJudgementDownloader()
    async for judgement in judgement_downloader.iter_first_n_judgements(100, max_per_second=None):
        print(f"{judgement.aktenzeichen} — {judgement.gertyp}")

asyncio.run(main())
```

Set `max_per_second=None` to start all downloads immediately without any rate limiting.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Data source: [Gesetze im Internet](https://www.gesetze-im-internet.de/)
- Data source: [Rechtsprechung im Internet](https://www.rechtsprechung-im-internet.de/)
- Author: Malte Weber
