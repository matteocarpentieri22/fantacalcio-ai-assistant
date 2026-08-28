from base import FantacalcioScraperBase

class StatisticheScraper(FantacalcioScraperBase):
    def __init__(self):
        super().__init__()

    def get_statistiche(self):
        """
        Scarica e analizza la pagina delle statistiche di Serie A.
        Ritorna una lista di dizionari con le statistiche dei giocatori.
        """
        # Aumentiamo il timeout perch la pagina statistiche pu essere pesante
        soup = self.fetch_page("/statistiche-serie-a", delay=(2.0, 4.0))
        if not soup:
            return []

        statistiche = []
        
        # Le righe dei giocatori hanno la classe "player-row"
        player_rows = soup.find_all('tr', class_='player-row')
        
        for row in player_rows:
            stats = {}
            
            # Nome giocatore
            name_tag = row.find('th', class_='player-name')
            if name_tag:
                a_tag = name_tag.find('a', class_='player-name')
                if a_tag:
                    stats['name'] = a_tag.text.strip()
            
            if 'name' not in stats:
                continue
                
            # Ruolo
            role_tag = row.find('th', class_='player-role-classic')
            if role_tag:
                span = role_tag.find('span', class_='role')
                if span:
                    stats['role'] = span.get('data-value', '')
                    
            # Squadra
            team_tag = row.find('td', {'data-col-key': 'sq'})
            if team_tag:
                stats['team'] = team_tag.text.strip()
                
            # Partite giocate
            pg_tag = row.find('td', {'data-col-key': 'pg'})
            if pg_tag:
                stats['partite_giocate'] = pg_tag.text.strip()
                
            # Media voto
            mv_tag = row.find('td', {'data-col-key': 'mv'})
            if mv_tag:
                stats['media_voto'] = mv_tag.text.strip().replace(',', '.')
                
            # Fanta media voto
            mfv_tag = row.find('td', {'data-col-key': 'mfv'})
            if mfv_tag:
                stats['fanta_media_voto'] = mfv_tag.text.strip().replace(',', '.')
                
            # Gol
            gol_tag = row.find('td', {'data-col-key': 'gol'})
            if gol_tag:
                stats['gol'] = gol_tag.text.strip()
                
            # Gol subiti
            gs_tag = row.find('td', {'data-col-key': 'gs'})
            if gs_tag:
                stats['gol_subiti'] = gs_tag.text.strip()
                
            # Assist
            ass_tag = row.find('td', {'data-col-key': 'ass'})
            if ass_tag:
                stats['assist'] = ass_tag.text.strip()
                
            # Ammonizioni
            amm_tag = row.find('td', {'data-col-key': 'amm'})
            if amm_tag:
                stats['ammonizioni'] = amm_tag.text.strip()
                
            # Espulsioni
            esp_tag = row.find('td', {'data-col-key': 'esp'})
            if esp_tag:
                stats['espulsioni'] = esp_tag.text.strip()
                
            statistiche.append(stats)
            
        return statistiche

if __name__ == "__main__":
    scraper = StatisticheScraper()
    stats = scraper.get_statistiche()
    import json
    print(f"Estratti {len(stats)} giocatori.")
    print(json.dumps(stats[:3], indent=2, ensure_ascii=False))
