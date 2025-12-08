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

    /* HEADER */
    .main-header {{
        background: {c['bg_gradient']};
        padding: 3rem; border-radius: 30px; color: white; margin-bottom: 2.5rem;
        box-shadow: 0 15px 40px rgba(0,0,0,0.3); 
        text-align: center; 
        border: 2px solid rgba(255,255,255,0.1);
    }}
    .main-header h1 {{ font-weight: 800; text-shadow: 0 4px 8px rgba(0,0,0,0.3); font-size: 2.8rem; }}

    /* SIDEBAR */
    section[data-testid="stSidebar"] {{
        background-color: {c['sidebar_bg']};
        border-right: 2px solid {c['border']};
    }}

    /* --- INPUTS --- */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] {{
        background-color: {c['card_bg']} !important;
        border: 2px solid {c['border']} !important;
        border-radius: 12px !important;
        color: {c['text_primary']} !important;
        font-weight: 600;
        padding: 10px 15px !important; 
        min-height: 45px; 
        box-shadow: inset 2px 2px 5px rgba(0,0,0,0.05) !important;
    }}
    .stTextInput input:focus {{
        border-color: {c['accent']} !important;
        box-shadow: 0 0 0 3px {c['accent']}33 !important;
    }}

    /* --- RADIO BUTTONS --- */
    .stRadio > div {{ gap: 10px; }}
    .stRadio label {{
        background-color: {c['card_bg']};
        border: 2px solid {c['border']};
        border-radius: 12px;
        padding: 12px 15px;
        color: {c['text_primary']};
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        display: flex; width: 100%;
    }}
    .stRadio label:has(div[aria-checked="true"]) {{
        background: {c['btn_grad']} !important;
        color: white !important;
        border-color: transparent;
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }}
    .stRadio div[role="radiogroup"] > label > div:first-child {{ display: none; }}

    /* --- CARDS --- */
    .book-card, .small-book-card {{
        background: {c['card_bg']};
        border-radius: 16px;
        padding: 15px;
        border: 2px solid {c['border']};
        box-shadow: 0 6px 15px rgba(0,0,0,0.08);
        transition: all 0.3s;
        display: flex; flex-direction: column; justify-content: space-between;
        height: 100%; min-height: 280px; 
    }}
    .book-card:hover, .small-book-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.15);
        border-color: {c['accent']};
    }}

    /* --- BUTTONS --- */
    .stButton > button {{
        background: {c['btn_grad']} !important;
        color: white !important;
        font-weight: 700;
        border-radius: 12px;
        height: 48px;
        border: none;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        transition: 0.2s;
        width: 100%;
    }}
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.3);
    }}

    /* TEXT FIXES */
    .book-title, .small-title {{ color: {c['text_primary']} !important; font-weight: 700; margin-top: 10px; font-size: 1rem; }}
    .book-author, .small-author {{ color: {c['text_secondary']} !important; font-weight: 600; font-size: 0.85rem; }}
    .book-year, .history-year {{ color: {c['accent']} !important; font-weight: 800; font-size: 0.9rem; margin-top: 5px; }}
    p, span, div, h1, h2, h3 {{ color: {c['text_primary']}; }}
    
    /* CHAT BUBBLE */
    .chat-bubble {{
        background: {c['card_bg']}; padding: 20px; border-radius: 20px;
        border-left: 6px solid {c['accent']};
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        border: 1px solid {c['border']};
        font-size: 1.1rem;
    }}
</style>
""", unsafe_allow_html=True)

# --- 1. DATA GENERATION (200 BOOKS) ---
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

# --- 2. EXPANDED HALL OF FAME DATA ---
def get_hall_of_fame_data():
    return {
        "Writers & Poets ✍️": [
            "Tim Winton", "Patrick White", "Banjo Paterson", "Henry Lawson", 
            "Miles Franklin", "Oodgeroo Noonuccal", "Judith Wright", "Les Murray", 
            "Peter Carey", "Helen Garner", "Liane Moriarty", "Markus Zusak", 
            "Christos Tsiolkas", "Kate Grenville", "Richard Flanagan", "Bryce Courtenay",
            "Thomas Keneally", "Colleen McCullough", "Germaine Greer", "Dorothea Mackellar",
            "Kenneth Slessor", "Gwen Harwood", "David Malouf", "Alexis Wright", "Trent Dalton"
        ],
        "Prime Ministers & Politicians 🏛️": [
            "Sir Edmund Barton", "Alfred Deakin", "Andrew Fisher", "Billy Hughes",
            "John Curtin", "Ben Chifley", "Robert Menzies", "Harold Holt", 
            "Gough Whitlam", "Malcolm Fraser", "Bob Hawke", "Paul Keating", 
            "John Howard", "Kevin Rudd", "Julia Gillard", "Tony Abbott", 
            "Malcolm Turnbull", "Scott Morrison", "Anthony Albanese", "Edith Cowan", "Neville Bonner"
        ],
        "Activists & Indigenous Leaders ✊": [
            "Eddie Mabo", "Vincent Lingiari", "Charles Perkins", "Lowitja O'Donoghue", 
            "Faith Bandler", "William Cooper", "Truganini", "Bennelong", "Pemulwuy",
            "Doug Nicholls", "Adam Goodes", "Grace Tame", "Bob Brown"
        ],
        "Scientists & Innovators 🔬": [
            "Howard Florey", "Elizabeth Blackburn", "Peter Doherty", "Barry Marshall", 
            "Robin Warren", "Fiona Wood", "Fred Hollows", "Victor Chang", 
            "Douglas Mawson", "David Unaipon", "Karl Kruszelnicki"
        ],
        "Arts, Music & Entertainment 🎭": [
            "Cate Blanchett", "Nicole Kidman", "Hugh Jackman", "Heath Ledger", 
            "Margot Robbie", "Kylie Minogue", "Nick Cave", "Sia", "AC/DC", 
            "INXS", "Cold Chisel", "Paul Hogan", "Baz Luhrmann", "George Miller",
            "Dame Edna Everage", "Steve Irwin", "Crocodile Dundee"
        ],
        "Sports Legends 🏆": [
            "Sir Donald Bradman", "Cathy Freeman", "Dawn Fraser", "Rod Laver", 
            "Margaret Court", "Ian Thorpe", "Shane Warne", "Ricky Ponting", 
            "Ash Barty", "Sam Kerr", "Greg Norman", "Cadel Evans"
        ]
    }

# --- 3. COMPREHENSIVE HISTORY TIMELINE ---
def get_history_timeline():
    return [
        {"year": "65,000+ Years Ago", "title": "Indigenous Stewardship", "desc": "Aboriginal and Torres Strait Islander peoples live on the continent, establishing the world's oldest continuous living culture.", "link": "https://en.wikipedia.org/wiki/History_of_Indigenous_Australians"},
        {"year": "1606", "title": "European Discovery", "desc": "Dutch navigator Willem Janszoon lands on the western side of Cape York. It is the first recorded European landing.", "link": "https://en.wikipedia.org/wiki/Willem_Janszoon"},
        {"year": "1770", "title": "Cook Claims the East Coast", "desc": "James Cook maps the East Coast and claims it for Britain at Possession Island, naming it New South Wales.", "link": "https://en.wikipedia.org/wiki/James_Cook"},
        {"year": "1788", "title": "Foundation of New South Wales", "desc": "The First Fleet arrives at Sydney Cove. Captain Arthur Phillip establishes the penal colony of NSW.", "link": "https://en.wikipedia.org/wiki/History_of_New_South_Wales"},
        {"year": "1803", "title": "Settlement of Tasmania", "desc": "British settlement begins in Van Diemen's Land (Tasmania) to prevent French claims.", "link": "https://en.wikipedia.org/wiki/History_of_Tasmania"},
        {"year": "1824", "title": "Settlement of Queensland", "desc": "A penal colony is established at Moreton Bay (Brisbane), beginning the colonization of Queensland.", "link": "https://en.wikipedia.org/wiki/History_of_Queensland"},
        {"year": "1829", "title": "Foundation of Western Australia", "desc": "The Swan River Colony (Perth) is founded as a free settlement, establishing Western Australia.", "link": "https://en.wikipedia.org/wiki/History_of_Western_Australia"},
        {"year": "1835", "title": "Foundation of Victoria", "desc": "John Batman signs a treaty (later voided) to settle Port Phillip District (Melbourne).", "link": "https://en.wikipedia.org/wiki/History_of_Victoria"},
        {"year": "1836", "title": "Foundation of South Australia", "desc": "South Australia is proclaimed as a free province (no convicts) at Glenelg, Adelaide.", "link": "https://en.wikipedia.org/wiki/History_of_South_Australia"},
        {"year": "1851", "title": "Separation of Victoria", "desc": "Victoria separates from NSW to become an independent colony. The Gold Rush begins.", "link": "https://en.wikipedia.org/wiki/Separation_of_Queensland"},
        {"year": "1854", "title": "Eureka Stockade", "desc": "Miners in Ballarat rebel against license fees. A key event for Australian democracy.", "link": "https://en.wikipedia.org/wiki/Eureka_Rebellion"},
        {"year": "1856", "title": "Secret Ballot Introduced", "desc": "South Australia and Victoria pioneer the 'Secret Ballot' system, influencing democracy worldwide.", "link": "https://en.wikipedia.org/wiki/Secret_ballot#Australia"},
        {"year": "1859", "title": "Separation of Queensland", "desc": "Queensland separates from NSW to become an independent colony.", "link": "https://en.wikipedia.org/wiki/History_of_Queensland"},
        {"year": "1890s", "title": "The Depression & Labor Movement", "desc": "Economic depression strikes. The Australian Labor Party is formed, one of the world's oldest labor parties.", "link": "https://en.wikipedia.org/wiki/Australian_Labor_Party"},
        {"year": "1901", "title": "Federation of Australia", "desc": "The six colonies unite to form the Commonwealth of Australia. Edmund Barton becomes the first PM.", "link": "https://en.wikipedia.org/wiki/Federation_of_Australia"},
        {"year": "1902", "title": "Women's Suffrage", "desc": "The Commonwealth Franchise Act gives women the right to vote and stand for federal parliament.", "link": "https://en.wikipedia.org/wiki/Women%27s_suffrage_in_Australia"},
        {"year": "1915", "title": "Gallipoli Campaign", "desc": "ANZAC troops land at Gallipoli. The event defines national identity and mateship.", "link": "https://en.wikipedia.org/wiki/Gallipoli_campaign"},
        {"year": "1924", "title": "Compulsory Voting", "desc": "Voting becomes compulsory in federal elections to ensure full participation.", "link": "https://en.wikipedia.org/wiki/Electoral_system_of_Australia#Compulsory_voting"},
        {"year": "1927", "title": "Canberra becomes Capital", "desc": "Parliament House opens in Canberra, replacing Melbourne as the temporary seat of government.", "link": "https://en.wikipedia.org/wiki/History_of_Canberra"},
        {"year": "1942", "title": "Statute of Westminster", "desc": "Australia formally adopts independence from British legislation (retroactive to 1939).", "link": "https://en.wikipedia.org/wiki/Statute_of_Westminster_Adoption_Act_1942"},
        {"year": "1949", "title": "Liberal Party Era Begins", "desc": "Robert Menzies wins the election, starting the longest prime ministership in Australian history.", "link": "https://en.wikipedia.org/wiki/Robert_Menzies"},
        {"year": "1962", "title": "Indigenous Federal Vote", "desc": "Aboriginal people are granted the right to vote in federal elections.", "link": "https://en.wikipedia.org/wiki/Commonwealth_Electoral_Act_1962"},
        {"year": "1966", "title": "End of White Australia Policy", "desc": "Harold Holt begins dismantling the White Australia Policy, opening migration to non-Europeans.", "link": "https://en.wikipedia.org/wiki/White_Australia_policy"},
        {"year": "1967", "title": "1967 Referendum", "desc": "Over 90% of Australians vote to count Indigenous people in the census and allow federal laws for them.", "link": "https://en.wikipedia.org/wiki/1967_Australian_referendum"},
        {"year": "1972", "title": "It's Time", "desc": "Gough Whitlam wins election, ending 23 years of Liberal rule and introducing free university and universal healthcare.", "link": "https://en.wikipedia.org/wiki/Gough_Whitlam"},
        {"year": "1975", "title": "The Dismissal", "desc": "PM Gough Whitlam is controversially dismissed by Governor-General John Kerr.", "link": "https://en.wikipedia.org/wiki/1975_Australian_constitutional_crisis"},
        {"year": "1986", "title": "Australia Acts", "desc": "The Australia Acts sever all remaining legal ties to the UK courts and government.", "link": "https://en.wikipedia.org/wiki/Australia_Act_1986"},
        {"year": "1992", "title": "Mabo Decision", "desc": "The High Court overturns 'Terra Nullius', recognizing Native Title for Indigenous people.", "link": "https://en.wikipedia.org/wiki/Mabo_v_Queensland_(No_2)"},
        {"year": "1996", "title": "Port Arthur Massacre", "desc": "A tragedy leads PM John Howard to introduce strict national gun control laws.", "link": "https://en.wikipedia.org/wiki/Port_Arthur_massacre_(Australia)"},
        {"year": "1999", "title": "Republic Referendum", "desc": "Australians vote to keep the Monarch as head of state rather than becoming a Republic.", "link": "https://en.wikipedia.org/wiki/1999_Australian_republic_referendum"},
        {"year": "2000", "title": "Sydney Olympics", "desc": "Sydney hosts the Summer Olympics, celebrating Australian culture and sport.", "link": "https://en.wikipedia.org/wiki/2000_Summer_Olympics"},
        {"year": "2008", "title": "The Apology", "desc": "PM Kevin Rudd formally apologises to the Stolen Generations on behalf of the parliament.", "link": "https://en.wikipedia.org/wiki/Apology_to_Australia%27s_Indigenous_peoples"},
        {"year": "2010", "title": "First Female PM", "desc": "Julia Gillard becomes Australia's first female Prime Minister.", "link": "https://en.wikipedia.org/wiki/Julia_Gillard"},
        {"year": "2017", "title": "Marriage Equality", "desc": "Same-sex marriage is legalized following a national postal survey.", "link": "https://en.wikipedia.org/wiki/Australian_Marriage_Law_Postal_Survey"},
        {"year": "2023", "title": "The Voice Referendum", "desc": "A referendum to establish an Indigenous Voice to Parliament is held but rejected.", "link": "https://en.wikipedia.org/wiki/2023_Australian_Indigenous_Voice_referendum"}
    ]

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

# --- OPEN LIBRARY API (Improved Image Fetching) ---
@st.cache_data
def search_open_library_api(query):
    try:
        # Sort by Newest & Limit 25
        url = f"https://openlibrary.org/search.json?q={query}&limit=25&sort=new"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            return []
            
        data = response.json()
        books = []
        
        for item in data.get('docs', []):
            title = item.get('title', 'Unknown')
            author = item.get('author_name', ['Unknown'])[0]
            year = item.get('first_publish_year', 'N/A')
            cover_id = item.get('cover_i')
            isbn_list = item.get('isbn', [])
            
            # Robust Image Strategy
            if cover_id:
                img_url = f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg"
            elif isbn_list:
                img_url = f"https://covers.openlibrary.org/b/isbn/{isbn_list[0]}-M.jpg"
            else:
                img_url = "https://placehold.co/150x220/2a9d8f/FFF?text=Book"

            google_link = f"https://www.google.com/search?q={title}+{author}+book"
            
            book_entry = {
                "title": title,
                "author": author,
                "year": str(year),
                "desc": "Details available on search.", 
                "image": img_url,
                "link": google_link
            }
            books.append(book_entry)
        
        books.sort(key=lambda x: int(x['year']) if x['year'].isdigit() else 0, reverse=True)
        return books
    except:
        return []

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

# --- AUDIO SYSTEM (AUTO) ---
async def edge_tts_save(text, filename):
    # Standard Female Voice
    voice = "en-AU-NatashaNeural" 
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(filename)

def get_audio(text):
    filename = "temp_audio.mp3"
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(edge_tts_save(text, filename))
        return filename
    except:
        try:
            tts = gTTS(text=text, lang='en', tld='com.au')
            tts.save(filename)
            return filename
        except:
            return None

# --- UI LAYOUT ---

# Sidebar Navigation
st.sidebar.markdown("### 🏛️ Main Menu")
nav = st.sidebar.radio("", 
    ["🏆 Top 200 Books", "🔍 Global Search", "❤️ Favorites", "🌟 Hall of Fame", "📜 Australian History", "🗣️ Practice Chat"],
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
    st.subheader("🌍 Open Library Search")
    st.caption("Showing 25 newest results (Powered by Open Library).")
    
    with st.form("search_form"):
        col_s1, col_s2 = st.columns([4, 1])
        with col_s1:
            query = st.text_input("Title, Author, or ISBN", placeholder="e.g. Tim Winton")
        with col_s2:
            st.write("") 
            st.write("") 
            submitted = st.form_submit_button("🔎 Search")
            
    if submitted and query:
        with st.spinner("Connecting to global archives..."):
            st.session_state.search_results = search_open_library_api(query)
            
    if 'search_results' in st.session_state and st.session_state.search_results:
        grid_cols = st.columns(4)
        for idx, book in enumerate(st.session_state.search_results):
            with grid_cols[idx % 4]:
                cover_img = book['image']
                st.markdown(f"""
                <div class="book-card">
                    <div>
                        <img src="{cover_img}" style="width:100%; height:200px; object-fit:cover; border-radius:10px;">
                        <h5 class="book-title">{book['title'][:50]}...</h5>
                        <p class="book-author">{book['author'][:30]}</p>
                        <p class="book-year">📅 {book['year']}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                c_btn1, c_btn2 = st.columns(2)
                with c_btn1:
                    if st.button("❤️ Save", key=f"search_{idx}", help="Save", use_container_width=True):
                        add_to_favorites(book)
                with c_btn2:
                     st.markdown(f"<a href='{book['link']}' target='_blank' style='display:block; text-align:center; padding:10px; background:#eee; border-radius:5px; text-decoration:none; color:#333; font-weight:bold; margin-top:5px;'>📖 Info</a>", unsafe_allow_html=True)

    elif submitted:
        st.warning("No results found.")

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
    
    hof_data = get_hall_of_fame_data()
    
    # 1. Category Selection
    category = st.selectbox("Select Category:", list(hof_data.keys()))
    
    # 2. Person Selection
    col_sel, col_disp = st.columns([1, 2])
    with col_sel:
        name = st.selectbox("Select Person:", hof_data[category])
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
        else:
            st.info("👈 Select a category and person to view their biography.")

# === TAB 5: HISTORY ===
elif nav == "📜 Australian History":
    st.subheader("📜 Timeline of Australia")
    st.caption("From ancient times to modern statehood and elections.")
    
    timeline_data = get_history_timeline()
    
    for event in timeline_data:
        # Subtle color coding for centuries
        year_val = event['year'][:4]
        border_color = c['accent']
        if "17" in year_val: border_color = "#e76f51"
        elif "18" in year_val: border_color = "#f4a261"
        elif "19" in year_val: border_color = "#2a9d8f"
        elif "20" in year_val: border_color = "#264653"

        st.markdown(f"""
        <div class="book-card" style="margin-bottom: 20px; border-left: 8px solid {border_color}; min-height: auto;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h2 class="history-year" style="color:{border_color} !important; margin:0;">{event['year']}</h2>
                <a href="{event['link']}" target="_blank" style="text-decoration:none; color:{border_color}; font-size:0.8rem;">Read More 🔗</a>
            </div>
            <h3 style="margin-top:5px; color:{c['text_primary']}; font-size:1.1rem;">{event['title']}</h3>
            <p style="color:{c['text_primary']}; opacity:0.85; font-size:0.95rem; margin-bottom:0;">{event['desc']}</p>
        </div>
        """, unsafe_allow_html=True)

# === TAB 6: CHAT ===
elif nav == "🗣️ Practice Chat":
    st.subheader("💬 Patron Roleplay")
    col_set, col_play = st.columns([1, 2])
    with col_set:
        st.write("Click to generate a scenario:")
        if st.button("🎲 New Customer", type="primary", use_container_width=True):
            book = random.choice(st.session_state.top_books_db)
            templates = [
                f"Hi! Do you have '{book['title']}'? I heard it's great.",
                f"I'm looking for '{book['title']}' by {book['author']}.",
                f"Can you help me find the section for {book['genre']} books?"
            ]
            st.session_state.chat_text = random.choice(templates)
            st.session_state.chat_audio_file = get_audio(st.session_state.chat_text)
            st.rerun()
    with col_play:
        if 'chat_text' in st.session_state:
            st.markdown(f"<div class='chat-bubble'><b>Patron:</b> {st.session_state.chat_text}</div>", unsafe_allow_html=True)
            if st.session_state.get('chat_audio_file'):
                st.audio(st.session_state.chat_audio_file, format='audio/mp3')
