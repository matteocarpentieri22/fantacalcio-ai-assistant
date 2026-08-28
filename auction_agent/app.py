from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List

from auction_state import AuctionState
from gemini_agent import GeminiAgent
from matrix import MatrixAnalyzer
import os

app = FastAPI(title="Fantacalcio Auction Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "new scraping", "data"))
print(f"Data Dir Configured: {DATA_DIR}")

# Instanza globale dello stato
state = AuctionState()
gemini = GeminiAgent(DATA_DIR)
matrix = MatrixAnalyzer(DATA_DIR)

class BuyRequest(BaseModel):
    team: str
    player: str
    role: str
    price: int
    fvm: int = 0

class RenameRequest(BaseModel):
    old_name: str
    new_name: str

@app.get("/state")
def get_state():
    return {
        "teams": {name: {
            "name": t.name,
            "budget": t.budget,
            "max_bid": t.max_bid,
            "remaining_slots": t.remaining_slots,
            "players": t.players
        } for name, t in state.teams.items()},
        "inflation": state.inflation_by_role
    }

@app.post("/buy")
def buy_player(req: BuyRequest):
    try:
        team = state.buy_player(req.team, req.player, req.role, req.price, req.fvm)
        return {"status": "success", "team": team.name, "budget": team.budget}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/undo")
def undo_purchase():
    try:
        last = state.undo_last_purchase()
        return {"status": "success", "undone_player": last.name}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/rename")
def rename_team(req: RenameRequest):
    try:
        state.rename_team(req.old_name, req.new_name)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/players")
def get_players():
    if isinstance(gemini.quotazioni, list):
        names = [p.get("name") for p in gemini.quotazioni if p.get("name")]
        return sorted(list(set(names)))
    return []

@app.get("/tierlist/{role}")
def get_tierlist(role: str):
    # Role: 'p', 'd', 'c', 'a'
    if not isinstance(gemini.quotazioni, list):
        return []
    
    sold_names = {p.player.lower() for p in state.sold_players}
    
    # Filter by role and exclude sold players
    available_players = []
    for p in gemini.quotazioni:
        if p.get("role", "").lower() == role.lower():
            name = p.get("name", "")
            if name and name.lower() not in sold_names:
                fvm_val = p.get("fvm", "0")
                fvm_int = int(fvm_val) if str(fvm_val).isdigit() else 0
                available_players.append({"name": name, "fvm": fvm_int, "team": p.get("team", "")})
    
    # Sort by FVM descending
    available_players.sort(key=lambda x: x["fvm"], reverse=True)
    
    # Group in slots of 10
    slots = []
    chunk_size = 10
    for i in range(0, len(available_players), chunk_size):
        slots.append({
            "slot_number": (i // chunk_size) + 1,
            "players": available_players[i:i + chunk_size]
        })
        
    return slots

@app.get("/advice/{player_name}")
def get_advice(player_name: str):
    # 1. Trova info base
    data = gemini.find_player_data(player_name)
    
    # 2. Genera testo Gemini
    text = gemini.generate_advice(player_name, state)
    
    # 3. Matchmaking difensori se ruolo è D o P
    # Poiché non abbiamo il ruolo certo nel payload iniziale se non dallo scraping, 
    # se la squadra è nota, generiamo gli incroci
    best_matches = []
    if data.get("team"):
        best_matches = matrix.find_best_matches(data["team"])
        
    return {
        "player_data": data,
        "advice": text,
        "best_matches": best_matches
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
