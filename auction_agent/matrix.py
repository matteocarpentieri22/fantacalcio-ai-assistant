import os
import json
from typing import Dict, List, Tuple

class MatrixAnalyzer:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.calendario = self._load_json("calendario.json")
        self.team_matches = self._build_team_matches()

    def _load_json(self, filename: str) -> List:
        path = os.path.join(self.data_dir, filename)
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f).get("data", [])
            except Exception:
                return []
        return []
        
    def _build_team_matches(self) -> Dict[str, List[int]]:
        """
        Costruisce per ogni squadra una lista di 38 interi.
        1 = Casa, -1 = Trasferta.
        """
        matches = {}
        for match in self.calendario:
            g = int(match.get("giornata", 0))
            if g == 0: continue
            
            home = match.get("casa")
            away = match.get("ospite")
            
            if home not in matches:
                matches[home] = [0] * 39
            if away not in matches:
                matches[away] = [0] * 39
                
            matches[home][g] = 1
            matches[away][g] = -1
            
        return matches

    def get_alternation_score(self, team1: str, team2: str) -> int:
        """
        Calcola quanto due squadre si alternano bene in casa/trasferta.
        Max = 38 (perfetta alternanza), Min = 0.
        """
        if team1 not in self.team_matches or team2 not in self.team_matches:
            return 0
            
        t1 = self.team_matches[team1]
        t2 = self.team_matches[team2]
        
        score = 0
        for i in range(1, 39):
            if t1[i] == 1 and t2[i] == -1:
                score += 1
            elif t1[i] == -1 and t2[i] == 1:
                score += 1
        return score

    def find_best_matches(self, target_team: str, top_n: int = 3) -> List[Tuple[str, int]]:
        if target_team not in self.team_matches:
            return []
            
        scores = []
        for team in self.team_matches:
            if team != target_team:
                score = self.get_alternation_score(target_team, team)
                scores.append((team, score))
                
        # Ordina per score decrescente
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_n]
