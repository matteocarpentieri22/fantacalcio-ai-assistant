from base import FantacalcioScraperBase

class FormazioniScraper(FantacalcioScraperBase):
    def __init__(self):
        super().__init__()

    def get_probabili_formazioni(self):
        """
        Scarica e analizza la pagina delle probabili formazioni.
        Ritorna un dizionario con le partite e le rispettive formazioni.
        """
        soup = self.fetch_page("/probabili-formazioni-serie-a")
        if not soup:
            return {}

        formazioni = []
        
        # Trova tutte le partite
        matches = soup.find_all('li', class_='match-item')
        
        for match in matches:
            match_id = match.get('data-match-id')
            if not match_id:
                continue
                
            match_data = {
                "match_id": match_id,
                "home_team": {},
                "away_team": {}
            }
            
            # Estrazione nomi squadre
            home_label = match.find('label', class_='team-home')
            away_label = match.find('label', class_='team-away')
            
            if home_label and away_label:
                home_meta = home_label.find('meta', itemprop='name')
                away_meta = away_label.find('meta', itemprop='name')
                if home_meta and away_meta:
                    match_data["home_team"]["name"] = home_meta.get("content", "").strip()
                    match_data["away_team"]["name"] = away_meta.get("content", "").strip()

            # Estrazione moduli e giocatori
            pitch = match.find('div', class_='pitch')
            if pitch:
                teams = pitch.find_all('div', class_='team')
                for team in teams:
                    team_side = "home_team" if "team-home" in team.get('class', []) else "away_team"
                    
                    formation = team.get('data-team-formation', '')
                    match_data[team_side]["formation"] = formation
                    
                    # Giocatori titolari
                    titolari = []
                    lineup_ul = team.find('ul', class_='team-lineup')
                    if lineup_ul:
                        players = lineup_ul.find_all('li', class_='player')
                        for player in players:
                            name_span = player.find('span')
                            if name_span:
                                titolari.append(name_span.text.strip())
                    
                    match_data[team_side]["titolari"] = titolari
                    
                    # Panchina, infortunati, squalificati (opzionale, si possono aggiungere se presenti nel DOM)
                    
            formazioni.append(match_data)
            
        return formazioni

if __name__ == "__main__":
    scraper = FormazioniScraper()
    dati = scraper.get_probabili_formazioni()
    import json
    print(json.dumps(dati[:2], indent=2, ensure_ascii=False))  # Stampa le prime due per test
