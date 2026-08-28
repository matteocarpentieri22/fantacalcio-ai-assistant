from base import FantacalcioScraperBase

class QuotazioniScraper(FantacalcioScraperBase):
    def __init__(self):
        super().__init__()

    def get_quotazioni(self):
        """
        Scarica e analizza la pagina delle quotazioni e FVM.
        Ritorna una lista di dizionari con i valori di mercato dei giocatori.
        """
        soup = self.fetch_page("/quotazioni-fantacalcio", delay=(1.5, 3.5))
        if not soup:
            return []

        quotazioni = []
        
        player_rows = soup.find_all('tr', class_='player-row')
        
        for row in player_rows:
            q = {}
            
            # Nome giocatore
            name_tag = row.find('th', class_='player-name')
            if name_tag:
                a_tag = name_tag.find('a', class_='player-name')
                if a_tag:
                    q['name'] = a_tag.text.strip()
            
            if 'name' not in q:
                continue
                
            # Ruolo
            role_tag = row.find('th', class_='player-role-classic')
            if role_tag:
                span = role_tag.find('span', class_='role')
                if span:
                    q['role'] = span.get('data-value', '')
                    
            # Squadra
            team_tag = row.find('td', {'data-col-key': 'sq'})
            if team_tag:
                q['team'] = team_tag.text.strip()
                
            # Quotazione Iniziale Classic
            qi_tag = row.find('td', {'data-col-key': 'c_qi'})
            if qi_tag:
                q['quotazione_iniziale'] = qi_tag.text.strip()
                
            # Quotazione Attuale Classic
            qa_tag = row.find('td', {'data-col-key': 'c_qa'})
            if qa_tag:
                q['quotazione_attuale'] = qa_tag.text.strip()
                
            # FVM Classic
            fvm_tag = row.find('td', {'data-col-key': 'c_fvm'})
            if fvm_tag:
                q['fvm'] = fvm_tag.text.strip()
                
            quotazioni.append(q)
            
        return quotazioni

if __name__ == "__main__":
    scraper = QuotazioniScraper()
    quots = scraper.get_quotazioni()
    import json
    print(f"Estratti {len(quots)} giocatori.")
    print(json.dumps(quots[:3], indent=2, ensure_ascii=False))
