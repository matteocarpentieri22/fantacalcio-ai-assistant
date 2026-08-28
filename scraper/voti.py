from base import FantacalcioScraperBase

class VotiScraper(FantacalcioScraperBase):
    def __init__(self):
        super().__init__()

    def _format_grade(self, val):
        if not val:
            return ''
        val = val.replace(',', '.')
        if len(val) == 2 and val.isdigit():
            val = f"{val[0]}.{val[1]}"
        return val

    def get_voti(self):
        """
        Scarica e analizza la pagina dei voti.
        Ritorna un dizionario strutturato per squadre e giocatori.
        """
        soup = self.fetch_page("/voti-fantacalcio-serie-a")
        if not soup:
            return {}

        risultati = {}
        
        # Trova tutte le tabelle delle squadre
        team_tables = soup.find_all('li', class_='team-table')
        
        for team_table in team_tables:
            header = team_table.find('header')
            if not header:
                continue
                
            team_name_tag = team_table.find('a', class_='team-name')
            if not team_name_tag:
                continue
            team_name = team_name_tag.text.strip()
            
            risultati[team_name] = []
            
            tbody = team_table.find('tbody')
            if not tbody:
                continue
                
            rows = tbody.find_all('tr')
            for row in rows:
                player_data = {}
                
                # Nome giocatore
                name_tag = row.find('a', class_='player-name')
                if not name_tag:
                    continue
                player_data['name'] = name_tag.text.strip()
                
                # Ruolo
                role_tag = row.find('span', class_='role')
                if role_tag:
                    player_data['role'] = role_tag.get('data-value', '')
                    
                # Voti (Redazione FC, Statistico, Italia)
                # Prendiamo il primo pill (Redazione FC) per il voto e fantavoto
                pills = row.find_all('div', class_='pill')
                if pills and len(pills) > 0:
                    fc_pill = pills[0]
                    voto_tag = fc_pill.find('span', class_='player-grade')
                    fv_tag = fc_pill.find('span', class_='player-fanta-grade')
                    
                    player_data['voto'] = self._format_grade(voto_tag.get('data-value', '')) if voto_tag else ''
                    player_data['fantavoto'] = self._format_grade(fv_tag.get('data-value', '')) if fv_tag else ''
                    
                # Bonus/Malus
                bonuses = row.find_all('span', class_='player-bonus')
                player_bonus = []
                for bonus in bonuses:
                    title = bonus.get('title', '')
                    val = bonus.get('data-value', '0').replace(',', '.')
                    if float(val) > 0:
                        player_bonus.append({title: val})
                
                player_data['bonus_malus'] = player_bonus
                
                risultati[team_name].append(player_data)
                
        return risultati

if __name__ == "__main__":
    scraper = VotiScraper()
    voti = scraper.get_voti()
    import json
    # Stampiamo solo i voti di una squadra come esempio
    first_team = list(voti.keys())[0] if voti else None
    if first_team:
        print(f"Voti per {first_team}:")
        print(json.dumps(voti[first_team][:3], indent=2, ensure_ascii=False))
