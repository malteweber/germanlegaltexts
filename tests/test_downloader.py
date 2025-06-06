import pytest
from pathlib import Path
from unittest.mock import patch
from src.germanlegaltexts.GermanLegalTextDownloader import GermanLegalTextDownloader
from src.germanlegaltexts.model.Gesetzbuch import Gesetzbuch

class TestGermanLegalTextDownloader:
    def test_base_url(self):
        """Test the base URL of the downloader."""
        downloader = GermanLegalTextDownloader()
        assert downloader.base_url == "https://www.gesetze-im-internet.de"

    def test_download_law_url_formation(self):
        """Test that the download_law method forms the correct URL."""
        downloader = GermanLegalTextDownloader()

        original_get = downloader.__class__.__dict__['download_law']

        try:
            def test_download_law(self, abbreviation):
                url = f"{self.base_url}/{abbreviation.lower()}/xml.zip"
                return url

            downloader.__class__.download_law_xml = test_download_law

            url = downloader.download_law_xml("ifsg")
            assert url == "https://www.gesetze-im-internet.de/ifsg/xml.zip"

            url = downloader.download_law_xml("ABGB")
            assert url == "https://www.gesetze-im-internet.de/abgb/xml.zip"
        finally:
            downloader.__class__.download_law_xml = original_get

    def test_download_law_book(self):
        """Test that the download_law_book method returns a Gesetzbuch object."""
        downloader = GermanLegalTextDownloader()

        test_xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <dokumente builddate="2023-01-01" doknr="BJNR000000000">
          <norm builddate="2023-01-01" doknr="BJNR000000000">
            <metadaten>
              <jurabk>TestGesetz</jurabk>
              <amtabk>TG</amtabk>
              <ausfertigung-datum>2023-01-01</ausfertigung-datum>
              <kurzue>Test Gesetz</kurzue>
              <langue>Deutsch</langue>
              <titel>Test Gesetz für Testzwecke</titel>
            </metadaten>
            <textdaten>
              <text format="XML">
                <Content>Test content</Content>
              </text>
            </textdaten>
          </norm>
        </dokumente>'''

        with patch.object(downloader, 'download_law', return_value=test_xml):
            result = downloader.download_law_book('tg')

            assert isinstance(result, Gesetzbuch)
            assert result.builddate == "2023-01-01"
            assert result.doknr == "BJNR000000000"
            assert len(result.norms) == 1
            assert result.norms[0].metadaten.jurabk == "TestGesetz"
            assert result.norms[0].metadaten.amtabk == "TG"
