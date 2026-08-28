from base import FantacalcioScraperBase

class InfortunatiScraper(FantacalcioScraperBase):
    def __init__(self):
        super().__init__()

    def get_infortunati(self):
        """
        Scarica e analizza la pagina degli infortunati.
        Ritorna un dizionario con le squadre come chiavi e liste di infortunati come valori.
        """
        soup = self.fetch_page("/infortunati-serie-a", delay=(1.5, 3.0))
        if not soup:
            return {}

        risultati = {}
        
        team_cards = soup.find_all('div', class_='team-card')
        for card in team_cards:
            team_name_tag = card.find('span', class_='team-name')
            if not team_name_tag:
                continue
            team_name = team_name_tag.text.strip()
            
            risultati[team_name] = []
            
            # Check for empty list
            empty_msg = card.find('div', class_='empty-list-message')
            if empty_msg and "Nessuno" in empty_msg.text:
                continue
                
            ul = card.find('ul', class_='unstyled')
            if not ul:
                continue
                
            lis = ul.find_all('li')
            for li in lis:
                name_tag = li.find('strong', class_='item-name')
                desc_tag = li.find('div', class_='item-description')
                
                if name_tag:
                    risultati[team_name].append({
                        "name": name_tag.text.strip(),
                        "details": desc_tag.text.strip() if desc_tag else ""
                    })
                    
        return risultati

if __name__ == "__main__":
    scraper = InfortunatiScraper()
    dati = scraper.get_infortunati()
    import json
    print("Infortunati estratti:")
    print(json.dumps(dati, indent=2, ensure_ascii=False)[:500] + "...")
