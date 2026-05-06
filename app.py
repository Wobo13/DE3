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

# --- 1. KOMPLETNY STARTER PACK (DOKŁADNIE 100 SŁÓW A1) ---
STARTER_WORDS = [
    {"de": "hallo", "pl": "cześć", "category": "Podstawy"}, {"de": "ja", "pl": "tak", "category": "Podstawy"},
    {"de": "nein", "pl": "nie", "category": "Podstawy"}, {"de": "bitte", "pl": "proszę", "category": "Podstawy"},
    {"de": "danke", "pl": "dziękuję", "category": "Podstawy"}, {"de": "entschuldigung", "pl": "przepraszam", "category": "Podstawy"},
    {"de": "ich", "pl": "ja", "category": "Zaimki"}, {"de": "du", "pl": "ty", "category": "Zaimki"},
    {"de": "er", "pl": "on", "category": "Zaimki"}, {"de": "sie", "pl": "ona / oni", "category": "Zaimki"},
    {"de": "es", "pl": "ono", "category": "Zaimki"}, {"de": "wir", "pl": "my", "category": "Zaimki"},
    {"de": "ihr", "pl": "wy", "category": "Zaimki"}, {"de": "sein", "pl": "być", "category": "Czasowniki"},
    {"de": "haben", "pl": "mieć", "category": "Czasowniki"}, {"de": "machen", "pl": "robić", "category": "Czasowniki"},
    {"de": "gehen", "pl": "iść", "category": "Czasowniki"}, {"de": "kommen", "pl": "przychodzić", "category": "Czasowniki"},
    {"de": "essen", "pl": "jeść", "category": "Czasowniki"}, {"de": "trinken", "pl": "pić", "category": "Czasowniki"},
    {"de": "gut", "pl": "dobry", "category": "Przymiotniki"}, {"de": "schön", "pl": "ładny", "category": "Przymiotniki"},
    {"de": "groß", "pl": "duży", "category": "Przymiotniki"}, {"de": "klein", "pl": "mały", "category": "Przymiotniki"},
    {"de": "der Mann", "pl": "mężczyzna", "category": "Ludzie"}, {"de": "die Frau", "pl": "kobieta", "category": "Ludzie"},
    {"de": "das Kind", "pl": "dziecko", "category": "Ludzie"}, {"de": "das Haus", "pl": "dom", "category": "Dom"},
    {"de": "eins", "pl": "jeden", "category": "Liczby"}, {"de": "zwei", "pl": "dwa", "category": "Liczby"},
    {"de": "drei", "pl": "trzy", "category": "Liczby"}, {"de": "vier", "pl": "cztery", "category": "Liczby"},
    {"de": "fünf", "pl": "pięć", "category": "Liczby"}, {"de": "sechs", "pl": "sześć", "category": "Liczby"},
    {"de": "sieben", "pl": "siedem", "category": "Liczby"}, {"de": "acht", "pl": "osiem", "category": "Liczby"},
    {"de": "neun", "pl": "dziewięć", "category": "Liczby"}, {"de": "zehn", "pl": "dziesięć", "category": "Liczby"},
    {"de": "der Vater", "pl": "ojciec", "category": "Rodzina"}, {"de": "die Mutter", "pl": "matka", "category": "Rodzina"},
    {"de": "der Bruder", "pl": "brat", "category": "Rodzina"}, {"de": "die Schwester", "pl": "siostra", "category": "Rodzina"},
    {"de": "das Brot", "pl": "chleb", "category": "Jedzenie"}, {"de": "das Wasser", "pl": "woda", "category": "Jedzenie"},
    {"de": "der Kaffee", "pl": "kawa", "category": "Jedzenie"}, {"de": "die Milch", "pl": "mleko", "category": "Jedzenie"},
    {"de": "neu", "pl": "nowy", "category": "Przymiotniki"}, {"de": "alt", "pl": "stary", "category": "Przymiotniki"},
    {"de": "teuer", "pl": "drogi", "category": "Przymiotniki"}, {"de": "billig", "pl": "tani", "category": "Przymiotniki"},
    {"de": "schlafen", "pl": "spać", "category": "Czasowniki"}, {"de": "lernen", "pl": "uczyć się", "category": "Czasowniki"},
    {"de": "sprechen", "pl": "mówić", "category": "Czasowniki"}, {"de": "schreiben", "pl": "pisać", "category": "Czasowniki"},
    {"de": "lesen", "pl": "czytać", "category": "Czasowniki"}, {"de": "kaufen", "pl": "kupować", "category": "Czasowniki"},
    {"de": "der Tisch", "pl": "stół", "category": "Dom"}, {"de": "der Stuhl", "pl": "krzesło", "category": "Dom"},
    {"de": "das Bett", "pl": "łóżko", "category": "Dom"}, {"de": "das Fenster", "pl": "okno", "category": "Dom"},
    {"de": "heute", "pl": "dzisiaj", "category": "Czas"}, {"de": "morgen", "pl": "jutro", "category": "Czas"},
    {"de": "der Tag", "pl": "dzień", "category": "Czas"}, {"de": "die Nacht", "pl": "noc", "category": "Czas"},
    {"de": "langsam", "pl": "wolno", "category": "Przymiotniki"}, {"de": "schnell", "pl": "szybko", "category": "Przymiotniki"},
    {"de": "warm", "pl": "ciepło", "category": "Przymiotniki"}, {"de": "kalt", "pl": "zimno", "category": "Przymiotniki"},
    {"de": "hell", "pl": "jasno", "category": "Przymiotniki"}, {"de": "dunkel", "pl": "ciemno", "category": "Przymiotniki"},
    {"de": "glücklich", "pl": "szczęśliwy", "category": "Przymiotniki"}, {"de": "traurig", "pl": "smutny", "category": "Przymiotniki"},
    {"de": "fertig", "pl": "gotowy", "category": "Przymiotniki"}, {"de": "krank", "pl": "chory", "category": "Przymiotniki"},
    {"de": "der Name", "pl": "imię / nazwisko", "category": "Ludzie"}, {"de": "das Geld", "pl": "pieniądze", "category": "Dom"},
    {"de": "die Stadt", "pl": "miasto", "category": "Miejsca"}, {"de": "das Dorf", "pl": "wieś", "category": "Miejsca"},
    {"de": "das Auto", "pl": "samochód", "category": "Miejsca"}, {"de": "der Bus", "pl": "autobus", "category": "Miejsca"},
    {"de": "hören", "pl": "słyszeć", "category": "Czasowniki"}, {"de": "sehen", "pl": "widzieć", "category": "Czasowniki"},
    {"de": "warten", "pl": "czekać", "category": "Czasowniki"}, {"de": "suchen", "pl": "szukać", "category": "Czasowniki"},
    {"de": "finden", "pl": "znaleźć", "category": "Czasowniki"}, {"de": "geben", "pl": "dawać", "category": "Czasowniki"},
    {"de": "helfen", "pl": "pomagać", "category": "Czasowniki"}, {"de": "verstehen", "pl": "rozumieć", "category": "Czasowniki"},
    {"de": "wissen", "pl": "wiedzieć", "category": "Czasowniki"}, {"de": "denken", "pl": "myśleć", "category": "Czasowniki"},
    {"de": "die Zeit", "pl": "czas", "category": "Czas"}, {"de": "das Jahr", "pl": "rok", "category": "Czas"},
    {"de": "die Woche", "pl": "tydzień", "category": "Czas"}, {"de": "der Monat", "pl": "miesiąc", "category": "Czas"},
    {"de": "immer", "pl": "zawsze", "category": "Czas"}, {"de": "nie", "pl": "nigdy", "category": "Czas"},
    {"de": "oft", "pl": "często", "category": "Czas"}, {"de": "zusammen", "pl": "razem", "category": "Podstawy"},
    {"de": "allein", "pl": "samemu", "category": "Podstawy"}, {"de": "vielleicht", "pl": "może", "category": "Podstawy"}
]

# --- 2. KONFIGURACJA I API ---
PRICE_IN_1M, PRICE_OUT_1M = 0.30, 1.20
BONUS_START = 1089.0
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

def track_cost(response):
    try:
        if hasattr(response, 'usage_metadata'):
            in_t, out_t = response.usage_metadata.prompt_token_count, response.usage_metadata.candidates_token_count
            cost = (in_t * (PRICE_IN_1M/1e6)) + (out_t * (PRICE_OUT_1M/1e6))
            st.session_state.total_session_cost += cost
    except: pass

# --- 3. DANE ---
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    return []
def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)
def load_user():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r", encoding="utf-8") as f:
            d = json.load(f)
            if "historical_cost" not in d: d["historical_cost"] = 0.0
            return d
    return {"streak": 0, "daily_count": 0, "daily_goal": 10, "historical_cost": 0.0}
def save_user(data):
    with open(USER_FILE, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)

# --- 4. FUNKCJE POMOCNICZE ---
def play_audio(text):
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang='de')
        f = BytesIO(); tts.write_to_fp(f)
        st.audio(f, format="audio/mp3", autoplay=True)
    except: pass

def is_correct(u_ans, corr_ans):
    u, c = u_ans.strip().lower(), corr_ans.strip().lower()
    if u == c: return True
    repls = [("ä","ae"),("ö","oe"),("ü","ue"),("ß","ss"),("ä","a"),("ö","o"),("ü","u")]
    for o, n in repls:
        if u == c.replace(o, n): return True
    return False

# --- 5. INIT SESJI ---
if "flashcards" not in st.session_state: st.session_state.flashcards = load_db()
if "user_data" not in st.session_state: st.session_state.user_data = load_user()
if "total_session_cost" not in st.session_state: st.session_state.total_session_cost = 0.0
if "pending_words" not in st.session_state: st.session_state.pending_words = None
if "last_kat" not in st.session_state: st.session_state.last_kat = "Wszystkie"

st.sidebar.title("🇩🇪 Niemiecki Master")
with st.sidebar.expander("🔑 Ustawienia Klucza AI"):
    m_key = st.text_input("Klucz:", type="password", value=st.session_state.manual_api_key)
    if st.button("Zastosuj"): 
        st.session_state.manual_api_key = m_key
        st.rerun()

menu = ["📅 Nauka", "🚀 Trening", "📸 Skaner AI", "➕ Dodaj", "📖 Słownik", "📊 Statystyki"]
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
                        prompt = "Podaj niemieckie słówka z obrazka (rzeczowniki z rodzajnikiem, czasowniki w bezokoliczniku, przymiotniki). NIE podawaj całych zdań. Podaj polskie znaczenie. Wynik TYLKO JSON: [{'de': 'rodzajnik słowo', 'pl': 'tłumaczenie'}]"
                        res = model.generate_content([prompt, img])
                        track_cost(res)
                        match = re.search(r'\[.*\]', res.text, re.DOTALL)
                        if match:
                            st.session_state.pending_words = json.loads(match.group(0))
                            st.rerun()
                        else: st.error("Nie znaleziono słówek. Spróbuj innego ujęcia.")
                    except Exception as e: st.error(f"Błąd: {e}")
    else:
        st.metric("Wykryto słów", len(st.session_state.pending_words))
        edited = st.data_editor(pd.DataFrame(st.session_state.pending_words), num_rows="dynamic", use_container_width=True)
        c1, c2 = st.columns(2)
        if c1.button("✅ Dodaj do bazy"):
            for w in edited.to_dict('records'):
                if w.get('de') and w.get('pl'):
                    w['category'], w['next_review'] = "Ze zdjęcia", str(date.today())
                    st.session_state.flashcards.append(w)
            save_db(st.session_state.flashcards); st.session_state.pending_words = None; st.rerun()
        if c2.button("🗑️ Anuluj"): st.session_state.pending_words = None; st.rerun()

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
            st.session_state.cur_card, st.session_state.dir, st.session_state.mode = random.choice(cards), random.choice(["de_to_pl", "pl_to_de"]), "ask"
        card = st.session_state.cur_card
        q = card['de'] if st.session_state.dir == "de_to_pl" else card['pl']
        ans = card['pl'] if st.session_state.dir == "de_to_pl" else card['de']
        st.write(f"### Przetłumacz: **{q}**")
        if st.session_state.mode == "ask":
            with st.form("quiz"):
                u_in = st.text_input("Twoja odpowiedź:", key=f"in_{card['de']}")
                if st.form_submit_button("Sprawdź"):
                    st.session_state.u_ans, st.session_state.mode = u_in, "res"; st.rerun()
        else:
            if is_correct(st.session_state.u_ans, ans): st.success(f"✅ Dobrze! -> {ans}")
            else: st.error(f"❌ Poprawnie: {ans}")
            play_audio(card['de'])
            if st.button("🔊 Powtórz wymowę"): play_audio(card['de'])
            st.write("---")
            if "ai_sentence" not in st.session_state and HAS_AI:
                try:
                    res = model.generate_content(f"Napisz proste zdanie A1 z '{card['de']}'. Format: DE: [zdanie] | PL: [tłumaczenie]")
                    track_cost(res)
                    st.session_state.ai_raw = st.session_state.ai_sentence = res.text
                except: st.session_state.ai_sentence = "AI odpoczywa..."
            if "ai_sentence" in st.session_state:
                st.info(st.session_state.ai_sentence)
                if st.button("💾 Zapisz zdanie"):
                    try:
                        raw = st.session_state.ai_raw
                        de_s = raw.split("DE:")[1].split("PL:")[0].strip().strip("|").strip()
                        pl_s = raw.split("PL:")[1].strip().strip("|").strip()
                        st.session_state.flashcards.append({"de": de_s, "pl": pl_s, "category": "Zdania AI", "next_review": str(date.today())})
                        save_db(st.session_state.flashcards); st.toast("Zapisano!")
                    except: st.error("Błąd zapisu.")
            st.write("---")
            c1, c2, c3 = st.columns(3)
            def next_s(days):
                if choice == "📅 Nauka": card["next_review"] = str(date.today() + timedelta(days=days))
                st.session_state.user_data["historical_cost"] += st.session_state.total_session_cost
                st.session_state.total_session_cost = 0.0
                save_user(st.session_state.user_data); save_db(st.session_state.flashcards)
                for k in ["cur_card", "mode", "u_ans", "ai_sentence", "ai_raw"]: 
                    if k in st.session_state: del st.session_state[k]
                st.rerun()
            if c1.button("🔴 Słabo (1d)"): next_s(1)
            if c2.button("🟡 Średnio (3d)"): next_s(3)
            if c3.button("🟢 Świetnie (7d)"): next_s(7)

elif choice == "📊 Statystyki":
    st.subheader("📊 Statystyki i Zarządzanie")
    spent = st.session_state.user_data.get('historical_cost', 0.0) + st.session_state.total_session_cost
    st.metric("Pozostały bonus AI", f"{BONUS_START - spent:.4f} PLN")
    st.write(f"Słówek w bazie: **{len(st.session_state.flashcards)}**")
    if st.button("🎁 Wgraj Pełny Starter Pack (100 słów)"):
        st.session_state.flashcards.extend(STARTER_WORDS)
        save_db(st.session_state.flashcards); st.success("Wgrano 100 słów!"); st.rerun()
    if st.button("🔥 WYCZYŚĆ BAZĘ"):
        save_db([]); st.session_state.flashcards = []; st.rerun()

elif choice == "📖 Słownik":
    sch = st.text_input("🔍 Szukaj:")
    for i, c in enumerate(st.session_state.flashcards):
        if sch.lower() in c['de'].lower():
            c1, c2, col3 = st.columns([3,3,1])
            c1.write(c['de']); c2.write(c['pl'])
            if col3.button("🗑️", key=f"d_{i}"):
                st.session_state.flashcards.pop(i); save_db(st.session_state.flashcards); st.rerun()

elif choice == "➕ Dodaj":
    de, pl = st.text_input("DE"), st.text_input("PL")
    if st.button("Zapisz"):
        st.session_state.flashcards.append({"de": de, "pl": pl, "category": "Ręczne", "next_review": str(date.today())})
        save_db(st.session_state.flashcards); st.success("Zapisano!")