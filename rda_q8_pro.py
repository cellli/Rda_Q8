"""
RDA Q8 INTELLIGENT SYSTEM - Professional Edition
================================================
Version: 14.0 (Production Ready)
Author: Stefano - AI Engineering
Description: Sistema di analisi intelligente per RDA Q8 con Gemini AI
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path
import warnings
from typing import Optional, Dict, List, Tuple
import json

# Conditional imports
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Centralized configuration management"""
    
    # App metadata
    APP_TITLE = "RDA Q8 Intelligence System"
    VERSION = "14.0"
    AUTHOR = "Stefano - Q8 Italia"
    
    # Column mapping
    COL_MAPPING = {
        'Costo Intervento': 'costo_totale',
        'N. RdA': 'numero_rda',
        'Data apertura': 'data_apertura',
        'Data Chiusura': 'data_chiusura',
        'Organizzazione': 'ditta',
        'Punto Vendita': 'punto_vendita',
        'Descrizione': 'descrizione',
        'Macrocategoria': 'macrocategoria',
        'Stato': 'stato_originale',
        'Priorità': 'priorita',
        'Fuori SLA': 'fuori_sla',
        'Scadenza': 'scadenza',
        'Città': 'citta',
        'Provincia': 'provincia',
        'Regione Cod.': 'regione'
    }
    
    # Data types
    DATE_COLUMNS = ['data_apertura', 'data_chiusura', 'scadenza']
    NUMERIC_COLUMNS = ['costo_totale']
    
    # UI Configuration
    CHART_COLORS = px.colors.qualitative.Plotly
    KPI_COLORS = {
        'primary': '#1f77b4',
        'success': '#2ca02c',
        'warning': '#ff7f0e',
        'danger': '#d62728'
    }
    
    # AI Configuration
    MAX_ROWS_FOR_AI = 2000
    AI_TEMPERATURE = 0.1
    AI_MAX_TOKENS = 2048

# ============================================================================
# UTILITIES
# ============================================================================

class Logger:
    """Simple logging utility"""
    
    @staticmethod
    def info(message: str):
        st.toast(f"ℹ️ {message}", icon="ℹ️")
    
    @staticmethod
    def success(message: str):
        st.toast(f"✅ {message}", icon="✅")
    
    @staticmethod
    def warning(message: str):
        st.toast(f"⚠️ {message}", icon="⚠️")
    
    @staticmethod
    def error(message: str):
        st.toast(f"❌ {message}", icon="❌")


class DataValidator:
    """Data validation utilities"""
    
    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> Tuple[bool, str]:
        """Validate if dataframe has required structure"""
        if df.empty:
            return False, "DataFrame vuoto"
        
        required_cols = ['numero_rda', 'costo_totale']
        missing = [col for col in required_cols if col not in df.columns]
        
        if missing:
            return False, f"Colonne mancanti: {', '.join(missing)}"
        
        return True, "Validazione OK"
    
    @staticmethod
    def validate_api_key(key: str) -> bool:
        """Basic API key validation"""
        return key and len(key) > 20 and key.startswith('AIza')

# ============================================================================
# DATA ENGINE
# ============================================================================

class DataEngine:
    """Advanced data loading and processing engine"""
    
    def __init__(self):
        self.df: Optional[pd.DataFrame] = None
        self.metadata: Dict = {}
    
    def load_file(self, file_obj) -> Tuple[bool, str, Optional[pd.DataFrame]]:
        """
        Load and process file with robust error handling
        
        Returns:
            Tuple of (success: bool, message: str, dataframe: Optional[pd.DataFrame])
        """
        try:
            # Try multiple encodings
            df = self._try_load_with_encodings(file_obj)
            
            if df is None:
                return False, "Impossibile leggere il file con nessun encoding", None
            
            # Clean and transform
            df_clean = self._clean_and_transform(df)
            
            if df_clean.empty:
                return False, "Nessun dato valido dopo la pulizia", None
            
            # Validate
            is_valid, msg = DataValidator.validate_dataframe(df_clean)
            if not is_valid:
                return False, msg, None
            
            # Store metadata
            self._update_metadata(df_clean)
            
            self.df = df_clean
            return True, f"✅ {len(df_clean)} righe caricate con successo", df_clean
            
        except Exception as e:
            return False, f"Errore durante il caricamento: {str(e)}", None
    
    def _try_load_with_encodings(self, file_obj) -> Optional[pd.DataFrame]:
        """Try loading file with multiple encodings"""
        encodings = ['utf-16', 'utf-8', 'latin1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                file_obj.seek(0)
                df = pd.read_csv(file_obj, sep='\t', encoding=encoding, engine='python')
                if not df.empty:
                    return df
            except:
                continue
        
        return None
    
    def _clean_and_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and transform raw data"""
        try:
            # Clean column names
            df.columns = df.columns.str.strip()
            
            # Map columns
            df_clean = pd.DataFrame()
            for old_col, new_col in Config.COL_MAPPING.items():
                if old_col in df.columns:
                    col_data = df[old_col]
                    # Handle multi-column case
                    if isinstance(col_data, pd.DataFrame):
                        df_clean[new_col] = col_data.iloc[:, 0]
                    else:
                        df_clean[new_col] = col_data
            
            # Clean numeric columns
            df_clean = self._clean_numeric_columns(df_clean)
            
            # Clean date columns
            df_clean = self._clean_date_columns(df_clean)
            
            # Add derived columns
            df_clean = self._add_derived_columns(df_clean)
            
            return df_clean
            
        except Exception as e:
            st.error(f"Errore durante la pulizia: {str(e)}")
            return pd.DataFrame()
    
    def _clean_numeric_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean numeric columns (costs)"""
        if 'costo_totale' in df.columns:
            # Remove thousands separator (.) and replace decimal separator (,) with (.)
            df['costo_totale'] = (df['costo_totale']
                                  .astype(str)
                                  .str.replace('.', '', regex=False)
                                  .str.replace(',', '.', regex=False)
                                  .str.replace('€', '', regex=False)
                                  .str.strip())
            
            df['costo_totale'] = pd.to_numeric(df['costo_totale'], errors='coerce').fillna(0)
        
        return df
    
    def _clean_date_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean date columns"""
        for col in Config.DATE_COLUMNS:
            if col in df.columns:
                df[col] = (df[col]
                          .astype(str)
                          .str.replace('"', '')
                          .str.strip())
                df[col] = pd.to_datetime(df[col], dayfirst=True, errors='coerce')
        
        return df
    
    def _add_derived_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add calculated/derived columns"""
        
        # SLA Status
        if 'fuori_sla' in df.columns:
            df['is_fuori_sla'] = (df['fuori_sla']
                                  .astype(str)
                                  .str.upper()
                                  .apply(lambda x: 'Sì' if x in ['Y', 'S', 'SI', 'YES', '1', 'TRUE', 'SÌ'] else 'No'))
        else:
            df['is_fuori_sla'] = 'N/D'
        
        # Stato calcolato
        df['stato_calcolato'] = df.apply(
            lambda x: 'APERTO' if pd.isna(x.get('data_chiusura')) else 'CHIUSO',
            axis=1
        )
        
        # Durata (giorni)
        if 'data_apertura' in df.columns and 'data_chiusura' in df.columns:
            df['durata_giorni'] = (df['data_chiusura'] - df['data_apertura']).dt.days
            df['durata_giorni'] = df['durata_giorni'].where(df['durata_giorni'] >= 0, None)
        
        # Mese apertura
        if 'data_apertura' in df.columns:
            df['mese_apertura'] = df['data_apertura'].dt.to_period('M').astype(str)
            df['anno_apertura'] = df['data_apertura'].dt.year
        
        return df
    
    def _update_metadata(self, df: pd.DataFrame):
        """Update dataset metadata"""
        self.metadata = {
            'total_rows': len(df),
            'total_cost': df['costo_totale'].sum() if 'costo_totale' in df.columns else 0,
            'date_range': {
                'min': df['data_apertura'].min() if 'data_apertura' in df.columns else None,
                'max': df['data_apertura'].max() if 'data_apertura' in df.columns else None
            },
            'loaded_at': datetime.now().isoformat()
        }
    
    def export_for_powerbi(self) -> bytes:
        """Export data in Power BI compatible format"""
        if self.df is None:
            return b""
        
        return self.df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8')
    
    def get_summary_stats(self) -> Dict:
        """Get summary statistics"""
        if self.df is None:
            return {}
        
        df = self.df
        
        return {
            'total_tickets': len(df),
            'total_cost': df['costo_totale'].sum() if 'costo_totale' in df.columns else 0,
            'open_tickets': len(df[df['stato_calcolato'] == 'APERTO']) if 'stato_calcolato' in df.columns else 0,
            'closed_tickets': len(df[df['stato_calcolato'] == 'CHIUSO']) if 'stato_calcolato' in df.columns else 0,
            'out_of_sla': len(df[df['is_fuori_sla'] == 'Sì']) if 'is_fuori_sla' in df.columns else 0,
            'avg_cost': df['costo_totale'].mean() if 'costo_totale' in df.columns else 0,
            'median_cost': df['costo_totale'].median() if 'costo_totale' in df.columns else 0,
        }

# ============================================================================
# VISUALIZATION ENGINE
# ============================================================================

class VisualizationEngine:
    """Advanced visualization and dashboard components"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
    
    def render_kpi_cards(self):
        """Render modern KPI cards"""
        stats = self._calculate_kpis()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            self._render_kpi_card(
                "Spesa Totale",
                f"€ {stats['total_cost']:,.0f}",
                "💰",
                delta=None,
                help_text="Somma di tutti i costi intervento"
            )
        
        with col2:
            self._render_kpi_card(
                "Ticket Totali",
                f"{stats['total_tickets']:,}",
                "🎫",
                delta=None,
                help_text="Numero totale di RDA nel sistema"
            )
        
        with col3:
            open_pct = (stats['open_tickets'] / stats['total_tickets'] * 100) if stats['total_tickets'] > 0 else 0
            self._render_kpi_card(
                "Ticket Aperti",
                f"{stats['open_tickets']:,}",
                "📂",
                delta=f"{open_pct:.1f}%",
                help_text="RDA ancora in lavorazione"
            )
        
        with col4:
            sla_pct = (stats['out_of_sla'] / stats['total_tickets'] * 100) if stats['total_tickets'] > 0 else 0
            self._render_kpi_card(
                "Fuori SLA",
                f"{stats['out_of_sla']:,}",
                "⚠️",
                delta=f"{sla_pct:.1f}%",
                delta_color="inverse",
                help_text="Ticket che hanno superato il tempo previsto"
            )
    
    def _render_kpi_card(self, label: str, value: str, icon: str, delta=None, delta_color="normal", help_text=None):
        """Render a single KPI card"""
        st.metric(
            label=f"{icon} {label}",
            value=value,
            delta=delta,
            delta_color=delta_color,
            help=help_text
        )
    
    def _calculate_kpis(self) -> Dict:
        """Calculate KPIs from dataframe"""
        return {
            'total_cost': self.df['costo_totale'].sum() if 'costo_totale' in self.df.columns else 0,
            'total_tickets': len(self.df),
            'open_tickets': len(self.df[self.df['stato_calcolato'] == 'APERTO']) if 'stato_calcolato' in self.df.columns else 0,
            'closed_tickets': len(self.df[self.df['stato_calcolato'] == 'CHIUSO']) if 'stato_calcolato' in self.df.columns else 0,
            'out_of_sla': len(self.df[self.df['is_fuori_sla'] == 'Sì']) if 'is_fuori_sla' in self.df.columns else 0,
        }
    
    def render_main_charts(self):
        """Render main dashboard charts"""
        col1, col2 = st.columns(2)
        
        with col1:
            self._render_top_vendors_chart()
        
        with col2:
            self._render_top_points_chart()
        
        col3, col4 = st.columns(2)
        
        with col3:
            self._render_monthly_trend()
        
        with col4:
            self._render_category_distribution()
    
    def _render_top_vendors_chart(self):
        """Top vendors by cost"""
        if 'ditta' not in self.df.columns:
            st.info("Colonna 'ditta' non disponibile")
            return
        
        top_vendors = (self.df.groupby('ditta')['costo_totale']
                      .sum()
                      .nlargest(10)
                      .sort_values(ascending=True))
        
        fig = go.Figure(go.Bar(
            x=top_vendors.values,
            y=top_vendors.index,
            orientation='h',
            marker=dict(
                color=top_vendors.values,
                colorscale='Blues',
                showscale=False
            ),
            text=[f"€ {val:,.0f}" for val in top_vendors.values],
            textposition='outside'
        ))
        
        fig.update_layout(
            title="Top 10 Ditte per Spesa",
            xaxis_title="Costo Totale (€)",
            yaxis_title="",
            height=400,
            showlegend=False,
            margin=dict(l=0, r=0, t=40, b=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_top_points_chart(self):
        """Top points of sale by ticket count"""
        if 'punto_vendita' not in self.df.columns:
            st.info("Colonna 'punto_vendita' non disponibile")
            return
        
        top_points = (self.df['punto_vendita']
                     .value_counts()
                     .head(10)
                     .sort_values(ascending=True))
        
        fig = go.Figure(go.Bar(
            x=top_points.values,
            y=top_points.index,
            orientation='h',
            marker=dict(
                color=top_points.values,
                colorscale='Greens',
                showscale=False
            ),
            text=top_points.values,
            textposition='outside'
        ))
        
        fig.update_layout(
            title="Top 10 Punti Vendita per N° Ticket",
            xaxis_title="Numero Ticket",
            yaxis_title="",
            height=400,
            showlegend=False,
            margin=dict(l=0, r=0, t=40, b=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_monthly_trend(self):
        """Monthly cost trend"""
        if 'mese_apertura' not in self.df.columns:
            st.info("Dati temporali non disponibili")
            return
        
        monthly = (self.df.groupby('mese_apertura')['costo_totale']
                  .sum()
                  .reset_index()
                  .sort_values('mese_apertura'))
        
        fig = go.Figure(go.Scatter(
            x=monthly['mese_apertura'],
            y=monthly['costo_totale'],
            mode='lines+markers',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=8),
            fill='tozeroy',
            fillcolor='rgba(31, 119, 180, 0.1)'
        ))
        
        fig.update_layout(
            title="Trend Mensile Spesa",
            xaxis_title="Mese",
            yaxis_title="Costo Totale (€)",
            height=400,
            showlegend=False,
            margin=dict(l=0, r=0, t=40, b=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_category_distribution(self):
        """Category distribution pie chart"""
        if 'macrocategoria' not in self.df.columns:
            st.info("Colonna 'macrocategoria' non disponibile")
            return
        
        category_costs = (self.df.groupby('macrocategoria')['costo_totale']
                         .sum()
                         .sort_values(ascending=False)
                         .head(8))
        
        fig = go.Figure(go.Pie(
            labels=category_costs.index,
            values=category_costs.values,
            hole=0.4,
            textinfo='label+percent',
            textposition='outside'
        ))
        
        fig.update_layout(
            title="Distribuzione Spesa per Categoria",
            height=400,
            showlegend=True,
            margin=dict(l=0, r=0, t=40, b=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# AI AGENT
# ============================================================================

class AIAgent:
    """Gemini AI integration for intelligent data analysis"""
    
    def __init__(self, api_key: str):
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai non installato")
        
        genai.configure(api_key=api_key)
        
        # Get available models
        models = [m.name for m in genai.list_models() 
                 if 'generateContent' in m.supported_generation_methods]
        
        if not models:
            raise ValueError("Nessun modello Gemini disponibile")
        
        self.model_name = models[0]
        self.model = genai.GenerativeModel(
            self.model_name,
            generation_config={
                'temperature': Config.AI_TEMPERATURE,
                'max_output_tokens': Config.AI_MAX_TOKENS,
            }
        )
        
        self.conversation_history = []
    
    def analyze(self, query: str, df: pd.DataFrame) -> str:
        """
        Analyze data using AI with FULL dataset access
        
        Sends the complete dataset to Gemini (up to 2000 rows)
        Gemini 1.5 Flash has 1M token context - can handle this easily!
        """
        try:
            # Limit to max rows for safety
            df_limited = df.head(Config.MAX_ROWS_FOR_AI)
            
            # Convert entire dataframe to CSV format
            # This gives AI complete visibility into all data
            full_csv_data = df_limited.to_csv(index=False)
            
            # Build prompt with full data
            prompt = self._build_full_data_prompt(query, full_csv_data, len(df))
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            # Store in history
            self.conversation_history.append({
                'query': query,
                'response': response.text,
                'timestamp': datetime.now().isoformat()
            })
            
            return response.text
            
        except Exception as e:
            return f"❌ Errore AI: {str(e)}"
    
    def _build_full_data_prompt(self, query: str, csv_data: str, total_rows: int) -> str:
        """Build prompt with complete dataset in CSV format"""
        
        prompt = f"""Sei un Senior Data Analyst specializzato in analisi RDA (Richieste di Assistenza) per Q8 Italia.

HAI ACCESSO ALL'INTERO DATASET in formato CSV qui sotto.
Il dataset contiene {total_rows} righe totali (mostrate tutte qui sotto se ≤ 2000 righe).

DATI COMPLETI IN FORMATO CSV:
```csv
{csv_data}
```

DOMANDA UTENTE:
{query}

ISTRUZIONI:
1. Leggi TUTTI i dati CSV forniti sopra
2. Esegui i calcoli o filtri necessari per rispondere
3. Rispondi in modo preciso e professionale
4. Usa numeri e statistiche dai dati reali
5. Se devi contare, filtrare o aggregare, fallo su TUTTI i dati
6. Mantieni un tono professionale ma accessibile
7. Formatta la risposta in modo chiaro con intestazioni e punti elenco dove appropriato
8. Quando dici "X ticket fuori SLA", conta TUTTE le righe dove la colonna corrisponde

IMPORTANTE: 
- La colonna "fuori_sla" o "is_fuori_sla" contiene "Sì" o "No"
- Conta TUTTE le righe, non solo un campione
- Se chiedo "chi ha più X", devi raggruppare e contare TUTTI i dati

RISPOSTA:"""
        
        return prompt
    
    def _prepare_analysis_context(self, df: pd.DataFrame) -> Dict:
        """Prepare optimized data context for AI"""
        
        # Limit rows
        df_sample = df.head(Config.MAX_ROWS_FOR_AI)
        
        # Helper function to convert pandas values to JSON-serializable types
        def make_serializable(obj):
            if pd.isna(obj):
                return None
            elif isinstance(obj, (pd.Timestamp, datetime)):
                return str(obj)
            elif isinstance(obj, (int, float, str, bool)):
                return obj
            else:
                return str(obj)
        
        # Get date range safely
        date_min = None
        date_max = None
        if 'data_apertura' in df.columns:
            try:
                date_min = df['data_apertura'].min()
                date_max = df['data_apertura'].max()
                if pd.notna(date_min):
                    date_min = str(date_min)
                else:
                    date_min = None
                if pd.notna(date_max):
                    date_max = str(date_max)
                else:
                    date_max = None
            except:
                date_min = None
                date_max = None
        
        context = {
            'metadata': {
                'total_rows': len(df),
                'columns': list(df.columns),
                'date_range': {
                    'min': date_min,
                    'max': date_max
                }
            },
            'summary_stats': {
                'total_cost': float(df['costo_totale'].sum()) if 'costo_totale' in df.columns else 0,
                'avg_cost': float(df['costo_totale'].mean()) if 'costo_totale' in df.columns else 0,
                'median_cost': float(df['costo_totale'].median()) if 'costo_totale' in df.columns else 0,
                'open_tickets': int(len(df[df['stato_calcolato'] == 'APERTO'])) if 'stato_calcolato' in df.columns else 0,
                'closed_tickets': int(len(df[df['stato_calcolato'] == 'CHIUSO'])) if 'stato_calcolato' in df.columns else 0,
            },
            'top_vendors': {k: float(v) for k, v in df.groupby('ditta')['costo_totale'].sum().nlargest(10).to_dict().items()} if 'ditta' in df.columns else {},
            'top_points': {str(k): int(v) for k, v in df['punto_vendita'].value_counts().head(10).to_dict().items()} if 'punto_vendita' in df.columns else {},
            'sample_data': [{k: make_serializable(v) for k, v in row.items()} for row in df_sample.to_dict('records')[:50]]
        }
        
        return context
    
    def _build_analysis_prompt(self, query: str, context: Dict) -> str:
        """Build optimized prompt for AI"""
        
        prompt = f"""Sei un Senior Data Analyst specializzato in analisi RDA (Richieste di Assistenza) per Q8 Italia.

CONTESTO DATASET:
- Totale righe: {context['metadata']['total_rows']}
- Periodo: {context['metadata']['date_range']['min']} → {context['metadata']['date_range']['max']}
- Colonne disponibili: {', '.join(context['metadata']['columns'])}

STATISTICHE PRINCIPALI:
- Spesa totale: € {context['summary_stats']['total_cost']:,.2f}
- Costo medio: € {context['summary_stats']['avg_cost']:,.2f}
- Ticket aperti: {context['summary_stats']['open_tickets']}
- Ticket chiusi: {context['summary_stats']['closed_tickets']}

TOP 5 DITTE PER SPESA:
{json.dumps(dict(list(context['top_vendors'].items())[:5]), indent=2, ensure_ascii=False)}

TOP 5 PUNTI VENDITA PER N° TICKET:
{json.dumps(dict(list(context['top_points'].items())[:5]), indent=2, ensure_ascii=False)}

CAMPIONE DATI (prime 10 righe):
{json.dumps(context['sample_data'][:10], indent=2, ensure_ascii=False)}

DOMANDA UTENTE:
{query}

ISTRUZIONI:
1. Analizza i dati forniti nel contesto
2. Rispondi in modo preciso e professionale
3. Usa numeri e statistiche quando possibile
4. Se i dati non sono sufficienti per rispondere, indica cosa manca
5. Mantieni un tono professionale ma accessibile
6. Formatta la risposta in modo chiaro con intestazioni e punti elenco dove appropriato

RISPOSTA:"""
        
        return prompt
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def init_session_state():
    """Initialize session state variables"""
    if 'data_engine' not in st.session_state:
        st.session_state.data_engine = DataEngine()
    
    if 'ai_agent' not in st.session_state:
        st.session_state.ai_agent = None
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'api_key' not in st.session_state:
        st.session_state.api_key = ""


def render_sidebar():
    """Render sidebar with controls"""
    with st.sidebar:
        st.markdown("### 📁 Gestione Dati")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Carica file RDA",
            type=['csv', 'txt'],
            help="Carica il file esportato dal sistema RDA Q8"
        )
        
        if uploaded_file and st.button("🔄 Carica File", use_container_width=True):
            with st.spinner("Caricamento in corso..."):
                success, message, df = st.session_state.data_engine.load_file(uploaded_file)
                
                if success:
                    Logger.success(message)
                    st.rerun()
                else:
                    Logger.error(message)
        
        # Data info
        if st.session_state.data_engine.df is not None:
            st.divider()
            st.markdown("### 📊 Info Dataset")
            metadata = st.session_state.data_engine.metadata
            st.metric("Righe", f"{metadata.get('total_rows', 0):,}")
            st.metric("Spesa Totale", f"€ {metadata.get('total_cost', 0):,.0f}")
            
            # Export button
            st.divider()
            st.download_button(
                "📥 Esporta per Power BI",
                data=st.session_state.data_engine.export_for_powerbi(),
                file_name=f"Q8_RDA_Export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        # AI Configuration
        st.divider()
        st.markdown("### 🤖 Configurazione AI")
        
        if not GEMINI_AVAILABLE:
            st.error("google-generativeai non installato")
            st.code("pip install google-generativeai")
        else:
            api_key = st.text_input(
                "Google API Key",
                type="password",
                value=st.session_state.api_key,
                help="Inserisci la tua API key di Google Gemini"
            )
            
            if api_key != st.session_state.api_key:
                st.session_state.api_key = api_key
            
            if api_key and st.button("🔗 Connetti AI", use_container_width=True):
                if DataValidator.validate_api_key(api_key):
                    try:
                        agent = AIAgent(api_key)
                        st.session_state.ai_agent = agent
                        Logger.success(f"Connesso: {agent.model_name}")
                    except Exception as e:
                        Logger.error(f"Connessione fallita: {str(e)}")
                else:
                    Logger.error("API Key non valida")
            
            # AI Status
            if st.session_state.ai_agent:
                st.success("✅ AI Connessa")
                if st.button("🗑️ Disconnetti", use_container_width=True):
                    st.session_state.ai_agent = None
                    st.session_state.chat_history = []
                    st.rerun()
        
        # Footer
        st.divider()
        st.caption(f"v{Config.VERSION} - {Config.AUTHOR}")


def render_dashboard_tab():
    """Render main dashboard tab"""
    df = st.session_state.data_engine.df
    
    if df is None or df.empty:
        st.info("👆 Carica un file RDA per iniziare")
        return
    
    # KPIs
    viz = VisualizationEngine(df)
    viz.render_kpi_cards()
    
    st.divider()
    
    # Charts
    viz.render_main_charts()


def render_ai_tab():
    """Render AI analysis tab"""
    df = st.session_state.data_engine.df
    
    if df is None or df.empty:
        st.info("👆 Carica prima un file RDA")
        return
    
    if not st.session_state.ai_agent:
        st.warning("⚠️ Configura l'AI nella sidebar per utilizzare questa funzione")
        st.markdown("""
        ### Come configurare l'AI:
        1. Vai su [Google AI Studio](https://makersuite.google.com/app/apikey)
        2. Crea una nuova API key
        3. Incolla la key nella sidebar
        4. Clicca su "Connetti AI"
        """)
        return
    
    st.markdown("### 🧠 Analisi Intelligente con AI")
    st.info("💡 Fai qualsiasi domanda sui tuoi dati RDA. L'AI analizzerà il dataset e ti fornirà risposte dettagliate.")
    
    # Chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Es: Quali sono i punti vendita più costosi? Quali ditte hanno i tempi di intervento più lunghi?"):
        
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Analizzando i dati..."):
                response = st.session_state.ai_agent.analyze(prompt, df)
                st.markdown(response)
        
        # Add AI response to history
        st.session_state.chat_history.append({"role": "assistant", "content": response})
    
    # Clear chat button
    if st.session_state.chat_history:
        if st.button("🗑️ Pulisci Chat"):
            st.session_state.chat_history = []
            st.session_state.ai_agent.clear_history()
            st.rerun()


def render_data_tab():
    """Render raw data table tab"""
    df = st.session_state.data_engine.df
    
    if df is None or df.empty:
        st.info("👆 Carica un file RDA per visualizzare i dati")
        return
    
    st.markdown("### 📋 Dati Completi")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if 'stato_calcolato' in df.columns:
            stato_filter = st.multiselect(
                "Stato",
                options=df['stato_calcolato'].unique(),
                default=None
            )
        else:
            stato_filter = []
    
    with col2:
        if 'ditta' in df.columns:
            ditta_filter = st.multiselect(
                "Ditta",
                options=sorted(df['ditta'].unique()),
                default=None
            )
        else:
            ditta_filter = []
    
    with col3:
        if 'is_fuori_sla' in df.columns:
            sla_filter = st.multiselect(
                "SLA",
                options=df['is_fuori_sla'].unique(),
                default=None
            )
        else:
            sla_filter = []
    
    # Apply filters
    filtered_df = df.copy()
    
    if stato_filter:
        filtered_df = filtered_df[filtered_df['stato_calcolato'].isin(stato_filter)]
    
    if ditta_filter:
        filtered_df = filtered_df[filtered_df['ditta'].isin(ditta_filter)]
    
    if sla_filter:
        filtered_df = filtered_df[filtered_df['is_fuori_sla'].isin(sla_filter)]
    
    # Display
    st.dataframe(
        filtered_df,
        use_container_width=True,
        height=600,
        column_config={
            "costo_totale": st.column_config.NumberColumn(
                "Costo Totale",
                format="€ %.2f"
            ),
            "data_apertura": st.column_config.DateColumn(
                "Data Apertura",
                format="DD/MM/YYYY"
            ),
            "data_chiusura": st.column_config.DateColumn(
                "Data Chiusura",
                format="DD/MM/YYYY"
            ),
        }
    )
    
    st.caption(f"Visualizzate {len(filtered_df):,} righe di {len(df):,} totali")


def main():
    """Main application entry point"""
    
    # Page config
    st.set_page_config(
        page_title=Config.APP_TITLE,
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
        <style>
        .main > div {
            padding-top: 2rem;
        }
        .stMetric {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Initialize
    init_session_state()
    
    # Header
    st.title(f"📊 {Config.APP_TITLE}")
    st.markdown(f"*Sistema di analisi intelligente per RDA Q8 Italia - v{Config.VERSION}*")
    
    # Sidebar
    render_sidebar()
    
    # Main content
    tabs = st.tabs(["📊 Dashboard", "🧠 AI Assistant", "📋 Dati Completi"])
    
    with tabs[0]:
        render_dashboard_tab()
    
    with tabs[1]:
        render_ai_tab()
    
    with tabs[2]:
        render_data_tab()


if __name__ == "__main__":
    main()
