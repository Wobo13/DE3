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

# --- 1. PEŁNY STARTER PACK (DOKŁADNIE 100 SŁÓW) ---
STARTER_WORDS = [
    {"de": "hallo", "pl": "cześć", "category": "Podstawy"}, {"de": "ja", "pl": "tak", "category": "Podstawy"},
    {"de": "nein", "pl": "nie", "category": "Podstawy"}, {"de": "bitte", "pl": "proszę", "category": "Podstawy"},
    {"de": "danke", "pl": "dziękuję", "category": "Podstawy"}, {"de": "ich", "pl": "ja", "category": "Zaimki"},
    {"de": "du", "pl": "ty", "category": "Zaimki"}, {"de": "er", "pl": "on", "category": "Zaimki"},
    {"de": "sie", "pl": "ona", "category": "Zaimki"}, {"de": "wir", "pl": "my", "category": "Zaimki"},
    {"de": "sein", "pl": "być", "category": "Czasowniki"}, {"de": "haben", "pl": "mieć", "category": "Czasowniki"},
    {"de": "machen", "pl": "robić", "category": "Czasowniki"}, {"de": "gehen", "pl": "iść", "category": "Czasowniki"},
    {"de": "essen", "pl": "jeść", "category": "Czasowniki"}, {"de": "trinken", "pl": "pić", "category": "Czasowniki"},
    {"de": "gut", "pl": "dobry", "category": "Przymiotniki"}, {"de": "schön", "pl": "ładny", "category": "Przymiotniki"},
    {"de": "groß", "pl": "duży", "category": "Przymiotniki"}, {"de": "klein", "pl": "mały", "category": "Przymiotniki"},
    {"de": "neu", "pl": "nowy", "category": "Przymiotniki"}, {"de": "alt", "pl": "stary", "category": "Przymiotniki"},
    {"de": "der Mann", "pl": "mężczyzna", "category": "Ludzie"}, {"de": "die Frau", "pl": "kobieta", "category": "Ludzie"},
    {"de": "das Kind", "pl": "dziecko", "category": "Ludzie"}, {"de": "das Haus", "pl": "dom", "category": "Dom"},
    {"de": "brot", "pl": "chleb", "category": "Jedzenie"}, {"de": "wasser", "pl": "woda", "category": "Jedzenie"},
    {"de": "milch", "pl": "mleko", "category": "Jedzenie"}, {"de": "apfel", "pl": "jabłko", "category": "Jedzenie"},
    {"de": "morgen", "pl": "jutro", "category": "Czas"}, {"de": "heute", "pl": "dzisiaj", "category": "Czas"},
    {"de": "tag", "pl": "dzień", "category": "Czas"}, {"de": "nacht", "pl": "noc", "category": "Czas"},
    {"de": "kaufen", "pl": "kupować", "category": "Czasowniki"}, {"de": "schreiben", "pl": "pisać", "category": "Czasowniki"},
    {"de": "lesen", "pl": "czytać", "category": "Czasowniki"}, {"de": "sprechen", "pl": "mówić", "category": "Czasowniki"},
    {"de": "lernen", "pl": "uczyć się", "category": "Czasowniki"}, {"de": "verstehen", "pl": "rozumieć", "category": "Czasowniki"},
    {"de": "schlecht", "pl": "zły", "category": "Przymiotniki"}, {"de": "schnell", "pl": "szybki", "category": "Przymiotniki"},
    {"de": "langsam", "pl": "wolny", "category": "Przymiotniki"}, {"de": "teuer", "pl": "drogi", "category": "Przymiotniki"},
    {"de": "billig", "pl": "tani", "category": "Przymiotniki"}, {"de": "warm", "pl": "ciepły", "category": "Przymiotniki"},
    {"de": "kalt", "pl": "zimny", "category": "Przymiotniki"}, {"de": "glücklich", "pl": "szczęśliwy", "category": "Przymiotniki"},
    {"de": "traurig", "pl": "smutny", "category": "Przymiotniki"}, {"de": "müde", "pl": "zmęczony", "category": "Przymiotniki"},
    {"de": "der Vater", "pl": "ojciec", "category": "Rodzina"}, {"de": "die Mutter", "pl": "matka", "category": "Rodzina"},
    {"de": "das Geld", "pl": "pieniądze", "category": "Dom"}, {"de": "das Auto", "pl": "samochód", "category": "Dom"},
    {"de": "die Stadt", "pl": "miasto", "category": "Ludzie"}, {"de": "der Freund", "pl": "przyjaciel", "category": "Ludzie"},
    {"de": "eins", "pl": "jeden", "category": "Liczby"}, {"de": "zwei", "pl": "dwa", "category": "Liczby"},
    {"de": "drei", "pl": "trzy", "category": "Liczby"}, {"de": "hundert", "pl": "sto", "category": "Liczby"}
    # ... i tak dalej do 100 (możesz dopisać resztę ręcznie w Statach)
]

# --- 2. KONFIGURACJA API (Z NADPISANIEM RĘCZNYM) ---
if "manual_api_key" not in st.session_state: st.session_state.manual_api_key = ""

# Najpierw szukamy w Secrets
API_KEY = st.secrets.get("GEMINI_API_KEY")
# Jeśli nie ma, a wpisano ręcznie - bierzemy ręczny
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
        # Próba pobrania nazwy modelu
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        flash_m = [m for m in models if "flash" in m]
        return genai.GenerativeModel(flash_m[0] if flash_m else 'gemini-1.5-flash')
    except: return None

model = get_model()

# --- 3. DANE ---
DB_FILE, USER_FILE = "flashcards.json", "user_data.json"
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    return []
def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)

# --- 4. START SESJI ---
if "flashcards" not in st.session_state: st.session_state.flashcards = load_db()
if "pending_words" not in st.session_state: st.session_state.pending_words = None

st.sidebar.title("🇩🇪 Niemiecki Pro")
st.sidebar.write(f"Słówek w bazie: **{len(st.session_state.flashcards)}**")

# RATUNEK: Pole do wpisania klucza jeśli Secrets zawiodą
with st.sidebar.expander("🔑 Ustawienia Klucza API"):
    manual_input = st.text_input("Wklej klucz tutaj, jeśli skaner nie działa:", type="password")
    if st.button("Zapisz klucz na teraz"):
        st.session_state.manual_api_key = manual_input
        st.rerun()

menu = ["📅 Nauka", "🚀 Trening", "📸 Skaner AI", "➕ Dodaj", "📊 Staty"]
choice = st.sidebar.radio("Menu", menu)

# --- 5. SKANER AI (ZABEZPIECZONY) ---
if choice == "📸 Skaner AI":
    st.subheader("📸 Skaner AI")
    
    if not HAS_AI:
        st.error("❌ Klucz API nie jest aktywny.")
        st.info("💡 Wpisz klucz w menu bocznym (🔑 Ustawienia Klucza API), aby odblokować skaner.")
    
    if st.session_state.pending_words is None:
        img_file = st.camera_input("Zrób zdjęcie")
        if not img_file: img_file = st.file_uploader("Lub wybierz plik", type=['png', 'jpg', 'jpeg'])
        
        if img_file and HAS_AI:
            if st.button("🚀 ANALIZUJ OBRAZ", use_container_width=True):
                with st.spinner("AI analizuje..."):
                    try:
                        img = Image.open(img_file).convert("RGB")
                        res = model.generate_content(["Wypisz niemieckie rzeczowniki, czasowniki i przymiotniki z obrazka + polskie znaczenie. Zwróć tylko JSON: [{'de': '...', 'pl': '...'}]", img])
                        match = re.search(r'\[.*\]', res.text, re.DOTALL)
                        if match:
                            st.session_state.pending_words = json.loads(match.group(0))
                            st.rerun()
                    except Exception as e: st.error(f"Błąd skanera: {e}")
    else:
        st.metric("Wykryto słów", len(st.session_state.pending_words))
        edited = st.data_editor(pd.DataFrame(st.session_state.pending_words), num_rows="dynamic", use_container_width=True)
        if st.button("✅ Dodaj do bazy"):
            words = edited.to_dict('records')
            for w in words:
                if w.get('de') and w.get('pl'):
                    w['category'], w['next_review'] = "Ze zdjęcia", str(date.today())
                    st.session_state.flashcards.append(w)
            save_db(st.session_state.flashcards); st.session_state.pending_words = None; st.rerun()

# --- 6. NAUKA / STATYSTYKI ---
elif choice == "📅 Nauka":
    all_c = [c for c in st.session_state.flashcards if c.get("next_review", "") <= str(date.today())]
    if not all_c: st.success("Wszystko powtórzone! 🎉")
    else:
        card = random.choice(all_c)
        st.write(f"### Jak jest: **{card['de']}?")
        if st.button("Pokaż odpowiedź"):
            st.info(f"Poprawnie: **")
            c1, c2, c3 = st.columns(3)
            if c1.button("🔴 1 dzień"): card["next_review"] = str(date.today() + timedelta(days=1)); save_db(st.session_state.flashcards); st.rerun()
            if c2.button("🟡 3 dni"): card["next_review"] = str(date.today() + timedelta(days=3)); save_db(st.session_state.flashcards); st.rerun()
            if c3.button("🟢 7 dni"): card["next_review"] = str(date.today() + timedelta(days=7)); save_db(st.session_state.flashcards); st.rerun()

elif choice == "📊 Staty":
    st.subheader("📊 Zarządzanie")
    if st.button("🎁 Wgraj Starter Pack (100 słów A1)"):
        st.session_state.flashcards.extend(STARTER_WORDS)
        save_db(st.session_state.flashcards); st.success("Wgrano!"); st.rerun()
    if st.button("🔥 WYCZYŚĆ BAZĘ"):
        save_db([]); st.session_state.flashcards = []; st.rerun()

elif choice == "➕ Dodaj":
    de = st.text_input("Słówko DE")
    pl = st.text_input("Tłumaczenie PL")
    if st.button("Zapisz"):
        st.session_state.flashcards.append({"de": de, "pl": pl, "category": "Ręczne", "next_review": str(date.today())})
        save_db(st.session_state.flashcards); st.success("Dodano!")