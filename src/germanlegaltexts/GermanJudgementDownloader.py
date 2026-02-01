import io
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
import requests
from .model.Rechtsprechung import Rechtsprechung, RIIIndexItem


class GermanJudgementDownloader:
    """Downloader for German court judgements from rechtsprechung-im-internet.de"""
    
    base_url = 'https://www.rechtsprechung-im-internet.de'

    def download_judgement_xml(self, url: str) -> str:
        """
        Downloads the XML content of a judgement from a given URL.
        
        Args:
            url: The URL to the ZIP file containing the judgement XML
            
        Returns:
            The XML content as a string
            
        Raises:
            ValueError: If the download fails or the ZIP doesn't contain exactly one XML file
        """
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

    def download_judgement(self, url: str) -> Rechtsprechung:
        """
        Downloads a judgement and returns it as a Rechtsprechung object.

        Args:
            url: The URL to the ZIP file containing the judgement XML

        Returns:
            A Rechtsprechung object representing the downloaded judgement

        Raises:
            ValueError: If the download fails or the XML cannot be parsed
        """
        xml_content = self.download_judgement_xml(url)
        return Rechtsprechung.from_xml(xml_content)

    def get_all_judgement_index_items(self) -> list[RIIIndexItem]:
        """
        Collects all judgement index items from the rii-toc.xml file.
        This XML file contains metadata for all available judgements.

        Returns:
            A list of RIIIndexItem objects containing metadata for all judgements

        Raises:
            ValueError: If the TOC XML file cannot be downloaded or parsed
        """
        toc_url = f"{self.base_url}/rii-toc.xml"

        try:
            response = requests.get(toc_url)
            if response.status_code != 200:
                raise ValueError(f"Failed to download the TOC XML file: {toc_url} - HTTP {response.status_code}")

            xml_content = response.text
            root = ET.fromstring(xml_content)

            index_items = []

            for item in root.findall('.//item'):
                gericht = item.findtext('gericht')
                entsch_datum = item.findtext('entsch-datum')
                aktenzeichen = item.findtext('aktenzeichen')
                link_element = item.find('link')
                modified = item.findtext('modified')

                # Ensure we have required fields
                if gericht and entsch_datum and aktenzeichen and link_element is not None and link_element.text:
                    link = link_element.text.strip()
                    index_items.append(RIIIndexItem(
                        gericht=gericht,
                        entsch_datum=entsch_datum,
                        aktenzeichen=aktenzeichen,
                        link=link,
                        modified=modified or ""
                    ))

            return index_items

        except ET.ParseError as e:
            raise ValueError(f"Failed to parse the TOC XML file: {str(e)}")
        except Exception as e:
            raise ValueError(f"An error occurred while processing {toc_url}: {str(e)}")

    def download_all_judgements(self) -> list[Rechtsprechung]:
        """
        Downloads all available judgements from rechtsprechung-im-internet.de.
        
        WARNING: This will download a very large number of judgements and may take
        a significant amount of time and bandwidth.

        Returns:
            A list of Rechtsprechung objects for all available judgements

        Raises:
            ValueError: If any download fails
        """
        index_items = self.get_all_judgement_index_items()
        judgements = []

        for i, item in enumerate(index_items, 1):
            try:
                judgement = self.download_judgement(item.link)
                judgements.append(judgement)
                
                if i % 100 == 0:
                    print(f"Downloaded {i}/{len(index_items)} judgements...")
                    
            except Exception as e:
                print(f"Warning: Failed to download judgement {item.aktenzeichen}: {str(e)}")
                continue

        return judgements

    def download_first_n_judgements(self, n: int) -> list[Rechtsprechung]:
        """
        Downloads the first n judgements from the index.

        Args:
            n: The number of judgements to download

        Returns:
            A list of up to n Rechtsprechung objects

        Raises:
            ValueError: If n is less than 1 or if the index cannot be retrieved
        """
        if n < 1:
            raise ValueError("n must be at least 1")

        index_items = self.get_all_judgement_index_items()
        items_to_download = index_items[:n]
        
        judgements = []

        for i, item in enumerate(items_to_download, 1):
            try:
                judgement = self.download_judgement(item.link)
                judgements.append(judgement)
                print(f"Downloaded {i}/{len(items_to_download)} judgements...")
                
            except Exception as e:
                print(f"Warning: Failed to download judgement {item.aktenzeichen}: {str(e)}")
                continue

        return judgements

    def get_judgement_count(self) -> int:
        """
        Returns the total number of available judgements in the index.

        Returns:
            The number of judgements in the rii-toc.xml index

        Raises:
            ValueError: If the index cannot be retrieved
        """
        return len(self.get_all_judgement_index_items())
