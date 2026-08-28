import React, { useState, useEffect, useRef } from 'react';
import './App.css';

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [state, setState] = useState(null);
  const [search, setSearch] = useState('');
  const [playersList, setPlayersList] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);
  
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  
  const [buyTeam, setBuyTeam] = useState('MyTeam');
  const [buyPrice, setBuyPrice] = useState('');

  const [selectedRole, setSelectedRole] = useState('p');
  const [tierList, setTierList] = useState([]);

  // Team editing state
  const [editingTeam, setEditingTeam] = useState(null);
  const [editNameValue, setEditNameValue] = useState("");
  const [expandedTeam, setExpandedTeam] = useState(null);
  
  const [apiKey, setApiKey] = useState(localStorage.getItem('geminiApiKey') || "");

  const searchRef = useRef(null);

  const fetchState = async () => {
    try {
      const res = await fetch(`${API_URL}/state`);
      const data = await res.json();
      setState(data);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchState();
    fetch(`${API_URL}/players`)
      .then(res => res.json())
      .then(data => setPlayersList(data))
      .catch(err => console.error(err));

    // Close dropdown when clicking outside
    const handleClickOutside = (event) => {
      if (searchRef.current && !searchRef.current.contains(event.target)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  useEffect(() => {
    fetch(`${API_URL}/tierlist/${selectedRole}`)
      .then(res => res.json())
      .then(data => setTierList(data))
      .catch(err => console.error(err));
  }, [selectedRole, state]); // refetch when role changes or state (buys) changes

  const handleSearch = async (playerName) => {
    const target = playerName || search;
    if (!target.trim()) return;
    setSearch(target);
    setShowDropdown(false);
    setLoading(true);
    setResult(null);
    try {
      const currentKey = localStorage.getItem('geminiApiKey') || apiKey;
      if (!currentKey) {
        alert("Inserisci la tua Gemini API Key in alto a destra prima di chiedere all'Agente.");
        setLoading(false);
        return;
      }
      const res = await fetch(`${API_URL}/advice`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ player_name: target, api_key: currentKey })
      });
      const data = await res.json();
      setResult(data);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  const handleBuy = async () => {
    if (!result || !buyPrice) return;
    const role = result.player_data?.stats?.role || 'A';
    const fvm = result.player_data?.quotazioni?.fvm || 0;

    try {
      const res = await fetch(`${API_URL}/buy`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          team: buyTeam,
          player: result.player_data.name || search,
          role,
          price: parseInt(buyPrice),
          fvm: parseInt(fvm)
        })
      });
      const data = await res.json();
      if (data.status === 'success') {
        setResult(null);
        setSearch('');
        setBuyPrice('');
        fetchState();
      } else {
        alert('Errore: ' + data.detail);
      }
    } catch (e) {
      alert('Errore di rete');
    }
  };

  const handleUndo = async () => {
    try {
      const res = await fetch(`${API_URL}/undo`, { method: 'POST' });
      const data = await res.json();
      if (data.status === 'success') {
        alert(`Acquisto di ${data.undone_player} annullato con successo.`);
        fetchState();
      } else {
        alert('Errore: ' + data.detail);
      }
    } catch (e) {
      alert('Errore di rete');
    }
  };

  const submitRename = async (oldName) => {
    if (!editNameValue.trim() || editNameValue === oldName) {
      setEditingTeam(null);
      return;
    }
    try {
      const res = await fetch(`${API_URL}/rename`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ old_name: oldName, new_name: editNameValue.trim() })
      });
      const data = await res.json();
      if (data.status === 'success') {
        if(buyTeam === oldName) setBuyTeam(editNameValue.trim());
        fetchState();
      } else {
        alert('Errore: ' + data.detail);
      }
    } catch (e) {
      console.error(e);
    }
    setEditingTeam(null);
  };

  const handleApiKeyChange = (e) => {
    const val = e.target.value;
    setApiKey(val);
    localStorage.setItem('geminiApiKey', val);
  };

  const filteredPlayers = playersList.filter(p => p.toLowerCase().includes(search.toLowerCase())).slice(0, 10);

  return (
    <div className="app-container">
      <div className="sidebar">
        <h2 style={{ marginBottom: 20 }}>Rivali</h2>
        {state && Object.values(state.teams).map(t => (
          <div key={t.name} className="team-list-item">
            {editingTeam === t.name ? (
              <input 
                className="edit-team-input"
                autoFocus
                value={editNameValue}
                onChange={e => setEditNameValue(e.target.value)}
                onBlur={() => submitRename(t.name)}
                onKeyDown={e => e.key === 'Enter' && submitRename(t.name)}
              />
            ) : (
              <div 
                className="team-name" 
                title="Clicca per rinominare"
                onClick={() => { setEditingTeam(t.name); setEditNameValue(t.name); }}
              >
                {t.name} ✎
              </div>
            )}
            <div>Budget: <span className="team-budget">{t.budget}</span></div>
            <div>Max Bid: <span className="team-maxbid">{t.max_bid}</span></div>
            <div className="team-slots">
              <span className="slot-p">P: {3 - (t.remaining_slots?.p || 0)}/3</span>
              <span className="slot-d">D: {8 - (t.remaining_slots?.d || 0)}/8</span>
              <span className="slot-c">C: {8 - (t.remaining_slots?.c || 0)}/8</span>
              <span className="slot-a">A: {6 - (t.remaining_slots?.a || 0)}/6</span>
            </div>
            
            {t.players && t.players.length > 0 && (
              <div className="roster-toggle" onClick={() => setExpandedTeam(expandedTeam === t.name ? null : t.name)}>
                {expandedTeam === t.name ? 'Nascondi Rosa ▲' : 'Mostra Rosa ▼'}
              </div>
            )}
            
            {expandedTeam === t.name && (
              <ul className="team-roster-list">
                {t.players.map((p, idx) => (
                  <li key={idx}>
                    <span className={`roster-role role-${p.role.toLowerCase()}`}>{p.role.toUpperCase()}</span>
                    <span className="roster-name">{p.name}</span>
                    <span className="roster-price">{p.price} cr</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        ))}
      </div>
      
      <div className="main-content">
        <div className="api-key-container">
          <input 
            type="password" 
            className="api-key-input" 
            placeholder="🔑 Incolla qui la tua Gemini API Key" 
            value={apiKey} 
            onChange={handleApiKeyChange} 
          />
        </div>
        <h1 className="title">Fantacalcio Auction Agent</h1>
        
        <div className="search-box" ref={searchRef}>
          <div className="autocomplete-wrapper">
            <input 
              className="search-input"
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setShowDropdown(true);
              }}
              onFocus={() => setShowDropdown(true)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  setShowDropdown(false);
                  handleSearch(search);
                }
              }}
              placeholder="Cerca giocatore..."
            />
            {showDropdown && search && filteredPlayers.length > 0 && (
              <ul className="autocomplete-dropdown">
                {filteredPlayers.map(p => (
                  <li key={p} onClick={() => handleSearch(p)}>{p}</li>
                ))}
              </ul>
            )}
          </div>
          <button className="btn-search" onClick={() => handleSearch(search)} disabled={loading}>
            Chiedi all'Agente
          </button>
          <button className="btn-undo" onClick={handleUndo} title="Annulla Ultimo Acquisto">
            ↩ Undo
          </button>
        </div>

        {loading && (
          <div className="loading-container">
            <div className="spinner"></div>
            <p className="loading-text">L'Agente sta analizzando dati storici e budget...</p>
          </div>
        )}

        {result && !loading && (
          <div className="card">
            <h2>{result.player_data.name}</h2>
            {result.player_data.infortunato && (
              <div style={{ color: '#ff6b6b', marginTop: 10, fontWeight: 'bold' }}>
                ⚠️ INFORTUNATO: {result.player_data.infortunio_dettagli}
              </div>
            )}
            
            <div className="stats-grid">
              <div className="stat-item">
                <div className="stat-value">{result.player_data?.quotazioni?.fvm || '-'}</div>
                <div className="stat-label">FVM</div>
              </div>
              <div className="stat-item">
                <div className="stat-value">{result.player_data?.stats?.fanta_media_voto || '-'}</div>
                <div className="stat-label">FantaMedia</div>
              </div>
              <div className="stat-item">
                <div className="stat-value">{result.player_data?.stats?.gol || '0'}</div>
                <div className="stat-label">Gol</div>
              </div>
              <div className="stat-item">
                <div className="stat-value">{result.player_data?.stats?.assist || '0'}</div>
                <div className="stat-label">Assist</div>
              </div>
            </div>

            <div className="advice-box">
              <strong>Consiglio dell'Agente:</strong><br/><br/>
              {result.advice}
            </div>

            {result.best_matches?.length > 0 && (
              <div style={{ marginTop: 20 }}>
                <strong>Incroci Perfetti (Matchmaking):</strong>
                <ul>
                  {result.best_matches.map(m => (
                    <li key={m[0]}>{m[0]} (Score: {m[1]}/38)</li>
                  ))}
                </ul>
              </div>
            )}

            <div className="buy-section">
              <select className="buy-select" value={buyTeam} onChange={e => setBuyTeam(e.target.value)}>
                {state && Object.keys(state.teams).map(name => (
                  <option key={name} value={name}>{name}</option>
                ))}
              </select>
              <input 
                type="number" 
                className="buy-input"
                placeholder="Prezzo pagato" 
                value={buyPrice} 
                onChange={e => setBuyPrice(e.target.value)} 
              />
              <button className="btn-buy" onClick={handleBuy}>Registra Acquisto</button>
            </div>
          </div>
        )}
      </div>

      <div className="tierlist-panel">
        <div className="role-tabs">
          <button className={selectedRole === 'p' ? 'active tab-p' : 'tab-p'} onClick={() => setSelectedRole('p')}>P</button>
          <button className={selectedRole === 'd' ? 'active tab-d' : 'tab-d'} onClick={() => setSelectedRole('d')}>D</button>
          <button className={selectedRole === 'c' ? 'active tab-c' : 'tab-c'} onClick={() => setSelectedRole('c')}>C</button>
          <button className={selectedRole === 'a' ? 'active tab-a' : 'tab-a'} onClick={() => setSelectedRole('a')}>A</button>
        </div>
        
        <div className="slots-container">
          {tierList.map(slot => (
            <div key={slot.slot_number} className="slot-card">
              <div className="slot-title">Slot {slot.slot_number}</div>
              <ul className="slot-players">
                {slot.players.map(p => (
                  <li key={p.name} onClick={() => handleSearch(p.name)} title="Analizza">
                    <div className="slot-player-info">
                      <span className="slot-player-name">{p.name}</span>
                      {p.team && <span className="slot-player-team">{p.team.toUpperCase()}</span>}
                    </div>
                    <span className="slot-player-fvm">FVM: {p.fvm}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default App;
