import json
from typing import Dict, List, Optional
from pydantic import BaseModel

class PlayerPurchase(BaseModel):
    name: str
    role: str
    price: int
    team: str

class TeamState(BaseModel):
    name: str
    budget: int = 500
    players: List[PlayerPurchase] = []
    
    @property
    def remaining_slots(self) -> Dict[str, int]:
        max_slots = {'p': 3, 'd': 8, 'c': 8, 'a': 6}
        current = {'p': 0, 'd': 0, 'c': 0, 'a': 0}
        for p in self.players:
            current[p.role.lower()] += 1
        return {k: max_slots[k] - current[k] for k in max_slots}

    @property
    def total_missing(self) -> int:
        return sum(self.remaining_slots.values())
        
    @property
    def max_bid(self) -> int:
        missing = self.total_missing
        if missing == 0:
            return 0
        return self.budget - (missing - 1)

class AuctionState:
    def __init__(self):
        # Inizializziamo 10 squadre
        self.teams: Dict[str, TeamState] = {
            f"Team {i}": TeamState(name=f"Team {i}") for i in range(1, 11)
        }
        self.teams["MyTeam"] = self.teams.pop("Team 1")
        self.teams["MyTeam"].name = "MyTeam"
        
        self.sold_players: List[PlayerPurchase] = []
        self.inflation_by_role = {'p': 1.0, 'd': 1.0, 'c': 1.0, 'a': 1.0}
        self.state_file = 'asta_salvataggio.json'
        
        # Try to load existing state
        self.load_state()

    def save_state(self):
        data = {
            "teams": {name: {"name": t.name, "budget": t.budget, "players": [p.dict() for p in t.players]} for name, t in self.teams.items()},
            "sold_players": [p.dict() for p in self.sold_players],
        }
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Errore durante il salvataggio dello stato: {e}")

    def load_state(self):
        import os
        if not os.path.exists(self.state_file):
            return
            
        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            self.teams.clear()
            for name, t_data in data.get("teams", {}).items():
                team = TeamState(name=t_data["name"], budget=t_data["budget"])
                for p_data in t_data.get("players", []):
                    team.players.append(PlayerPurchase(**p_data))
                self.teams[name] = team
                
            self.sold_players.clear()
            for p_data in data.get("sold_players", []):
                self.sold_players.append(PlayerPurchase(**p_data))
        except Exception as e:
            print(f"Errore durante il caricamento dello stato: {e}")

    def buy_player(self, team_name: str, player_name: str, role: str, price: int, fvm: int = 0):
        if team_name not in self.teams:
            raise ValueError(f"Squadra {team_name} non trovata")
            
        team = self.teams[team_name]
        
        # Check validità
        if team.remaining_slots[role.lower()] <= 0:
            raise ValueError(f"Nessuno slot {role.upper()} rimasto per {team_name}")
            
        if team.budget < price:
            raise ValueError(f"Budget insufficiente per {team_name}")
            
        if price > team.max_bid:
            raise ValueError(f"Offerta {price} superiore al Max Bid ({team.max_bid}) per {team_name}")

        purchase = PlayerPurchase(name=player_name, role=role, price=price, team=team_name)
        team.players.append(purchase)
        team.budget -= price
        self.sold_players.append(purchase)
        
        # Aggiorna inflazione rudimentale per ruolo (prezzo / fvm) se fvm è disponibile
        if fvm > 0:
            sold_role = [p for p in self.sold_players if p.role.lower() == role.lower()]
            # Questo è solo un placeholder, la logica complessa andrebbe affinata
            # Es: calcolare somma(prezzi) / somma(fvm) per il ruolo
            pass
            
        self.save_state()
        return team
        
    def undo_last_purchase(self) -> PlayerPurchase:
        if not self.sold_players:
            raise ValueError("Nessun acquisto da annullare.")
            
        last_purchase = self.sold_players.pop()
        team = self.teams[last_purchase.team]
        
        # Remove from team.players (find the exact object or one matching name)
        for p in team.players:
            if p.name == last_purchase.name and p.role == last_purchase.role:
                team.players.remove(p)
                break
                
        # Refund budget
        team.budget += last_purchase.price
        
        self.save_state()
        return last_purchase
        
    def get_max_bid(self, team_name: str) -> int:
        if team_name not in self.teams:
            return 0
        return self.teams[team_name].max_bid

    def rename_team(self, old_name: str, new_name: str):
        if old_name not in self.teams:
            raise ValueError(f"Squadra {old_name} non trovata")
        if new_name in self.teams:
            raise ValueError(f"Nome {new_name} già in uso")
            
        team = self.teams.pop(old_name)
        team.name = new_name
        self.teams[new_name] = team
        
        # Aggiorna anche i nomi nelle liste dei giocatori venduti (opzionale, ma utile)
        for p in self.sold_players:
            if p.team == old_name:
                p.team = new_name
        for p in team.players:
            if p.team == old_name:
                p.team = new_name
                
        self.save_state()
