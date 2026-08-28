import json
import os
import time
import schedule
import logging
from datetime import datetime

from formazioni import FormazioniScraper
from voti import VotiScraper
from statistiche import StatisticheScraper
from quotazioni import QuotazioniScraper
from news import NewsScraper
from infortunati import InfortunatiScraper
from squalificati import SqualificatiScraper
from classifica import ClassificaScraper
from calendario import CalendarioScraper
from rigoristi import RigoristiScraper

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("FantacalcioOrchestrator")

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

def setup_directories():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        logger.info(f"Creata directory dati in {DATA_DIR}")

def save_to_json(filename, data):
    filepath = os.path.join(DATA_DIR, filename)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                "last_update": datetime.now().isoformat(),
                "data": data
            }, f, indent=2, ensure_ascii=False)
        logger.info(f"Salvato {filename} con successo.")
    except Exception as e:
        logger.error(f"Errore durante il salvataggio di {filename}: {e}")

def run_all_scrapers():
    logger.info("Iniziando ciclo completo di scraping...")
    
    # 1. Probabili Formazioni
    try:
        f_scraper = FormazioniScraper()
        formazioni = f_scraper.get_probabili_formazioni()
        save_to_json('formazioni.json', formazioni)
    except Exception as e:
        logger.error(f"Errore nello scraping formazioni: {e}")
        
    time.sleep(2)
        
    # 2. Voti
    try:
        v_scraper = VotiScraper()
        voti = v_scraper.get_voti()
        save_to_json('voti.json', voti)
    except Exception as e:
        logger.error(f"Errore nello scraping voti: {e}")
        
    time.sleep(2)
        
    # 3. Statistiche
    try:
        s_scraper = StatisticheScraper()
        stats = s_scraper.get_statistiche()
        save_to_json('statistiche.json', stats)
    except Exception as e:
        logger.error(f"Errore nello scraping statistiche: {e}")
        
    time.sleep(2)
        
    # 4. Quotazioni
    try:
        q_scraper = QuotazioniScraper()
        quots = q_scraper.get_quotazioni()
        save_to_json('quotazioni.json', quots)
    except Exception as e:
        logger.error(f"Errore nello scraping quotazioni: {e}")
        
    time.sleep(2)
        
    # 5. News
    try:
        n_scraper = NewsScraper()
        news = n_scraper.get_ultime_notizie()
        save_to_json('news.json', news)
    except Exception as e:
        logger.error(f"Errore nello scraping news: {e}")

    time.sleep(2)
    
    # 6. Infortunati
    try:
        i_scraper = InfortunatiScraper()
        inf = i_scraper.get_infortunati()
        save_to_json('infortunati.json', inf)
    except Exception as e:
        logger.error(f"Errore nello scraping infortunati: {e}")
        
    time.sleep(2)
    
    # 7. Squalificati / Diffidati
    try:
        sq_scraper = SqualificatiScraper()
        sq = sq_scraper.get_squalificati_diffidati()
        save_to_json('squalificati.json', sq)
    except Exception as e:
        logger.error(f"Errore nello scraping squalificati: {e}")

    time.sleep(2)
    
    # 8. Classifica
    try:
        cl_scraper = ClassificaScraper()
        classifica = cl_scraper.get_classifica()
        save_to_json('classifica.json', classifica)
    except Exception as e:
        logger.error(f"Errore nello scraping classifica: {e}")

    time.sleep(2)
    
    # 9. Calendario
    try:
        cal_scraper = CalendarioScraper()
        # Per test scarichiamo 3 giornate, per il full metti 38
        calendario = cal_scraper.get_calendario(max_giornate=38)
        save_to_json('calendario.json', calendario)
    except Exception as e:
        logger.error(f"Errore nello scraping calendario: {e}")

    time.sleep(2)
    
    # 10. Rigoristi
    try:
        rig_scraper = RigoristiScraper()
        rigoristi = rig_scraper.get_rigoristi()
        save_to_json('rigoristi.json', rigoristi)
    except Exception as e:
        logger.error(f"Errore nello scraping rigoristi: {e}")

    logger.info("Ciclo di scraping completato!")

def start_scheduler(run_every_minutes=60):
    """
    Avvia lo scheduler per eseguire lo scraping periodicamente.
    """
    setup_directories()
    
    # Esegue subito il primo ciclo
    run_all_scrapers()
    
    # Pianifica i successivi
    schedule.every(run_every_minutes).minutes.do(run_all_scrapers)
    
    logger.info(f"Scheduler avviato. Prossimo ciclo tra {run_every_minutes} minuti.")
    
    # Loop infinito per lo scheduler (puoi fermarlo con Ctrl+C)
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Scheduler interrotto manualmente.")

if __name__ == "__main__":
    # Puoi configurare la frequenza qui. Per il "tempo reale", un intervallo di 15-30 minuti 
    # di solito un buon compromesso per non essere bannati, ma dipende dalle tue necessit.
    # Impostiamo 30 minuti di default.
    setup_directories()
    
    # Se vuoi solo testare un'esecuzione singola commenta start_scheduler e usa run_all_scrapers:
    run_all_scrapers()
    
    # Per avviare lo schedule continuo (de-commentare per il live):
    # start_scheduler(run_every_minutes=30)
