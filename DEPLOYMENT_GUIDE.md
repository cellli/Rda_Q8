# 🚀 Guida Rapida Deployment Streamlit Cloud

## Setup in 5 minuti

### 1️⃣ Prepara il Repository

```bash
# Crea una nuova directory
mkdir rda-q8-system
cd rda-q8-system

# Copia i files che ti ho fornito:
# - rda_q8_pro.py
# - requirements.txt
# - README.md
# - .gitignore
# - .streamlit/config.toml
```

### 2️⃣ Crea Repository GitHub

**Opzione A: Via Web**
1. Vai su github.com
2. Clicca "New repository"
3. Nome: `rda-q8-system`
4. Visibilità: Private (consigliato per dati aziendali)
5. NON inizializzare con README
6. Clicca "Create repository"

**Opzione B: Via CLI**
```bash
git init
git add .
git commit -m "Initial commit - RDA Q8 Pro v14.0"
git branch -M main
git remote add origin https://github.com/TUO-USERNAME/rda-q8-system.git
git push -u origin main
```

### 3️⃣ Deploy su Streamlit Cloud

1. **Vai su**: https://streamlit.io/cloud
2. **Sign up/Login**: Usa il tuo account GitHub
3. **New app**: Clicca "New app"
4. **Configurazione**:
   - Repository: `TUO-USERNAME/rda-q8-system`
   - Branch: `main`
   - Main file path: `rda_q8_pro.py`
   - App URL: `rda-q8-italia` (o quello che preferisci)

### 4️⃣ Configura Secrets (API Key)

1. Vai su **App settings** (icona ingranaggio)
2. Clicca su **Secrets**
3. Incolla questo contenuto:

```toml
GOOGLE_API_KEY = "AIza_LA_TUA_API_KEY_QUI"
```

4. Clicca **Save**

### 5️⃣ Deploy! 🎉

1. Clicca **Deploy!**
2. Attendi 2-3 minuti per il primo deploy
3. L'app sarà disponibile su: `https://TUO-APP.streamlit.app`

---

## 🔄 Aggiornamenti Futuri

Quando vuoi aggiornare l'app:

```bash
# Modifica i file localmente
git add .
git commit -m "Descrizione modifiche"
git push

# Streamlit Cloud farà il redeploy automaticamente!
```

---

## 🎯 Modifica per Usare Secrets

Se vuoi che l'app carichi automaticamente la API key dai secrets di Streamlit, modifica questa sezione nel file `rda_q8_pro.py`:

**Trova (circa linea 740):**
```python
api_key = st.text_input(
    "Google API Key",
    type="password",
    value=st.session_state.api_key,
    help="Inserisci la tua API key di Google Gemini"
)
```

**Sostituisci con:**
```python
# Try to load from secrets first
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    st.success("✅ API Key caricata dai secrets")
    st.session_state.api_key = api_key
except:
    api_key = st.text_input(
        "Google API Key",
        type="password",
        value=st.session_state.api_key,
        help="Inserisci la tua API key di Google Gemini"
    )
```

Poi fai commit e push.

---

## 🔒 Sicurezza

### ✅ FARE:
- Usa repository **private** per dati aziendali
- Configura API key nei **secrets di Streamlit**
- NON committare mai `secrets.toml` su Git
- Usa `.gitignore` per escludere file sensibili

### ❌ NON FARE:
- NON mettere API keys nel codice
- NON condividere il link pubblico senza autenticazione
- NON caricare file CSV con dati sensibili su Git

---

## 🆘 Troubleshooting Deploy

### Deploy fallisce
**Errore**: `ModuleNotFoundError`
- **Soluzione**: Verifica che `requirements.txt` sia corretto

### Secrets non funzionano
**Errore**: API key non trovata
- **Soluzione**: Verifica di aver salvato i secrets e fatto redeploy

### App lenta
**Problema**: Performance scarse
- **Soluzione**: Streamlit Cloud ha risorse limitate, considera:
  - Ridurre dimensioni dataset
  - Usare caching con `@st.cache_data`
  - Upgrade a piano Business se necessario

---

## 📊 Piani Streamlit Cloud

- **Community (Free)**:
  - 1 app pubblica
  - Risorse limitate
  - Perfetto per test

- **Business ($30/mese/utente)**:
  - App private
  - Più risorse
  - Supporto prioritario
  - SSO/SAML

Per Q8 Italia, considera il piano Business se:
- Hai più utenti (>5)
- Serve privacy garantita
- Serve performance enterprise

---

## 🎓 Best Practices

### Performance
```python
# Usa caching per dati statici
@st.cache_data
def load_data(file):
    return pd.read_csv(file)
```

### Testing Locale
```bash
# Testa sempre in locale prima di pushare
streamlit run rda_q8_pro.py

# Verifica che tutto funzioni
# - Caricamento dati ✓
# - Dashboard ✓
# - AI ✓
# - Export ✓
```

### Versioning
```bash
# Usa git tags per le versioni
git tag -a v14.0 -m "Professional Edition Release"
git push origin v14.0
```

---

**Fatto! 🎉**

Ora hai un'app enterprise-grade deployata sul cloud, accessibile ovunque, sempre aggiornata!
