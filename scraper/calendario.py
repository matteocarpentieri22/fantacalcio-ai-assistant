import re
from typing import Optional
from base import FantacalcioScraperBase

def _safe_int(text: str) -> Optional[int]:
    try:
        return int(text.strip())
    except (ValueError, AttributeError):
        return None

class CalendarioScraper(FantacalcioScraperBase):
    def __init__(self):
        super().__init__()

    def get_calendario(self, max_giornate=38):
        """
        Scarica il calendario completo o le prime 'max_giornate'.
        Ritorna una lista di dizionari con i dettagli delle partite.
        """
        # Partiamo dalla prima pagina per recuperare i link delle giornate
        soup = self.fetch_page("/serie-a/calendario")
        if not soup:
            return []

        all_matches = self._parse_matches(soup)

        # Cerca i link alle altre giornate
        giornate_links = soup.select("a[href*='/serie-a/calendario/']")
        giornata_nums = set()
        for a in giornate_links:
            href = a.get("href", "")
            m = re.search(r"/serie-a/calendario/(\d+)", href)
            if m:
                giornata_nums.add(int(m.group(1)))

        existing_giornate = {m.get("giornata") for m in all_matches if m.get("giornata")}
        
        # Iteriamo sulle giornate trovate (fino a max_giornate per sicurezza)
        for g in sorted(giornata_nums):
            if str(g) in existing_giornate:
                continue
            if g > max_giornate:
                break
                
            soup_g = self.fetch_page(f"/serie-a/calendario/{g}", delay=(1.0, 2.5))
            if soup_g:
                all_matches.extend(self._parse_matches(soup_g))
                
        return all_matches

    def _parse_matches(self, soup) -> list:
        matches = []
        match_pills = soup.select("[data-match-id], .match-pill, div[itemtype*='SportsEvent']")

        for el in match_pills:
            try:
                m = self._parse_match_pill(el)
                if m:
                    matches.append(m)
            except Exception as e:
                pass
        return matches

    def _parse_match_pill(self, el) -> Optional[dict]:
        match_id = el.get("data-match-id")
        if not match_id:
            parent = el.find_parent(attrs={"data-match-id": True})
            if parent:
                match_id = parent.get("data-match-id")
                
        match_status = el.get("data-match-status")

        # Giornata
        mw_el = el.select_one(".matchweek")
        giornata = mw_el.get_text(strip=True) if mw_el else None
        
        # Pulizia stringa giornata (es. "1ª Giornata" -> "1")
        if giornata:
            m = re.search(r"(\d+)", giornata)
            if m:
                giornata = m.group(1)

        # Squadra casa
        home_el = el.select_one("[itemprop='homeTeam'] a, label.team-home a")
        home_name = home_el.get_text(strip=True) if home_el else None

        # Squadra ospite
        away_el = el.select_one("[itemprop='awayTeam'] a, label.team-away a")
        away_name = away_el.get_text(strip=True) if away_el else None

        if not home_name or not away_name:
            return None

        # Risultato
        score_home = _safe_int(self._text(el, ".score-home"))
        score_away = _safe_int(self._text(el, ".score-away"))

        # Data e ora
        date_meta = el.select_one("meta[itemprop='startDate']")
        match_date = date_meta.get("content") if date_meta else None
        
        if not match_date:
            day_el = el.select_one(".match-date .day")
            hour_el = el.select_one(".match-date .hours")
            day = day_el.get_text(strip=True) if day_el else ""
            hour = hour_el.get_text(strip=True) if hour_el else ""
            match_date = f"{day} {hour}".strip() or None

        # Stadio
        stadium_el = el.select_one(".stadium, [itemprop='location']")
        stadium = stadium_el.get_text(strip=True) if stadium_el else None

        return {
            "match_id": match_id,
            "giornata": giornata,
            "data": match_date,
            "stadio": stadium,
            "stato": match_status,  # 0=non giocata, 1=in corso, 2=finita
            "casa": home_name,
            "ospite": away_name,
            "gol_casa": score_home,
            "gol_ospite": score_away
        }

    @staticmethod
    def _text(el, selector: str) -> str:
        found = el.select_one(selector)
        return found.get_text(strip=True) if found else ""

if __name__ == "__main__":
    scraper = CalendarioScraper()
    # Esegue test solo per 2 giornate per non sovraccaricare
    dati = scraper.get_calendario(max_giornate=2)
    import json
    print(f"Estratte {len(dati)} partite.")
    print(json.dumps(dati[:3], indent=2, ensure_ascii=False))
