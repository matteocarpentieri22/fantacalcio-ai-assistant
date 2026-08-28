from base import FantacalcioScraperBase

class RigoristiScraper(FantacalcioScraperBase):
    def __init__(self):
        super().__init__()

    def get_rigoristi(self):
        """
        Scarica e analizza la pagina dei rigoristi e tiratori da fermo della Serie A.
        Ritorna un dizionario con i dati strutturati per squadra.
        """
        soup = self.fetch_page("/rigoristi-serie-a", delay=(1.0, 2.0))
        if not soup:
            return {}

        teams_data = {}
        for card in soup.find_all('div', class_='team-card'):
            team_name_tag = card.find('span', class_='team-name')
            if not team_name_tag:
                continue
                
            team_name = team_name_tag.text.strip()
            teams_data[team_name] = {}
            
            for col in card.find_all('div', class_='col'):
                header_tag = col.find('header', class_='primary')
                if not header_tag:
                    continue
                    
                category = header_tag.text.strip()
                players = []
                for li in col.find_all('li'):
                    player_tag = li.find('a', class_='player-name')
                    if player_tag:
                        name = player_tag.text.strip()
                        players.append(name)
                        
                teams_data[team_name][category] = players
                
        return teams_data

if __name__ == "__main__":
    scraper = RigoristiScraper()
    rigoristi = scraper.get_rigoristi()
    import json
    print(json.dumps(rigoristi, indent=2, ensure_ascii=False))
