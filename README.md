# RDA Q8 Intelligence System - Professional Edition

Sistema di analisi intelligente per RDA (Richieste di Assistenza) Q8 Italia con integrazione AI Gemini.

## 🚀 Features

### Core Features
- ✅ **Caricamento dati robusto**: Gestione automatica di encoding multipli (UTF-16, UTF-8, Latin1, CP1252)
- ✅ **Pulizia dati avanzata**: Trasformazione automatica di costi, date e categorie
- ✅ **Validazione dati**: Controlli automatici sulla qualità dei dati caricati
- ✅ **Colonne derivate**: Calcolo automatico di SLA, stato, durata interventi

### Dashboard & Analytics
- 📊 **KPI Cards moderne**: Spesa totale, ticket, stati, SLA
- 📈 **Visualizzazioni interattive**:
  - Top 10 ditte per spesa
  - Top 10 punti vendita per numero ticket
  - Trend mensile della spesa
  - Distribuzione per categoria
- 🔍 **Filtri avanzati**: Filtra per stato, ditta, SLA
- 📥 **Export Power BI**: Esportazione CSV ottimizzata

### AI Assistant
- 🤖 **Integrazione Gemini AI**: Analisi intelligente dei dati
- 💬 **Chat interface**: Fai domande in linguaggio naturale
- 📊 **Analisi contestuale**: L'AI riceve statistiche aggregate e campioni di dati
- 🎯 **Risposte precise**: Basate sui tuoi dati reali

## 📋 Requisiti

### Sistema
- Python 3.8+
- Connessione internet (per AI Gemini)

### Dipendenze
```
streamlit>=1.30.0
pandas>=2.0.0
plotly>=5.18.0
google-generativeai>=0.3.0
openpyxl>=3.1.0
```

## 🛠️ Setup Locale

### 1. Installazione

```bash
# Clona o scarica i files
cd rda-q8-system

# Crea ambiente virtuale (consigliato)
python -m venv venv
source venv/bin/activate  # Su Windows: venv\Scripts\activate

# Installa dipendenze
pip install -r requirements.txt
```

### 2. Configurazione API Key

Per utilizzare l'AI Assistant, hai bisogno di una Google API Key:

1. Vai su [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Crea un nuovo progetto (se necessario)
3. Genera una nuova API key
4. Copia la key (inizia con `AIza...`)

### 3. Avvio Applicazione

```bash
streamlit run rda_q8_pro.py
```

L'app si aprirà automaticamente nel browser a `http://localhost:8501`

## 🌐 Deploy su Streamlit Cloud

### Setup Streamlit Cloud

1. **Crea account**: Vai su [streamlit.io/cloud](https://streamlit.io/cloud)

2. **Connetti repository**:
   - Carica i files su GitHub
   - Collega il tuo repository a Streamlit Cloud
   - Seleziona il file `rda_q8_pro.py` come main file

3. **Configura secrets** (per API Key):
   - Vai su App settings → Secrets
   - Aggiungi:
     ```toml
     GOOGLE_API_KEY = "your-api-key-here"
     ```

4. **Deploy**: Clicca su "Deploy!"

### Modifica per usare Secrets (opzionale)

Se vuoi usare i secrets di Streamlit, modifica la sezione AI nel codice:

```python
# Nel render_sidebar(), sostituisci:
api_key = st.text_input(...)

# Con:
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    st.success("✅ API Key caricata dai secrets")
except:
    api_key = st.text_input(...)
```

## 📖 Guida all'uso

### 1. Caricamento Dati

1. Clicca su "Carica file RDA" nella sidebar
2. Seleziona il file esportato dal sistema Q8 (formato `.csv` o `.txt`)
3. Clicca su "🔄 Carica File"
4. Attendi la conferma di caricamento

### 2. Dashboard

La tab "Dashboard" mostra:
- **KPI**: Metriche principali (spesa, ticket, SLA)
- **Grafici interattivi**: Top ditte, punti vendita, trend, categorie
- Tutti i grafici sono interattivi (zoom, hover, download)

### 3. AI Assistant

1. **Configura AI**:
   - Inserisci la tua Google API Key nella sidebar
   - Clicca su "🔗 Connetti AI"

2. **Fai domande**:
   - "Quali sono i punti vendita più costosi?"
   - "Mostrami il trend della spesa negli ultimi 6 mesi"
   - "Quali ditte hanno superato più spesso gli SLA?"
   - "Analizza i costi per regione"

3. **Ricevi risposte**: L'AI analizzerà i dati e risponderà in modo dettagliato

### 4. Dati Completi

- Visualizza tutti i dati in formato tabella
- Usa i filtri per esplorare sottoinsiemi
- Esporta per Power BI dalla sidebar

## 🎯 Esempi di Domande per l'AI

### Analisi Costi
- "Qual è la distribuzione dei costi per regione?"
- "Quali sono le 5 ditte più costose?"
- "Mostrami il costo medio per punto vendita"

### Analisi Temporale
- "Come varia la spesa mese per mese?"
- "Quali mesi hanno avuto più interventi?"
- "Qual è la durata media degli interventi?"

### Analisi SLA
- "Quanti ticket sono fuori SLA per ditta?"
- "Quali categorie superano più spesso gli SLA?"
- "C'è correlazione tra costo e rispetto SLA?"

### Analisi Comparative
- "Confronta le performance delle top 3 ditte"
- "Quali punti vendita hanno i costi più alti rispetto alla media?"
- "Trova anomalie nei costi"

## 🔧 Troubleshooting

### File non carica
- **Problema**: Errore durante il caricamento
- **Soluzione**: Verifica che sia un file CSV/TXT valido con le colonne corrette

### AI non risponde
- **Problema**: Errore AI o timeout
- **Soluzione**: 
  - Verifica la API key
  - Controlla la connessione internet
  - Riprova la domanda (più semplice)

### Grafici non visualizzati
- **Problema**: Colonne mancanti nel dataset
- **Soluzione**: Verifica che il file contenga tutte le colonne richieste

### Performance lente
- **Problema**: App lenta con dataset grandi
- **Soluzione**: 
  - L'AI analizza max 2000 righe
  - Usa filtri per ridurre il dataset visualizzato

## 📊 Struttura File RDA

Il sistema si aspetta un file CSV/TXT con queste colonne:

| Colonna Originale | Colonna Sistema | Tipo |
|------------------|-----------------|------|
| Costo Intervento | costo_totale | Numerico |
| N. RdA | numero_rda | Testo |
| Data apertura | data_apertura | Data |
| Data Chiusura | data_chiusura | Data |
| Organizzazione | ditta | Testo |
| Punto Vendita | punto_vendita | Testo |
| Descrizione | descrizione | Testo |
| Macrocategoria | macrocategoria | Testo |
| Stato | stato_originale | Testo |
| Priorità | priorita | Testo |
| Fuori SLA | fuori_sla | Boolean |
| Scadenza | scadenza | Data |
| Città | citta | Testo |
| Provincia | provincia | Testo |
| Regione Cod. | regione | Testo |

## 🔒 Privacy & Sicurezza

- ✅ I dati NON vengono salvati permanentemente
- ✅ L'AI riceve solo statistiche aggregate + campioni
- ✅ La API key è gestita in modo sicuro (non condivisa)
- ⚠️ Usa sempre secrets per API keys in produzione

## 🆘 Supporto

Per problemi o suggerimenti:
- Apri una issue su GitHub
- Contatta: stefano@q8italia.it

## 📝 Changelog

### v14.0 - Professional Edition
- ✨ Architettura completamente refactored
- ✨ UI/UX moderna e professionale
- ✨ Error handling robusto
- ✨ Validazione dati avanzata
- ✨ AI ottimizzata (context-aware)
- ✨ Performance migliorate
- ✨ Documentazione completa

### v13.0 - Limitless Agent
- Feature: AI con accesso dataset completo
- Fix: Encoding issues

---

**Sviluppato con ❤️ per Q8 Italia**
*Stefano - AI Engineering Team*
