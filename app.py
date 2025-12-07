import streamlit as st
import pandas as pd
import requests
import asyncio
import edge_tts
from gtts import gTTS
import nest_asyncio
import random
import os

# Fix for asyncio loops
nest_asyncio.apply()

# --- Page Config ---
st.set_page_config(
    page_title="Aria Library AI Hub",
    layout="wide",
    page_icon="🐨",
    initial_sidebar_state="expanded"
)

# --- THEME CONFIGURATION ---
themes = {
    "Ocean 🌊 (Default)": {
        "bg_gradient": "linear-gradient(135deg, #264653 0%, #2a9d8f 100%)",
        "btn_grad": "linear-gradient(90deg, #264653 0%, #2a9d8f 100%)",
        "sidebar_bg": "#eef6f9",
        "card_bg": "#ffffff",
        "text_primary": "#2c3e50",
        "text_secondary": "#e76f51",
        "accent": "#2a9d8f",
        "border": "#b2dfdb"
    },
    "Midnight 🌑 (Dark)": {
        "bg_gradient": "linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%)",
        "btn_grad": "linear-gradient(90deg, #4db6ac 0%, #80cbc4 100%)",
        "sidebar_bg": "#121212",
        "card_bg": "#1e1e1e",
        "text_primary": "#e0e0e0",
        "text_secondary": "#4db6ac",
        "accent": "#80cbc4",
        "border": "#333333"
    },
    "Vintage 📜": {
        "bg_gradient": "linear-gradient(135deg, #8e44ad 0%, #c0392b 100%)",
        "btn_grad": "linear-gradient(90deg, #d7c08e 0%, #bcaaa4 100%)",
        "sidebar_bg": "#f4e4bc",
        "card_bg": "#fffbf0",
        "text_primary": "#5d4037",
        "text_secondary": "#8d6e63",
        "accent": "#a1887f",
        "border": "#d7c08e"
    },
    "Cyberpunk 🤖": {
        "bg_gradient": "linear-gradient(135deg, #2b003e 0%, #000000 100%)",
        "btn_grad": "linear-gradient(90deg, #ff0099 0%, #493240 100%)",
        "sidebar_bg": "#0b0c15",
        "card_bg": "#1a1a2e",
        "text_primary": "#ffffff",
        "text_secondary": "#00f3ff",
        "accent": "#ff0099",
        "border": "#ff0099"
    },
    "Classic 🏛️": {
        "bg_gradient": "linear-gradient(135deg, #2c3e50 0%, #4ca1af 100%)",
        "btn_grad": "linear-gradient(90deg, #2c3e50 0%, #34495e 100%)",
        "sidebar_bg": "#ffffff",
        "card_bg": "#ffffff",
        "text_primary": "#2c3e50",
        "text_secondary": "#7f8c8d",
        "accent": "#2980b9",
        "border": "#bdc3c7"
    },
    "Forest 🌲": {
        "bg_gradient": "linear-gradient(135deg, #134e5e 0%, #71b280 100%)",
        "btn_grad": "linear-gradient(90deg, #11998e 0%, #38ef7d 100%)",
        "sidebar_bg": "#e8f5e9",
        "card_bg": "#ffffff",
        "text_primary": "#2e7d32",
        "text_secondary": "#558b2f",
        "accent": "#2e7d32",
        "border": "#a5d6a7"
    },
    "Royal 👑": {
        "bg_gradient": "linear-gradient(135deg, #4b134f 0%, #c94b4b 100%)",
        "btn_grad": "linear-gradient(90deg, #8e24aa 0%, #ab47bc 100%)",
        "sidebar_bg": "#f3e5f5",
        "card_bg": "#ffffff",
        "text_primary": "#4a148c",
        "text_secondary": "#7b1fa2",
        "accent": "#8e24aa",
        "border": "#e1bee7"
    },
    "Sunset 🌅": {
        "bg_gradient": "linear-gradient(135deg, #ff512f 0%, #dd2476 100%)",
        "btn_grad": "linear-gradient(90deg, #ff512f 0%, #f09819 100%)",
        "sidebar_bg": "#fff3e0",
        "card_bg": "#ffffff",
        "text_primary": "#bf360c",
        "text_secondary": "#f57c00",
        "accent": "#ff6f00",
        "border": "#ffcc80"
    }
}

# Theme Init
if 'current_theme' not in st.session_state:
    st.session_state.current_theme = "Ocean 🌊 (Default)"

# --- SIDEBAR & STYLING ---
st.sidebar.markdown("### 🎨 Theme Settings")
selected_theme_name = st.sidebar.selectbox("Select Theme:", list(themes.keys()), index=0)
st.session_state.current_theme = selected_theme_name
c = themes[st.session_state.current_theme]

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Poppins', sans-serif;
        color: {c['text_primary']};
    }}
    
    /* BACKGROUND */
    .stApp {{ background-color: {c.get('sidebar_bg', '#fff')} !important; }}

    /* HEADER - EXTREME 3D */
    .main-header {{
        background: {c['bg_gradient']};
        padding: 3rem; border-radius: 30px; color: white; margin-bottom: 2.5rem;
        /* Multiple strong shadows for depth */
        box-shadow: 0 20px 50px -10px rgba(0,0,0,0.5), inset 0 2px 5px rgba(255,255,255,0.2); 
        text-align: center; 
        border: 3px solid rgba(255,255,255,0.15);
    }}
    .main-header h1 {{ font-weight: 800; text-shadow: 0 5px 10px rgba(0,0,0,0.4); font-size: 3rem; }}

    /* SIDEBAR */
    section[data-testid="stSidebar"] {{
        background-color: {c['sidebar_bg']};
        border-right: 2px solid {c['border']};
        box-shadow: 5px 0 15px rgba(0,0,0,0.05);
    }}

    /* --- BOLD INPUTS (Sunken Look) --- */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] {{
        background-color: {c['card_bg']} !important;
        border: 3px solid {c['border']} !important; /* Thicker border */
        border-radius: 15px !important;
        color: {c['text_primary']} !important;
        font-weight: 700;
        /* Deep inner shadow */
        box-shadow: inset 3px 3px 8px rgba(0,0,0,0.1), inset -2px -2px 5px rgba(255,255,255,0.5) !important;
        height: 55px;
    }}
    .stTextInput input:focus, .stSelectbox div[data-baseweb="select"]:focus-within {{
        border-color: {c['accent']} !important;
        box-shadow: 0 0 0 4px {c['accent']}33, inset 2px 2px 5px rgba(0,0,0,0.1) !important;
    }}

    /* --- 3D RADIO BUTTONS (Voice & Menu) --- */
    .stRadio > div {{ gap: 12px; }}
    
    /* Unchecked State (Raised) */
    .stRadio label {{
        background-color: {c['card_bg']};
        border: 3px solid {c['border']};
        border-radius: 15px;
        padding: 18px 22px;
        color: {c['text_primary']};
        font-weight: 700;
        cursor: pointer;
        transition: all 0.25s cubic-bezier(0.175, 0.885, 0.32, 1.275); /* Bouncy transition */
        box-shadow: 0 8px 15px rgba(0,0,0,0.1), 0 3px 5px rgba(0,0,0,0.05); /* Significant lift */
        display: flex; width: 100%;
    }}
    
    /* Checked State (Pressed/Popped) */
    .stRadio label:has(div[aria-checked="true"]) {{
        background: {c['btn_grad']} !important;
        color: white !important;
        border-color: transparent;
        transform: translateY(-4px) scale(1.02); /* Higher lift */
        box-shadow: 0 15px 35px rgba(0,0,0,0.3); /* Huge shadow */
    }}
    .stRadio label:hover {{
        transform: translateY(-2px);
        border-color: {c['accent']};
        box-shadow: 0 10px 20px rgba(0,0,0,0.15);
    }}
    .stRadio div[role="radiogroup"] > label > div:first-child {{ display: none; }}

    /* --- CARDS (High Lift) --- */
    .book-card, .small-book-card {{
        background: {c['card_bg']};
        border-radius: 20px;
        padding: 20px;
        border: 3px solid {c['border']};
        /* Strong base shadow */
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        display: flex; flex-direction: column; justify-content: space-between;
        height: 100%; min-height: 250px;
    }}
    .book-card:hover, .small-book-card:hover {{
        transform: translateY(-10px) scale(1.03);
        /* Very strong hover shadow */
        box-shadow: 0 25px 50px rgba(0,0,0,0.25);
        border-color: {c['accent']};
        z-index: 10;
    }}

    /* --- BUTTONS (Physical Clicky Feel) --- */
    .stButton > button {{
        background: {c['btn_grad']} !important;
        color: white !important;
        font-weight: 800;
        border-radius: 15px;
        height: 55px;
        border: none;
        /* Chunky shadow + inset highlight + bottom border for thickness */
        box-shadow: 0 8px 20px rgba(0,0,0,0.25), inset 0 2px 5px rgba(255,255,255,0.3);
        border-bottom: 5px solid rgba(0,0,0,0.2); 
        transition: all 0.2s;
        width: 100%;
        letter-spacing: 0.5px;
    }}
    .stButton > button:hover {{
        transform: translateY(-4px);
        box-shadow: 0 12px 30px rgba(0,0,0,0.35), inset 0 2px 5px rgba(255,255,255,0.3);
    }}
    .stButton > button:active {{
        transform: translateY(2px); /* Physical press down */
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        border-bottom-width: 2px;
    }}

    /* TEXT FIXES */
    .book-title, .small-title {{ color: {c['text_primary']} !important; font-weight: 800; margin-top: 12px; font-size: 1.05rem; }}
    .book-author, .small-author {{ color: {c['text_secondary']} !important; font-weight: 700; }}
    p, span, div, h1, h2, h3 {{ color: {c['text_primary']}; }}
    
    /* CHAT BUBBLE */
    .chat-bubble {{
        background: {c['card_bg']}; padding: 25px; border-radius: 25px;
        border-left: 8px solid {c['accent']};
        box-shadow: 5px 5px 20px rgba(0,0,0,0.15); /* Deeper shadow */
        border: 2px solid {c['border']};
        font-size: 1.15rem; font-weight: 600;
    }}
</style>
""", unsafe_allow_html=True)

# --- DATA GENERATION (200 BOOKS) ---
if 'favorites' not in st.session_state:
    st.session_state.favorites = []

def get_top_200_books():
    base_list = [
        ("Cloudstreet", "Tim Winton", "Classic"), ("The Book Thief", "Markus Zusak", "Classic"),
        ("My Brilliant Career", "Miles Franklin", "Classic"), ("The Harp in the South", "Ruth Park", "Classic"),
        ("Picnic at Hanging Rock", "Joan Lindsay", "Mystery"), ("Power Without Glory", "Frank Hardy", "Classic"),
        ("The Chant of Jimmie Blacksmith", "Thomas Keneally", "Classic"), ("Schindler's Ark", "Thomas Keneally", "Classic"),
        ("Oscar and Lucinda", "Peter Carey", "Classic"), ("True History of the Kelly Gang", "Peter Carey", "Classic"),
        ("Jack Maggs", "Peter Carey", "Historical"), ("The Secret River", "Kate Grenville", "Historical"),
        ("The Lieutenant", "Kate Grenville", "Historical"), ("Sarah Thornhill", "Kate Grenville", "Historical"),
        ("The Thorn Birds", "Colleen McCullough", "Classic"), ("A Fortunate Life", "A.B. Facey", "Biography"),
        ("They're a Weird Mob", "Nino Culotta", "Humor"), ("Poor Man's Orange", "Ruth Park", "Classic"),
        ("Seven Little Australians", "Ethel Turner", "Kids Classic"), ("The Magic Pudding", "Norman Lindsay", "Kids Classic"),
        ("Snugglepot and Cuddlepie", "May Gibbs", "Kids Classic"), ("Blinky Bill", "Dorothy Wall", "Kids Classic"),
        ("Boy Swallows Universe", "Trent Dalton", "Fiction"), ("Lola in the Mirror", "Trent Dalton", "Fiction"),
        ("All Our Shimmering Skies", "Trent Dalton", "Fiction"), ("Big Little Lies", "Liane Moriarty", "Thriller"),
        ("The Husband's Secret", "Liane Moriarty", "Thriller"), ("Nine Perfect Strangers", "Liane Moriarty", "Thriller"),
        ("Apples Never Fall", "Liane Moriarty", "Thriller"), ("Here One Moment", "Liane Moriarty", "New Release"),
        ("The Dry", "Jane Harper", "Crime"), ("Force of Nature", "Jane Harper", "Crime"),
        ("The Lost Man", "Jane Harper", "Crime"), ("The Survivors", "Jane Harper", "Crime"),
        ("Exiles", "Jane Harper", "Crime"), ("The Slap", "Christos Tsiolkas", "Fiction"),
        ("Barracuda", "Christos Tsiolkas", "Fiction"), ("Damascus", "Christos Tsiolkas", "Fiction"),
        ("Breath", "Tim Winton", "Coming of Age"), ("Dirt Music", "Tim Winton", "Literary"),
        ("The Shepherd's Hut", "Tim Winton", "Fiction"), ("Juice", "Tim Winton", "Sci-Fi"),
        ("Shantaram", "Gregory David Roberts", "Fiction"), ("The Rosie Project", "Graeme Simsion", "Rom-Com"),
        ("The Rosie Effect", "Graeme Simsion", "Rom-Com"), ("The Light Between Oceans", "M.L. Stedman", "Fiction"),
        ("The Dressmaker", "Rosalie Ham", "Fiction"), ("Jasper Jones", "Craig Silvey", "YA"),
        ("Honeybee", "Craig Silvey", "Fiction"), ("Runt", "Craig Silvey", "Kids"),
        ("Scrublands", "Chris Hammer", "Crime"), ("Silver", "Chris Hammer", "Crime"),
        ("Trust", "Chris Hammer", "Crime"), ("The Valley", "Chris Hammer", "Crime"),
        ("Bodies of Light", "Jennifer Down", "Fiction"), ("Cold Enough for Snow", "Jessica Au", "Fiction"),
        ("The White Girl", "Tony Birch", "Fiction"), ("Too Much Lip", "Melissa Lucashenko", "Fiction"),
        ("The Yield", "Tara June Winch", "Fiction"), ("Bila Yarrudhanggalangdhuray", "Anita Heiss", "Historical"),
        ("Bruny", "Heather Rose", "Thriller"), ("Love & Virtue", "Diana Reid", "Fiction"),
        ("Seeing Other People", "Diana Reid", "Fiction"), ("Everyone In My Family Has Killed Someone", "Benjamin Stevenson", "Mystery"),
        ("The Barefoot Investor", "Scott Pape", "Finance"), ("RecipeTin Eats: Dinner", "Nagi Maehashi", "Cooking"),
        ("RecipeTin Eats: Tonight", "Nagi Maehashi", "Cooking"), ("Dark Emu", "Bruce Pascoe", "History"),
        ("Sand Talk", "Tyson Yunkaporta", "Philosophy"), ("Growing Up Aboriginal in Australia", "Anita Heiss", "Anthology"),
        ("Mao's Last Dancer", "Li Cunxin", "Biography"), ("The Happiest Man on Earth", "Eddie Jaku", "Biography"),
        ("Tracks", "Robyn Davidson", "Travel"), ("Any Ordinary Day", "Leigh Sales", "Non-Fiction"),
        ("Eggshell Skull", "Bri Lee", "Memoir"), ("Working Class Boy", "Jimmy Barnes", "Memoir"),
        ("Working Class Man", "Jimmy Barnes", "Memoir"), ("Reckoning", "Magda Szubanski", "Memoir"),
        ("My Place", "Sally Morgan", "Biography"), ("Follow the Rabbit-Proof Fence", "Doris Pilkington", "Biography"),
        ("No Friend But the Mountains", "Behrouz Boochani", "Memoir"), ("Phosphorescence", "Julia Baird", "Self-Help"),
        ("The Trauma Cleaner", "Sarah Krasnostein", "Biography"), ("Woman of Substances", "Jenny Valentish", "Memoir"),
        ("Possum Magic", "Mem Fox", "Kids"), ("Where is the Green Sheep?", "Mem Fox", "Kids"),
        ("Ten Little Fingers and Ten Little Toes", "Mem Fox", "Kids"), ("Wombat Stew", "Marcia K. Vaughan", "Kids"),
        ("Diary of a Wombat", "Jackie French", "Kids"), ("Hitler's Daughter", "Jackie French", "Kids"),
        ("Magic Beach", "Alison Lester", "Kids"), ("Are We There Yet?", "Alison Lester", "Kids"),
        ("Animalia", "Graeme Base", "Kids"), ("The 13-Storey Treehouse", "Andy Griffiths", "Kids"),
        ("The 26-Storey Treehouse", "Andy Griffiths", "Kids"), ("The 169-Storey Treehouse", "Andy Griffiths", "Kids"),
        ("The Bad Guys", "Aaron Blabey", "Kids"), ("Pig the Pug", "Aaron Blabey", "Kids"),
        ("WeirDo", "Anh Do", "Kids"), ("Wolf Girl", "Anh Do", "Kids"),
        ("Bluey: The Beach", "Ludo Studio", "Kids"), ("Bluey: Goodnight Fruit Bat", "Ludo Studio", "Kids"),
        ("Looking for Alibrandi", "Melina Marchetta", "YA"), ("Saving Francesca", "Melina Marchetta", "YA"),
        ("On the Jellicoe Road", "Melina Marchetta", "YA"), ("Tomorrow, When the War Began", "John Marsden", "YA"),
        ("The Dead of the Night", "John Marsden", "YA"), ("Obernewtyn", "Isobelle Carmody", "Fantasy"),
        ("Deltora Quest", "Emily Rodda", "Fantasy"), ("Rowan of Rin", "Emily Rodda", "Fantasy"),
        ("It Ends with Us", "Colleen Hoover", "Romance"), ("It Starts with Us", "Colleen Hoover", "Romance"),
        ("Verity", "Colleen Hoover", "Thriller"), ("Where the Crawdads Sing", "Delia Owens", "Fiction"),
        ("The Seven Husbands of Evelyn Hugo", "Taylor Jenkins Reid", "Fiction"), ("Daisy Jones & The Six", "Taylor Jenkins Reid", "Fiction"),
        ("Lessons in Chemistry", "Bonnie Garmus", "Fiction"), ("The Thursday Murder Club", "Richard Osman", "Mystery"),
        ("The Man Who Died Twice", "Richard Osman", "Mystery"), ("Normal People", "Sally Rooney", "Fiction"),
        ("Conversations with Friends", "Sally Rooney", "Fiction"), ("Beautiful World, Where Are You", "Sally Rooney", "Fiction"),
        ("A Court of Thorns and Roses", "Sarah J. Maas", "Fantasy"), ("Throne of Glass", "Sarah J. Maas", "Fantasy"),
        ("Fourth Wing", "Rebecca Yarros", "Fantasy"), ("Iron Flame", "Rebecca Yarros", "Fantasy"),
        ("Atomic Habits", "James Clear", "Self-Help"), ("Sapiens", "Yuval Noah Harari", "History"),
        ("Becoming", "Michelle Obama", "Biography"), ("Spare", "Prince Harry", "Biography"),
        ("The Da Vinci Code", "Dan Brown", "Thriller"), ("Harry Potter and the Philosopher's Stone", "J.K. Rowling", "Fantasy"),
        ("The Hunger Games", "Suzanne Collins", "YA"), ("Twilight", "Stephenie Meyer", "YA"),
        ("The Alchemist", "Paulo Coelho", "Fiction"), ("1984", "George Orwell", "Classic"),
        ("To Kill a Mockingbird", "Harper Lee", "Classic"), ("Pride and Prejudice", "Jane Austen", "Classic"),
        ("The Great Gatsby", "F. Scott Fitzgerald", "Classic"), ("The Catcher in the Rye", "J.D. Salinger", "Classic"),
        ("Lord of the Flies", "William Golding", "Classic"), ("Little Women", "Louisa May Alcott", "Classic"),
        ("Dune", "Frank Herbert", "Sci-Fi"), ("The Hobbit", "J.R.R. Tolkien", "Fantasy"),
        ("A Game of Thrones", "George R.R. Martin", "Fantasy"), ("The Handmaid's Tale", "Margaret Atwood", "Dystopian"),
        ("The Testaments", "Margaret Atwood", "Dystopian"), ("Klara and the Sun", "Kazuo Ishiguro", "Fiction"),
        ("Never Let Me Go", "Kazuo Ishiguro", "Fiction"), ("Norwegian Wood", "Haruki Murakami", "Fiction"),
        ("Kafka on the Shore", "Haruki Murakami", "Fiction"), ("1Q84", "Haruki Murakami", "Fiction"),
        ("Before the Coffee Gets Cold", "Toshikazu Kawaguchi", "Fiction"), ("Yellowface", "R.F. Kuang", "Satire"),
        ("Babel", "R.F. Kuang", "Fantasy"), ("Tomorrow, and Tomorrow, and Tomorrow", "Gabrielle Zevin", "Fiction"),
        ("Demon Copperhead", "Barbara Kingsolver", "Fiction"), ("Trust", "Hernan Diaz", "Fiction"),
        ("The Midnight Library", "Matt Haig", "Fiction"), ("Eleanor Oliphant is Completely Fine", "Gail Honeyman", "Fiction"),
        ("Gone Girl", "Gillian Flynn", "Thriller"), ("The Girl on the Train", "Paula Hawkins", "Thriller"),
        ("Bridgerton: The Duke and I", "Julia Quinn", "Romance"), ("Outlander", "Diana Gabaldon", "Historical"),
        ("The Tattooist of Auschwitz", "Heather Morris", "Historical"), ("Cilka's Journey", "Heather Morris", "Historical"),
        ("Thinking, Fast and Slow", "Daniel Kahneman", "Psychology"), ("Educated", "Tara Westover", "Memoir"),
        ("Born a Crime", "Trevor Noah", "Memoir"), ("Greenlights", "Matthew McConaughey", "Memoir"),
        ("The Body Keeps the Score", "Bessel van der Kolk", "Psychology"), ("Why We Sleep", "Matthew Walker", "Health"),
        ("Breath", "James Nestor", "Health"), ("I'm Glad My Mom Died", "Jennette McCurdy", "Memoir"),
        ("Friends, Lovers, and the Big Terrible Thing", "Matthew Perry", "Memoir"), ("Elon Musk", "Walter Isaacson", "Biography"),
        ("Steve Jobs", "Walter Isaacson", "Biography"), ("Project Hail Mary", "Andy Weir", "Sci-Fi"),
        ("The Martian", "Andy Weir", "Sci-Fi"), ("Dark Matter", "Blake Crouch", "Sci-Fi"),
        ("Ready Player One", "Ernest Cline", "Sci-Fi"), ("Ender's Game", "Orson Scott Card", "Sci-Fi"),
        ("Foundation", "Isaac Asimov", "Sci-Fi"), ("Fahrenheit 451", "Ray Bradbury", "Classic"),
        ("Brave New World", "Aldous Huxley", "Classic"), ("Animal Farm", "George Orwell", "Classic"),
        ("The Giver", "Lois Lowry", "YA"), ("The Fault in Our Stars", "John Green", "YA"),
        ("Paper Towns", "John Green", "YA"), ("Wonder", "R.J. Palacio", "Kids"),
        ("The Boy in the Striped Pyjamas", "John Boyne", "Historical"), ("Life of Pi", "Yann Martel", "Fiction"),
        ("The Kite Runner", "Khaled Hosseini", "Fiction"), ("A Thousand Splendid Suns", "Khaled Hosseini", "Fiction"),
        ("The God of Small Things", "Arundhati Roy", "Fiction"), ("Midnight's Children", "Salman Rushdie", "Fiction"),
        ("Interpreter of Maladies", "Jhumpa Lahiri", "Fiction"), ("Homegoing", "Yaa Gyasi", "Historical"),
        ("Girl, Woman, Other", "Bernardine Evaristo", "Fiction"), ("Americanah", "Chimamanda Ngozi Adichie", "Fiction")
    ]
    base_list = list(set(base_list))
    base_list.sort(key=lambda x: x[0])
    full_data = []
    for title, author, genre in base_list:
        full_data.append({
            "title": title, "author": author, "genre": genre,
            "search_link": f"https://www.google.com/search?q={title}+{author}+book"
        })
    return full_data

if 'top_books_db' not in st.session_state:
    st.session_state.top_books_db = get_top_200_books()

# --- HALL OF FAME ---
if 'hall_of_fame' not in st.session_state:
    st.session_state.hall_of_fame = sorted([
        "Tim Winton", "Richard Flanagan", "Liane Moriarty", "Markus Zusak", "Jane Harper",
        "Helen Garner", "Trent Dalton", "Christos Tsiolkas", "Kate Grenville", "Thomas Keneally",
        "Bryce Courtenay", "Gerald Murnane", "Charlotte Wood", "Alexis Wright", "Patrick White",
        "Peter Carey", "Colleen McCullough", "Banjo Paterson", "Henry Lawson", "Les Murray", 
        "Judith Wright", "Oodgeroo Noonuccal", "Dorothea Mackellar", "Kenneth Slessor", 
        "Gough Whitlam", "Robert Menzies", "John Curtin", "Bob Hawke", "Julia Gillard",
        "Paul Keating", "Edith Cowan", "Neville Bonner", "Kevin Rudd", "John Howard",
        "Eddie Mabo", "Charles Perkins", "Faith Bandler", "William Cooper", "Lowitja O'Donoghue",
        "Bob Brown", "Germaine Greer", "Grace Tame", "Julian Assange", "Colleen Hoover", 
        "Taylor Jenkins Reid", "Bonnie Garmus", "Richard Osman", "Sally Rooney", "Sarah J. Maas", 
        "Haruki Murakami", "Stephen King", "J.K. Rowling", "Steve Irwin", "Ned Kelly", 
        "Cathy Freeman", "Sir Donald Bradman", "Kylie Minogue", "Hugh Jackman", "Cate Blanchett", 
        "Nicole Kidman", "Heath Ledger", "Margot Robbie", "Chris Hemsworth", "Sia", "AC/DC"
    ])

# --- BACKEND FUNCTIONS ---
def add_to_favorites(book_item):
    if not any(b['title'] == book_item['title'] for b in st.session_state.favorites):
        st.session_state.favorites.append(book_item)
        st.toast(f"✅ Saved!", icon="❤️")
    else:
        st.toast("⚠️ Already Saved", icon="ℹ️")

def remove_from_favorites(book_title):
    st.session_state.favorites = [b for b in st.session_state.favorites if b['title'] != book_title]
    st.rerun()

@st.cache_data
def search_google_books_api(query):
    # FALLBACK LOGIC TO FIX EMPTY RESULTS
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    # 1. Try Newest first (Likely to fail on general terms but good for new books)
    try:
        url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=20&orderBy=newest&langRestrict=en"
        response = requests.get(url, headers=headers, timeout=8)
        data = response.json()
        if 'items' in data:
            return parse_google_data(data)
    except:
        pass # If fails, move to step 2

    # 2. Fallback: Relevance Search (More robust)
    try:
        url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=40&langRestrict=en"
        response = requests.get(url, headers=headers, timeout=8)
        data = response.json()
        if 'items' in data:
            return parse_google_data(data)
    except:
        pass
        
    return []

def parse_google_data(data):
    books = []
    for item in data.get('items', []):
        v = item.get('volumeInfo', {})
        img = v.get('imageLinks', {}).get('thumbnail', '')
        desc = v.get('description', 'No description available.')
        book_entry = {
            "title": v.get('title', 'Unknown Title'),
            "author": ", ".join(v.get('authors', ['Unknown'])),
            "year": v.get('publishedDate', '')[:4],
            "desc": desc,
            "image": img,
            "link": v.get('infoLink', '#')
        }
        books.append(book_entry)
    return books

def get_wiki_bio(name):
    headers = {'User-Agent': 'AriaLibBot/5.0'}
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{name.replace(' ', '_')}"
        data = requests.get(url, headers=headers).json()
        if 'title' in data:
            return {
                "title": data['title'],
                "summary": data.get('extract', 'No summary available.'),
                "image": data.get('thumbnail', {}).get('source'),
                "url": data.get('content_urls', {}).get('desktop', {}).get('page')
            }
    except:
        return None
    return None

# --- AUDIO SYSTEM ---
async def edge_tts_save(text, voice, filename):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(filename)

def get_audio(text, gender):
    voice = "en-AU-WilliamNeural" if gender == "Male" else "en-AU-NatashaNeural"
    filename = "temp_audio.mp3"
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(edge_tts_save(text, voice, filename))
        return filename
    except:
        try:
            tts = gTTS(text=text, lang='en', tld='com.au')
            tts.save(filename)
            return filename
        except:
            return None

# --- UI LAYOUT ---

# Sidebar Navigation (3D Styled)
st.sidebar.markdown("### 🏛️ Main Menu")
nav = st.sidebar.radio("", 
    ["🏆 Top 200 Books", "🔍 Global Search", "❤️ Favorites", "🌟 Hall of Fame", "🗣️ Practice Chat"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.metric(label="Saved Books", value=len(st.session_state.favorites), delta=None)

# Main Header
st.markdown("""
<div class="main-header">
    <h1>🐨 Aria Library AI Hub</h1>
    <p>Discover Australian Literature | Interact with AI</p>
</div>
""", unsafe_allow_html=True)

# === TAB 1: TOP 200 LIST ===
if nav == "🏆 Top 200 Books":
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("🇦🇺 Essential Australian Reading")
    with col2:
        filter_genre = st.selectbox("Filter Genre", ["All", "Fiction", "Non-Fiction", "Classic", "Kids", "YA", "Crime", "Historical"])
    
    display_list = st.session_state.top_books_db
    if filter_genre != "All":
        if filter_genre == "Non-Fiction":
            display_list = [b for b in display_list if b['genre'] in ["Cooking", "Finance", "Biography", "Memoir", "History", "Non-Fiction", "Philosophy", "Travel", "Self-Help", "Psychology", "Health"]]
        else:
            display_list = [b for b in display_list if b['genre'] == filter_genre]
            
    cols = st.columns(6) 
    for idx, book in enumerate(display_list):
        with cols[idx % 6]:
            st.markdown(f"""
            <div class="small-book-card">
                <span class="small-badge">{book['genre']}</span>
                <div>
                    <h5 class="small-title">{book['title']}</h5>
                    <p class="small-author">{book['author']}</p>
                </div>
                <div style="margin-top:auto;">
                   <a href="{book['search_link']}" target="_blank" style="text-decoration:none; font-size:0.75rem; color:{c['text_secondary']}; font-weight:600;">🔎 Verify</a>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("➕ Add", key=f"top_{idx}", help="Add to Favorites", use_container_width=True):
                add_to_favorites(book)
            st.write("") 

# === TAB 2: SEARCH ===
elif nav == "🔍 Global Search":
    st.subheader("🌍 Google Books Search")
    st.caption("Searching live global archives. (Sorted by relevance/recency)")
    
    with st.form("search_form"):
        col_s1, col_s2 = st.columns([4, 1])
        with col_s1:
            query = st.text_input("Title, Author, or ISBN", placeholder="e.g. Tim Winton")
        with col_s2:
            st.write("") 
            st.write("") 
            submitted = st.form_submit_button("🔎 Search")
            
    if submitted and query:
        with st.spinner("Connecting to global library network..."):
            st.session_state.search_results = search_google_books_api(query)
            
    if 'search_results' in st.session_state and st.session_state.search_results:
        grid_cols = st.columns(4)
        for idx, book in enumerate(st.session_state.search_results):
            with grid_cols[idx % 4]:
                cover_img = book['image'] if book['image'] else "https://via.placeholder.com/150x220?text=No+Cover"
                st.markdown(f"""
                <div class="book-card">
                    <div>
                        <img src="{cover_img}" class="book-cover-img">
                        <h5 class="book-title">{book['title'][:50]}...</h5>
                        <p class="book-author">{book['author'][:30]}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                c_btn1, c_btn2 = st.columns(2)
                with c_btn1:
                    if st.button("❤️ Save", key=f"search_{idx}", help="Save", use_container_width=True):
                        add_to_favorites(book)
                with c_btn2:
                    with st.popover("📖 Info"):
                        st.subheader(book['title'])
                        st.write(book['desc'])
                        st.markdown(f"[View on Google]({book['link']})")
    elif submitted:
        st.warning("No results found. Try a broader term.")

# === TAB 3: FAVORITES ===
elif nav == "❤️ Favorites":
    st.subheader("📚 My Reading List")
    if not st.session_state.favorites:
        st.info("List is empty! Add books from Top 200 or Search.")
    else:
        if st.button("🗑️ Clear All", type="primary"):
            st.session_state.favorites = []
            st.rerun()
        for fav in st.session_state.favorites:
            with st.container():
                c1, c2 = st.columns([5, 1])
                with c1:
                    st.markdown(f"**{fav['title']}** - {fav['author']}")
                with c2:
                    if st.button("❌ Remove", key=f"del_{fav['title']}"):
                        remove_from_favorites(fav['title'])
            st.divider()

# === TAB 4: HALL OF FAME ===
elif nav == "🌟 Hall of Fame":
    st.subheader("🌟 Australian Icons")
    col_sel, col_disp = st.columns([1, 2])
    with col_sel:
        name = st.selectbox("Select Personality:", st.session_state.hall_of_fame)
        if st.button("Load Biography", type="primary", use_container_width=True):
            with st.spinner("Fetching info..."):
                st.session_state.wiki_bio = get_wiki_bio(name)
    with col_disp:
        if 'wiki_bio' in st.session_state and st.session_state.wiki_bio:
            bio = st.session_state.wiki_bio
            st.markdown(f"""
            <div class="book-card" style="display:flex; gap:20px; align-items:start; flex-direction:row;">
                <img src="{bio['image']}" style="width:120px; height:120px; object-fit:cover; border-radius:50%; border:4px solid {c['accent']}; flex-shrink:0; box-shadow: 0 5px 15px rgba(0,0,0,0.2);">
                <div>
                    <h2 style="color:{c['text_primary']}; margin-top:0;">{bio['title']}</h2>
                    <p style="color:{c['text_primary']};">{bio['summary']}</p>
                    <a href="{bio['url']}" target="_blank" style="color:{c['accent']}; font-weight:bold;">Read Full Article</a>
                </div>
            </div>
            """, unsafe_allow_html=True)

# === TAB 5: CHAT ===
elif nav == "🗣️ Practice Chat":
    st.subheader("💬 Patron Roleplay")
    col_set, col_play = st.columns([1, 2])
    with col_set:
        st.markdown("**Voice Selection:**")
        gender = st.radio("", ["Female", "Male"], horizontal=True, label_visibility="collapsed")
        st.write("")
        if st.button("🎲 New Customer", type="primary", use_container_width=True):
            book = random.choice(st.session_state.top_books_db)
            g_code = "Female" if gender == "Female" else "Male"
            templates = [
                f"Hi! Do you have '{book['title']}'? I heard it's great.",
                f"I'm looking for '{book['title']}' by {book['author']}.",
                f"Can you help me find the section for {book['genre']} books?"
            ]
            st.session_state.chat_text = random.choice(templates)
            st.session_state.chat_audio_file = get_audio(st.session_state.chat_text, g_code)
            st.rerun()
    with col_play:
        if 'chat_text' in st.session_state:
            st.markdown(f"<div class='chat-bubble'><b>Patron:</b> {st.session_state.chat_text}</div>", unsafe_allow_html=True)
            if st.session_state.get('chat_audio_file'):
                st.audio(st.session_state.chat_audio_file, format='audio/mp3')
