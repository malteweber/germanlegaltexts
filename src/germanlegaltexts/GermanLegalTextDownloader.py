import tempfile
import requests
import zipfile
import io
import re
from pathlib import Path
from .model.Gesetzbuch import Gesetzbuch

class GermanLegalTextDownloader:

    base_url = 'https://www.gesetze-im-internet.de'

    def download_law_xml(self, abbreviation: str) -> str:
        url = f"{self.base_url}/{abbreviation.lower()}/xml.zip"

        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                response = requests.get(url, stream=True)
                if response.status_code != 200:
                    raise ValueError(f"Failed to download the file: {url} - HTTP {response.status_code}")

                with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                    z.extractall(tmpdir)

                xml_files = [*Path(tmpdir).glob('*.xml')]
                if len(xml_files) != 1:
                    raise RuntimeError(f"Expected 1 XML file, found {len(xml_files)}")
                else:
                    with open(Path(tmpdir) / xml_files[0], 'rb') as xml_file:
                        return xml_file.read().decode('utf-8')
            except Exception as e:
                raise ValueError(f"An error occurred while processing {url}: {str(e)}")

    def download_law_xml(self, url: str) -> str:

        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                response = requests.get(url, stream=True)
                if response.status_code != 200:
                    raise ValueError(f"Failed to download the file: {url} - HTTP {response.status_code}")

                with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                    z.extractall(tmpdir)

                xml_files = [*Path(tmpdir).glob('*.xml')]
                if len(xml_files) != 1:
                    raise RuntimeError(f"Expected 1 XML file, found {len(xml_files)}")
                else:
                    with open(Path(tmpdir) / xml_files[0], 'rb') as xml_file:
                        return xml_file.read().decode('utf-8')
            except Exception as e:
                raise ValueError(f"An error occurred while processing {url}: {str(e)}")

    def download_law_book(self, url: str) -> Gesetzbuch:
        """
        Downloads the law book for a given abbreviation and returns it as a Gesetzbuch object.

        Args:
            abbreviation: The abbreviation of the law book to download

        Returns:
            A Gesetzbuch object representing the downloaded law book

        Raises:
            ValueError: If the download fails or the XML cannot be parsed
        """
        xml_content = self.download_law_xml(url)
        return Gesetzbuch.from_xml(xml_content)

    def get_all_xml_paths(self) -> list:
        """
        Collects all XML paths from https://www.gesetze-im-internet.de/aktuell.html
        For all laws linked in each Teilliste, from A to Z and 1 to 9.

        Returns:
            A list of XML paths for all laws

        Raises:
            ValueError: If the index page cannot be downloaded
        """
        index_url = f"{self.base_url}/aktuell.html"

        response = requests.get(index_url)
        if response.status_code != 200:
            raise ValueError(f"Failed to download the index page: {index_url} - HTTP {response.status_code}")

        index_content = response.text

        teilliste_pattern = r'href="(\./Teilliste_[A-Z0-9]\.html)"'
        teilliste_links = re.findall(teilliste_pattern, index_content)

        all_xml_paths = []

        for teilliste_link in teilliste_links:
            clean_link = teilliste_link.replace("./", "")
            teilliste_url = f"{self.base_url}/{clean_link}"

            try:
                teilliste_response = requests.get(teilliste_url)
                if teilliste_response.status_code != 200:
                    continue

                teilliste_content = teilliste_response.text

                law_pattern = r'href="\./([^\/]+)/index\.html"'
                law_abbreviations = re.findall(law_pattern, teilliste_content)

                for abbreviation in law_abbreviations:
                    xml_path = f"{self.base_url}/{abbreviation}/xml.zip"
                    all_xml_paths.append(xml_path)
            except Exception:
                continue

        return all_xml_paths

    def download_all_law_books(self) -> list:
        """
        Downloads all law books available from the German legal texts website.

        This method calls get_all_xml_paths() to get URLs for all available law books,
        then downloads each one by calling download_law_book() for each URL.

        Returns:
            A list of Gesetzbuch objects representing all downloaded law books

        Raises:
            ValueError: If there are issues downloading the index page or any law book
        """
        xml_paths = self.get_all_xml_paths()

        law_books = []

        for xml_path in xml_paths:
            try:
                law_book = self.download_law_book(xml_path)
                law_books.append(law_book)
            except Exception as e:
                continue

        return law_books
