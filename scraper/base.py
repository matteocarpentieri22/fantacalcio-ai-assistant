import requests
from bs4 import BeautifulSoup
import time
import random
import logging

class FantacalcioScraperBase:
    def __init__(self, base_url="https://www.fantacalcio.it"):
        self.base_url = base_url
        self.session = requests.Session()
        # Elenco di User-Agent per evitare il ban
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        ]
        
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(self.__class__.__name__)

    def _get_headers(self):
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive'
        }

    def fetch_page(self, endpoint, delay=(1.0, 3.0)):
        """
        Scarica una pagina web e restituisce un oggetto BeautifulSoup.
        """
        url = endpoint if endpoint.startswith("http") else f"{self.base_url}{endpoint}"
        self.logger.info(f"Fetching {url}...")
        
        # Aggiunge un ritardo casuale tra le richieste
        if delay:
            time.sleep(random.uniform(*delay))

        try:
            response = self.session.get(url, headers=self._get_headers(), timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Errore durante il fetch di {url}: {e}")
            return None
