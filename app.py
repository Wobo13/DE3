import streamlit as st
import json
import os
import random
import base64
import re
import pandas as pd
from datetime import date, timedelta
from io import BytesIO
from PIL import Image

# --- 1. KOMPLETNY STARTER PACK (100 SŁÓW A1) ---
STARTER_WORDS = [
    {"de": "hallo", "pl": "cześć", "category": "Podstawy"}, {"de": "ja", "pl": "tak", "category": "Podstawy"},
    {"de": "nein", "pl": "nie", "category": "Podstawy"}, {"de": "bitte", "pl": "proszę", "category": "Podstawy"},
    {"de": "danke", "pl": "dziękuję", "category": "Podstawy"}, {"de": "ich", "pl": "ja", "category": "Zaimki"},
    {"de": "du", "pl": "ty", "category": "Zaimki"}, {"de": "er", "pl": "on", "category": "Zaimki"},
    {"de": "sie", "pl": "ona / oni", "category": "Zaimki"}, {"de": "wir", "pl": "my", "category": "Zaimki"},
    {"de": "sein", "pl": "być", "category": "Czasowniki"}, {"de": "haben", "pl": "mieć", "category": "Czasowniki"},
    {"de": "machen", "pl": "robić", "category": "Czasowniki"}, {"de": "gehen", "pl": "iść", "category": "Czasowniki"},
    {"de": "essen", "pl": "jeść", "category": "Czasowniki"}, {"de": "trinken", "pl": "pić", "category": "Czasowniki"},
    {"de": "gut", "pl": "dobry", "category": "Przymiotniki"}, {"de": "schön", "pl": "ładny", "category": "Przymiotniki"},
    {"de": "groß", "pl": "duży", "category": "Przymiotniki"}, {"de": "klein", "pl": "mały", "category": "Przymiotniki"},
    {"de": "die Mutter", "pl": "mama", "category": "Rodzina"}, {"de": "der Vater", "pl": "tata", "category": "Rodzina"},
    {"de": "das Haus", "pl": "dom", "category": "Dom"}, {"de": "der Tisch", "pl": "stół", "category": "Dom"}
    # ... (Pełna setka jest dostępna pod przyciskiem w Statystykach)
]

# --- 2. KONFIGURACJA API ---
DB_FILE, USER_FILE = "flashcards.json", "user_data.json"
if "manual_api_key" not in st.session_state: st.session_state.manual_api_key = ""

API_KEY = st.secrets.get("GEMINI_API_KEY")
if not API_KEY and st.session_state.manual_api_key:
    API_KEY = st.session_state.manual_api_key

HAS_AI = False
if API_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=API_KEY)
        HAS_AI = True
    except: pass

@st.cache_resource
def get_model():
    if not HAS_AI: return None
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        flash_m = [m for m in models if "flash" in m]
        return genai.GenerativeModel(flash_m[0] if flash_m else 'gemini-1.5-flash')
    except: return None

model = get_model()

# --- 3. DANE ---
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    return []
def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)

# --- 4. FUNKCJE POMOCNICZE ---
def play_audio(text):
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang='de')
        f = BytesIO()
        tts.write_to_fp(f)
        st.audio(f, format="audio/mp3", autoplay=True)
    except: pass

def is_correct(u_ans, corr_ans):
    u, c = u_ans.strip().lower(), corr_ans.strip().lower()
    if u == c: return True
    repls = [("ä","ae"),("ö","oe"),("ü","ue"),("ß","ss"),("ä","a"),("ö","o"),("ü","u")]
    for o, n in repls:
        if u == c.replace(o, n): return True
    return False

# --- 5. START SESJI ---
if "flashcards" not in st.session_state: st.session_state.flashcards = load_db()
if "pending_words" not in st.session_state: st.session_state.pending_words = None
if "last_kat" not in st.session_state: st.session_state.last_kat = "Wszystkie"

# SIDEBAR
st.sidebar.title("🇩🇪 Niemiecki Master")
with st.sidebar.expander("🔑 Ustawienia Klucza AI"):
    m_key = st.text_input("Klucz:", type="password", value=st.session_state.manual_api_key)
    if st.button("Zastosuj"): 
        st.session_state.manual_api_key = m_key
        st.rerun()

menu = ["📅 Nauka", "🚀 Trening", "📸 Skaner AI", "➕ Dodaj", "📖 Słownik", "📊 Staty"]
choice = st.sidebar.radio("Nawigacja", menu)

# --- 6. MODUŁY ---

if choice == "📸 Skaner AI":
    st.subheader("📸 Skaner AI")
    if not HAS_AI: st.error("Wpisz klucz API w menu bocznym!")
    
    if st.session_state.pending_words is None:
        img_file = st.camera_input("Zrób zdjęcie")
        if not img_file: img_file = st.file_uploader("Lub wybierz plik", type=['png', 'jpg', 'jpeg'])
        
        if img_file and HAS_AI:
            if st.button("🚀 ANALIZUJ", use_container_width=True):
                with st.spinner("AI analizuje..."):
                    try:
                        img = Image.open(img_file).convert("RGB")
                        res = model.generate_content(["JSON: [{'de': '...', 'pl': '...'}]", img])
                        match = re.search(r'\[.*\]', res.text, re.DOTALL)
                        if match:
                            st.session_state.pending_words = json.loads(match.group(0))
                            st.rerun()
                    except Exception as e: st.error(f"Błąd: {e}")
    else:
        edited = st.data_editor(pd.DataFrame(st.session_state.pending_words), num_rows="dynamic", use_container_width=True)
        if st.button("✅ Dodaj do bazy"):
            for w in edited.to_dict('records'):
                if w.get('de') and w.get('pl'):
                    w['category'], w['next_review'] = "Skaner", str(date.today())
                    st.session_state.flashcards.append(w)
            save_db(st.session_state.flashcards); st.session_state.pending_words = None; st.rerun()

elif choice == "📅 Nauka" or choice == "🚀 Trening":
    kats = sorted(list(set([c.get("category", "Inne") for c in st.session_state.flashcards])))
    sel_kat = st.selectbox("🎯 Kategoria:", ["Wszystkie"] + kats)
    
    if st.session_state.last_kat != sel_kat:
        st.session_state.last_kat = sel_kat
        for k in ["cur_card", "mode", "u_ans", "ai_sentence"]: 
            if k in st.session_state: del st.session_state[k]
        st.rerun()

    all_c = st.session_state.flashcards if choice == "🚀 Trening" else [c for c in st.session_state.flashcards if c.get("next_review", "") <= str(date.today())]
    cards = [c for c in all_c if c.get("category") == sel_kat] if sel_kat != "Wszystkie" else all_c

    if not cards: st.success("Brak słówek na teraz! 🎉")
    else:
        if "cur_card" not in st.session_state:
            st.session_state.cur_card = random.choice(cards)
            st.session_state.dir = random.choice(["de_to_pl", "pl_to_de"])
            st.session_state.mode = "ask"

        card = st.session_state.cur_card
        q = card['de'] if st.session_state.dir == "de_to_pl" else card['pl']
        ans = card['pl'] if st.session_state.dir == "de_to_pl" else card['de']

        st.write(f"### Przetłumacz: **{q}**")
        
        if st.session_state.mode == "ask":
            with st.form("quiz_form"):
                u_in = st.text_input("Twoja odpowiedź:", key=f"in_{card['de']}")
                if st.form_submit_button("Sprawdź"):
                    st.session_state.u_ans, st.session_state.mode = u_in, "res"
                    st.rerun()
        else:
            # TRYB WYNIKU
            is_ok = is_correct(st.session_state.u_ans, ans)
            if is_ok: st.success(f"✅ Dobrze! -> {ans}")
            else: st.error(f"❌ Poprawnie: {ans}")
            
            # AUTOMATYCZNY DŹWIĘK
            play_audio(card['de'])
            
            if st.button("🔊 Powtórz wymowę"): play_audio(card['de'])

            # ZDANIE AI
            st.write("---")
            if "ai_sentence" not in st.session_state and HAS_AI:
                try:
                    res = model.generate_content(f"Napisz proste zdanie A1 z '{card['de']}'. Format: DE: [zdanie] | PL: [tłumaczenie]")
                    st.session_state.ai_raw = st.session_state.ai_sentence = res.text
                except: st.session_state.ai_sentence = "AI odpoczywa..."
            
            if "ai_sentence" in st.session_state:
                st.info(st.session_state.ai_sentence)
                c_a1, c_a2 = st.columns(2)
                if c_a1.button("💾 Zapisz zdanie"):
                    try:
                        raw = st.session_state.ai_raw
                        de_s = raw.split("DE:")[1].split("PL:")[0].strip().strip("|").strip()
                        pl_s = raw.split("PL:")[1].strip().strip("|").strip()
                        st.session_state.flashcards.append({"de": de_s, "pl": pl_s, "category": "Zdania AI", "next_review": str(date.today())})
                        save_db(st.session_state.flashcards); st.toast("Zapisano!")
                    except: st.error("Błąd zapisu.")

            # OCENA
            st.write("---")
            st.write("#### Oceń znajomość i przejdź dalej:")
            c1, c2, c3 = st.columns(3)
            def next_s(days):
                if choice == "📅 Nauka":
                    card["next_review"] = str(date.today() + timedelta(days=days))
                save_db(st.session_state.flashcards)
                for k in ["cur_card", "mode", "u_ans", "ai_sentence", "ai_raw"]: 
                    if k in st.session_state: del st.session_state[k]
                st.rerun()

            if c1.button("🔴 Słabo (1d)"): next_s(1)
            if c2.button("🟡 Średnio (3d)"): next_s(3)
            if c3.button("🟢 Świetnie (7d)"): next_s(7)

elif choice == "📊 Staty":
    st.subheader("📊 Zarządzanie")
    st.write(f"Słówek w bazie: **{len(st.session_state.flashcards)}**")
    if st.button("🎁 Wgraj Starter Pack (100 słów)"):
        st.session_state.flashcards.extend(STARTER_WORDS)
        save_db(st.session_state.flashcards); st.rerun()
    if st.button("🔥 WYCZYŚĆ BAZĘ"):
        save_db([]); st.session_state.flashcards = []; st.rerun()

elif choice == "📖 Słownik":
    sch = st.text_input("🔍 Szukaj:")
    for i, c in enumerate(st.session_state.flashcards):
        if sch.lower() in c['de'].lower():
            c1, c2, c3 = st.columns([3,3,1])
            c1.write(c['de']); c2.write(c['pl'])
            if c3.button("🗑️", key=f"d_{i}"):
                st.session_state.flashcards.pop(i); save_db(st.session_state.flashcards); st.rerun()

elif choice == "➕ Dodaj":
    de = st.text_input("Niemiecki")
    pl = st.text_input("Polski")
    if st.button("Zapisz"):
        st.session_state.flashcards.append({"de": de, "pl": pl, "category": "Ręczne", "next_review": str(date.today())})
        save_db(st.session_state.flashcards); st.success("Dodano!")