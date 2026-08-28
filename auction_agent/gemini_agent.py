import os
import json
import google.generativeai as genai
from typing import Dict, Any
from dotenv import load_dotenv

class GeminiAgent:
    def __init__(self, data_dir: str):
        load_dotenv()
        self.api_key = os.environ.get("GEMINI_API_KEY", "")
        # We don't configure genai here anymore, we do it per-request or globally when needed
        if self.api_key:
            genai.configure(api_key=self.api_key)
            
        self.data_dir = data_dir
        self.statistiche = self._load_json("statistiche.json")
        self.quotazioni = self._load_json("quotazioni.json")
        self.infortunati = self._load_json("infortunati.json")
        self.news = self._load_json("news.json")
        self.rigoristi = self._load_json("rigoristi.json")

    def _load_json(self, filename: str) -> Dict:
        path = os.path.join(self.data_dir, filename)
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f).get("data", {})
            except Exception:
                return {}
        return {}
        
    def find_player_data(self, name: str) -> Dict[str, Any]:
        """Trova tutte le informazioni disponibili per un giocatore."""
        name_lower = name.lower().strip()
        data = {"name": name, "stats": None, "quotazioni": None, "infortunato": False}
        
        # Cerca statistiche
        if isinstance(self.statistiche, list):
            for p in self.statistiche:
                if name_lower in p.get("name", "").lower():
                    data["stats"] = p
                    data["team"] = p.get("team", "")
                    break
                        
        # Cerca quotazioni
        if isinstance(self.quotazioni, list):
            for p in self.quotazioni:
                if name_lower in p.get("name", "").lower():
                    data["quotazioni"] = p
                    if not data.get("team"):
                        data["team"] = p.get("team", "")
                    break

        # Cerca se infortunato
        if data.get("team") and isinstance(self.infortunati, dict):
            team_inf = self.infortunati.get(data["team"], [])
            for inf in team_inf:
                if name_lower in inf.get("name", "").lower():
                    data["infortunato"] = True
                    data["infortunio_dettagli"] = inf.get("details", "")
                    break

        # Cerca notizie recenti
        data["news_recenti"] = []
        if isinstance(self.news, list):
            for n in self.news:
                # Controlliamo se il cognome del giocatore è nel titolo o nel testo
                if name_lower in n.get("title", "").lower() or name_lower in n.get("content", "").lower():
                    data["news_recenti"].append(n.get("title", ""))

        # Cerca se è rigorista o tiratore
        data["rigorista"] = False
        data["tiratore_piazzati"] = []
        if data.get("team") and isinstance(self.rigoristi, dict):
            team_rig = self.rigoristi.get(data["team"], {})
            for category, players in team_rig.items():
                for p in players:
                    if name_lower in p.lower():
                        if category == "Rigori":
                            data["rigorista"] = True
                        else:
                            data["tiratore_piazzati"].append(category)

        return data

    def generate_advice(self, player_name: str, auction_state: Any, provided_api_key: str = None) -> str:
        key = provided_api_key or self.api_key
        if not key:
            return "Errore: Inserisci la tua API Key nell'interfaccia."
            
        genai.configure(api_key=key)
        model = genai.GenerativeModel('gemini-2.5-pro')
        
        player_data = self.find_player_data(player_name)
        
        # Costruisci lo stato della rosa dell'utente
        my_team = auction_state.teams.get("MyTeam")
        my_budget = my_team.budget if my_team else 0
        my_max_bid = my_team.max_bid if my_team else 0
        my_roster = [f"{p.name} ({p.role})" for p in my_team.players] if my_team else []
        
        # Costruisci lo stato degli avversari
        opponents_info = []
        richest_opp_budget = 0
        for name, team in auction_state.teams.items():
            if name != "MyTeam":
                if team.max_bid > richest_opp_budget:
                    richest_opp_budget = team.max_bid
                roster_str = ", ".join([f"{p.name} ({p.role})" for p in team.players])
                opponents_info.append(f"- {name}: Budget={team.budget}, MaxBid={team.max_bid}, Slot_Rimasti={sum(team.remaining_slots.values())}, Rosa=[{roster_str}]")
                
        opponents_str = "\n".join(opponents_info) if opponents_info else "Nessun avversario registrato."
        
        prompt = f"""Sei un Agente esperto per l'asta del Fantacalcio (lega a 10, 500 crediti, modificatore difesa).
Devi dare un consiglio rapido e letale (massimo 4 frasi) su questo giocatore appena chiamato: {player_name}.

DATI DEL GIOCATORE:
{json.dumps(player_data, indent=2, ensure_ascii=False)}

STATO DELLA MIA SQUADRA (MyTeam):
Budget residuo: {my_budget}
Rilancio massimo: {my_max_bid}
Rosa attuale: {', '.join(my_roster) if my_roster else 'Vuota'}

STATO AVVERSARI:
{opponents_str}
Il rivale con il rilancio massimo più alto può offrire fino a: {richest_opp_budget} crediti.

Considera:
1. Se il giocatore è infortunato o ci sono notizie recenti rilevanti, avvisa.
2. Evidenzia se è un rigorista o tiratore, aumenta il suo valore se lo è.
3. Basandoti sull'FVM, dimmi un prezzo massimo consigliato per non sforare.
4. Dimmi se ha senso per la mia rosa e se qualche avversario ha disperato bisogno di lui o ti ostacolerà (valutando le loro rose e budget).

Rispondi in modo diretto, come un coach al tavolo dell'asta. No preamboli.
"""
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Errore durante la connessione a Gemini: {str(e)}"
