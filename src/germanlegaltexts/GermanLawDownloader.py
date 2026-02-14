import io
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
import requests
import logging
from .model.Gesetzbuch import Gesetzbuch

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

class GermanLawDownloader:
    base_url = 'https://www.gesetze-im-internet.de'

    def download_law_xml(self, abbreviation: str) -> str:
        url = f"{self.base_url}/{abbreviation.lower()}/xml.zip"
        logger.debug(f"Downloading law XML for abbreviation '{abbreviation}' from {url}")

        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                response = requests.get(url, stream=True)
                if response.status_code != 200:
                    logger.error(f"Download failed: HTTP {response.status_code} for {url}")
                    raise ValueError(f"Failed to download the file: {url} - HTTP {response.status_code}")

                with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                    z.extractall(tmpdir)

                xml_files = [*Path(tmpdir).glob('*.xml')]
                if len(xml_files) != 1:
                    logger.error(f"Expected 1 XML file, found {len(xml_files)} for {abbreviation}")
                    raise RuntimeError(f"Expected 1 XML file, found {len(xml_files)}")
                else:
                    with open(Path(tmpdir) / xml_files[0], 'rb') as xml_file:
                        logger.debug(f"Successfully extracted XML: {xml_files[0].name}")
                        return xml_file.read().decode('utf-8')
            except Exception as e:
                logger.error(f"Error processing {url}: {str(e)}")
                raise ValueError(f"An error occurred while processing {url}: {str(e)}")

    def download_law_xml(self, url: str) -> str:
        logger.debug(f"Downloading law XML from {url}")

        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                response = requests.get(url, stream=True)
                if response.status_code != 200:
                    logger.error(f"Download failed: HTTP {response.status_code} for {url}")
                    raise ValueError(f"Failed to download the file: {url} - HTTP {response.status_code}")

                with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                    z.extractall(tmpdir)

                xml_files = [*Path(tmpdir).glob('*.xml')]
                if len(xml_files) != 1:
                    logger.error(f"Expected 1 XML file, found {len(xml_files)} in {url}")
                    raise RuntimeError(f"Expected 1 XML file, found {len(xml_files)}")
                else:
                    with open(Path(tmpdir) / xml_files[0], 'rb') as xml_file:
                        logger.debug(f"Successfully extracted XML: {xml_files[0].name}")
                        return xml_file.read().decode('utf-8')
            except Exception as e:
                logger.error(f"Error processing {url}: {str(e)}")
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
        Collects all XML paths from https://www.gesetze-im-internet.de/gii-toc.xml
        This XML file contains items with titles and links to XML zip files.

        Returns:
            A list of XML paths for all laws

        Raises:
            ValueError: If the TOC XML file cannot be downloaded or parsed
        """
        toc_url = f"{self.base_url}/gii-toc.xml"
        logger.debug(f"Fetching law index from {toc_url}")

        try:
            response = requests.get(toc_url)
            if response.status_code != 200:
                logger.error(f"Failed to download TOC: HTTP {response.status_code}")
                raise ValueError(f"Failed to download the TOC XML file: {toc_url} - HTTP {response.status_code}")

            xml_content = response.text
            root = ET.fromstring(xml_content)

            all_xml_paths = []

            for item in root.findall('.//item'):
                link_element = item.find('link')
                if link_element is not None and link_element.text:
                    link = link_element.text.strip()
                    all_xml_paths.append(link)

            logger.info(f"Retrieved {len(all_xml_paths)} law book entries from index")
            return all_xml_paths
        except ET.ParseError as e:
            logger.error(f"Failed to parse TOC XML: {str(e)}")
            raise ValueError(f"Failed to parse the TOC XML file: {str(e)}")
        except Exception as e:
            logger.error(f"Error processing TOC: {str(e)}")
            raise ValueError(f"An error occurred while processing the TOC XML file: {str(e)}")

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
        logger.info(f"Starting download of {len(xml_paths)} law books")

        law_books = []

        for i, xml_path in enumerate(xml_paths, 1):
            try:
                law_book = self.download_law_book(xml_path)
                law_books.append(law_book)
                
                if i % 50 == 0:
                    logger.info(f"Progress: {i}/{len(xml_paths)} law books downloaded")
            except Exception as e:
                logger.warning(f"Failed to download law book from {xml_path}: {str(e)}")
                continue

        logger.info(f"Completed: {len(law_books)}/{len(xml_paths)} law books downloaded successfully")
        return law_books
