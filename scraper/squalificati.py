from base import FantacalcioScraperBase

class SqualificatiScraper(FantacalcioScraperBase):
    def __init__(self):
        super().__init__()

    def get_squalificati_diffidati(self):
        """
        Scarica e analizza la pagina degli squalificati e diffidati.
        Ritorna un dizionario con le squadre come chiavi e i dati.
        """
        soup = self.fetch_page("/squalificati-e-diffidati-campionato-serie-a", delay=(1.5, 3.0))
        if not soup:
            return {}

        risultati = {}
        
        team_cards = soup.find_all('div', class_='team-card')
        for card in team_cards:
            team_name_tag = card.find('span', class_='team-name')
            if not team_name_tag:
                continue
            team_name = team_name_tag.text.strip()
            
            risultati[team_name] = {
                "squalificati": [],
                "diffidati": []
            }
            
            cols = card.find_all('div', class_='col')
            
            for col in cols:
                header = col.find('header')
                if not header:
                    continue
                label_tag = header.find('strong')
                if not label_tag:
                    continue
                
                tipo = label_tag.text.strip().lower() # "squalificati" o "diffidati"
                if tipo not in ["squalificati", "diffidati"]:
                    continue
                
                # Controllo vuoti
                empty_msg = col.find('div', class_='empty-list-message')
                if empty_msg and "Nessuno" in empty_msg.text:
                    continue
                
                ul = col.find('ul', class_='unstyled')
                if not ul:
                    continue
                    
                lis = ul.find_all('li')
                for li in lis:
                    name_tag = li.find('strong', class_='item-name')
                    desc_tag = li.find('div', class_='item-description')
                    
                    if name_tag:
                        item = {
                            "name": name_tag.text.strip()
                        }
                        if desc_tag:
                            item["details"] = desc_tag.text.strip()
                        risultati[team_name][tipo].append(item)
                    
        return risultati

if __name__ == "__main__":
    scraper = SqualificatiScraper()
    dati = scraper.get_squalificati_diffidati()
    import json
    print("Squalificati/Diffidati estratti:")
    print(json.dumps(dati, indent=2, ensure_ascii=False)[:500] + "...")
