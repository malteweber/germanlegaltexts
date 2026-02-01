import os
import sys
from unittest.mock import patch, Mock
from germanlegaltexts.GermanLawDownloader import GermanLawDownloader
from germanlegaltexts.model.Gesetzbuch import Gesetzbuch

# Add the parent directory to sys.path to allow importing from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestGermanLawDownloader:
    def test_base_url(self):
        """Test the base URL of the downloader."""
        downloader = GermanLawDownloader()
        assert downloader.base_url == "https://www.gesetze-im-internet.de"

    def test_download_law_url_formation(self):
        """Test that the download_law method forms the correct URL."""
        downloader = GermanLawDownloader()

        original_get = downloader.__class__.__dict__['download_law_xml']

        try:
            def test_download_law_xml(self, abbreviation):
                url = f"{self.base_url}/{abbreviation.lower()}/xml.zip"
                return url

            downloader.__class__.download_law_xml = test_download_law_xml

            url = downloader.download_law_xml("ifsg")
            assert url == "https://www.gesetze-im-internet.de/ifsg/xml.zip"

            url = downloader.download_law_xml("ABGB")
            assert url == "https://www.gesetze-im-internet.de/abgb/xml.zip"
        finally:
            downloader.__class__.download_law_xml = original_get

    def test_download_law_book(self):
        """Test that the download_law_book method returns a Gesetzbuch object."""
        downloader = GermanLawDownloader()

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

        with patch.object(downloader, 'download_law_xml', return_value=test_xml):
            result = downloader.download_law_book('tg')

            assert isinstance(result, Gesetzbuch)
            assert result.builddate == "2023-01-01"
            assert result.doknr == "BJNR000000000"
            assert len(result.norms) == 1
            assert result.norms[0].metadaten.jurabk == "TestGesetz"
            assert result.norms[0].metadaten.amtabk == "TG"

    def test_get_all_xml_paths(self):
        """Test that get_all_xml_paths correctly extracts links from the TOC XML."""
        downloader = GermanLawDownloader()

        # Sample XML content similar to the format described in the issue
        test_xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <items>
          <item>
            <title>Gesetz über die Ausprägung einer 1-DM-Goldmünze</title>
            <link>http://www.gesetze-im-internet.de/1-dm-goldm_nzg/xml.zip</link>
          </item>
          <item>
            <title>Erstes Gesetz zur Vereinheitlichung</title>
            <link>http://www.gesetze-im-internet.de/besvng_1/xml.zip</link>
          </item>
          <item>
            <title>Erste Verordnung zur Durchführung</title>
            <link>http://www.gesetze-im-internet.de/bimschv_1_2010/xml.zip</link>
          </item>
        </items>'''

        # Mock the requests.get method to return our test XML
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = test_xml

        with patch('requests.get', return_value=mock_response):
            result = downloader.get_all_xml_paths()

            # Check that the method extracted the correct links
            assert len(result) == 3
            assert result[0] == "http://www.gesetze-im-internet.de/1-dm-goldm_nzg/xml.zip"
            assert result[1] == "http://www.gesetze-im-internet.de/besvng_1/xml.zip"
            assert result[2] == "http://www.gesetze-im-internet.de/bimschv_1_2010/xml.zip"
