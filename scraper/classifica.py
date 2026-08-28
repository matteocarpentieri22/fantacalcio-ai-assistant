from base import FantacalcioScraperBase

class ClassificaScraper(FantacalcioScraperBase):
    def __init__(self):
        super().__init__()

    def get_classifica(self):
        """
        Scarica e analizza la classifica di Serie A.
        Ritorna una lista di dizionari con i dati di ogni squadra.
        """
        soup = self.fetch_page("/serie-a/classifica", delay=(1.5, 3.0))
        if not soup:
            return []

        classifica = []
        
        # Le righe della classifica hanno data-team-position e data-name
        rows = soup.find_all('tr')
        for row in rows:
            if not row.has_attr('data-team-position'):
                continue
                
            team_name = row.get('data-name', '')
            position = row.get('data-team-position', '')
            
            c = {
                "posizione": int(position) if position.isdigit() else position,
                "squadra": team_name
            }
            
            points_tag = row.find('td', class_='points')
            if points_tag: c['punti'] = int(points_tag.text.strip())
            
            played_tag = row.find('td', class_='played')
            if played_tag: c['giocate'] = int(played_tag.text.strip())
            
            won_tag = row.find('td', class_='won')
            if won_tag: c['vinte'] = int(won_tag.text.strip())
            
            drawn_tag = row.find('td', class_='drawn')
            if drawn_tag: c['pareggiate'] = int(drawn_tag.text.strip())
            
            lost_tag = row.find('td', class_='lost')
            if lost_tag: c['perse'] = int(lost_tag.text.strip())
            
            gs_tag = row.find('td', class_='goalsscored')
            if gs_tag: c['gol_fatti'] = int(gs_tag.text.strip())
            
            gc_tag = row.find('td', class_='goalsconceded')
            if gc_tag: c['gol_subiti'] = int(gc_tag.text.strip())
            
            gd_tag = row.find('td', class_='goalsdifference')
            if gd_tag: c['differenza_reti'] = int(gd_tag.text.strip())
            
            classifica.append(c)
            
        # Assicuriamoci che siano ordinate
        classifica.sort(key=lambda x: x.get('posizione', 99))
        return classifica

if __name__ == "__main__":
    scraper = ClassificaScraper()
    dati = scraper.get_classifica()
    import json
    print("Classifica estratta:")
    print(json.dumps(dati[:5], indent=2, ensure_ascii=False))
