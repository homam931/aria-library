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

# --- THEME CONFIGURATION (With Gradients for Buttons) ---
themes = {
    "Ocean 🌊 (پیش‌فرض)": {
        "bg_gradient": "linear-gradient(135deg, #264653 0%, #2a9d8f 100%)",
        "btn_grad": "linear-gradient(90deg, #264653 0%, #2a9d8f 100%)",
        "sidebar_bg": "#f0f8ff",
        "sidebar_text": "#264653",
        "card_bg": "#ffffff",
        "card_border": "#b2dfdb",
        "text_primary": "#2c3e50",
        "text_secondary": "#e76f51",
        "accent": "#2a9d8f",
        "badge_bg": "#e9c46a",
        "badge_text": "#264653"
    },
    "Midnight 🌑 (شب)": {
        "bg_gradient": "linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%)",
        "btn_grad": "linear-gradient(90deg, #4db6ac 0%, #80cbc4 100%)",
        "sidebar_bg": "#121212",
        "sidebar_text": "#ffffff",
        "card_bg": "#1e1e1e",
        "card_border": "#333333",
        "text_primary": "#e0e0e0",
        "text_secondary": "#4db6ac",
        "accent": "#80cbc4",
        "badge_bg": "#ffca28",
        "badge_text": "#000000"
    },
    "Vintage 📜 (کاغذ قدیمی)": {
        "bg_gradient": "linear-gradient(135deg, #8e44ad 0%, #c0392b 100%)",
        "btn_grad": "linear-gradient(90deg, #d7c08e 0%, #bcaaa4 100%)",
        "main_bg_color": "#fdf6e3",
        "sidebar_bg": "#f4e4bc",
        "sidebar_text": "#4b3621",
        "card_bg": "#fffbf0",
        "card_border": "#d7c08e",
        "text_primary": "#5d4037",
        "text_secondary": "#8d6e63",
        "accent": "#a1887f",
        "badge_bg": "#8d6e63",
        "badge_text": "#ffffff"
    },
    "Cyberpunk 🤖 (سایبر)": {
        "bg_gradient": "linear-gradient(135deg, #2b003e 0%, #000000 100%)",
        "btn_grad": "linear-gradient(90deg, #ff0099 0%, #493240 100%)",
        "sidebar_bg": "#0b0c15",
        "sidebar_text": "#00f3ff",
        "card_bg": "#1a1a2e",
        "card_border": "#ff0099",
        "text_primary": "#ffffff",
        "text_secondary": "#00f3ff",
        "accent": "#ff0099",
        "badge_bg": "#00f3ff",
        "badge_text": "#000000"
    },
    "Classic 🏛️ (کلاسیک)": {
        "bg_gradient": "linear-gradient(135deg, #2c3e50 0%, #4ca1af 100%)",
        "btn_grad": "linear-gradient(90deg, #2c3e50 0%, #34495e 100%)",
        "sidebar_bg": "#ffffff",
        "sidebar_text": "#2c3e50",
        "card_bg": "#ffffff",
        "card_border": "#bdc3c7",
        "text_primary": "#2c3e50",
        "text_secondary": "#7f8c8d",
        "accent": "#2980b9",
        "badge_bg": "#ecf0f1",
        "badge_text": "#2c3e50"
    },
    "Forest 🌲 (طبیعت)": {
        "bg_gradient": "linear-gradient(135deg, #134e5e 0%, #71b280 100%)",
        "btn_grad": "linear-gradient(90deg, #11998e 0%, #38ef7d 100%)",
        "sidebar_bg": "#e8f5e9",
        "sidebar_text": "#1b5e20",
        "card_bg": "#ffffff",
        "card_border": "#a5d6a7",
        "text_primary": "#2e7d32",
        "text_secondary": "#558b2f",
        "accent": "#2e7d32",
        "badge_bg": "#c8e6c9",
        "badge_text": "#1b5e20"
    },
    "Royal 👑 (سلطنتی)": {
        "bg_gradient": "linear-gradient(135deg, #4b134f 0%, #c94b4b 100%)",
        "btn_grad": "linear-gradient(90deg, #8e24aa 0%, #ab47bc 100%)",
        "sidebar_bg": "#f3e5f5",
        "sidebar_text": "#4a148c",
        "card_bg": "#ffffff",
        "card_border": "#e1bee7",
        "text_primary": "#4a148c",
        "text_secondary": "#7b1fa2",
        "accent": "#8e24aa",
        "badge_bg": "#ffd700",
        "badge_text": "#4a148c"
    },
    "Sunset 🌅 (غروب)": {
        "bg_gradient": "linear-gradient(135deg, #ff512f 0%, #dd2476 100%)",
        "btn_grad": "linear-gradient(90deg, #ff512f 0%, #f09819 100%)",
        "sidebar_bg": "#fff3e0",
        "sidebar_text": "#e65100",
        "card_bg": "#ffffff",
        "card_border": "#ffcc80",
        "text_primary": "#bf360c",
        "text_secondary": "#f57c00",
        "accent": "#ff6f00",
        "badge_bg": "#ffcc80",
        "badge_text": "#bf360c"
    }
}

# Initialize Theme State
if 'current_theme' not in st.session_state:
    st.session_state.current_theme = "Ocean 🌊 (پیش‌فرض)"

# --- SIDEBAR UI ---
st.sidebar.markdown("### 🎨 تنظیمات ظاهر")
selected_theme_name = st.sidebar.selectbox("انتخاب تم:", list(themes.keys()), index=0)
st.session_state.current_theme = selected_theme_name
c = themes[st.session_state.current_theme]

# --- DYNAMIC CSS ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Poppins', sans-serif;
        color: {c['text_primary']};
    }}
    
    .stApp {{
        background-color: {c.get('main_bg_color', '#ffffff')} !important;
    }}

    /* HEADER - 3D Effect */
    .main-header {{
        background: {c['bg_gradient']};
        padding: 2.5rem; 
        border-radius: 20px; 
        color: white; 
        margin-bottom: 2.5rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15); 
        text-align: center;
        border: 1px solid rgba(255,255,255,0.2);
    }}
    .main-header h1 {{ font-weight: 700; letter-spacing: -1px; text-shadow: 0 2px 4px rgba(0,0,0,0.2); }}

    /* SIDEBAR styling */
    section[data-testid="stSidebar"] {{
        background-color: {c['sidebar_bg']};
        border-right: 1px solid {c['card_border']};
    }}
    
    /* Active Sidebar Item - POP Effect */
    .stRadio > div > label[data-baseweb="radio"] > div:first-child {{
        background-color: transparent !important;
        border-color: transparent !important; 
    }}
    .stRadio > div > label {{
        background-color: transparent;
        color: {c['sidebar_text']};
        padding: 12px 15px;
        margin-bottom: 8px;
        border-radius: 12px;
        border: 1px solid transparent;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        cursor: pointer;
        font-weight: 500;
    }}
    /* When Checked (Simulated via CSS targeting the one with darker text usually, but Streamlit is tricky. 
       We rely on the internal checked div structure) */
    .stRadio > div > label:has(div[aria-checked="true"]) {{
        background: {c['btn_grad']} !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transform: scale(1.02);
        font-weight: 700;
    }}
    .stRadio > div > label:hover {{
        background-color: {c['card_border']}44;
    }}

    /* GLOBAL TEXT COLOR FIX */
    .stMarkdown, .stText, p, h1, h2, h3, h4, h5, li, span, div {{
        color: {c['text_primary']} !important;
    }}
    /* Exception for buttons and header text which need to be white usually */
    .main-header *, button * {{
        color: inherit !important;
    }}
    
    /* CARDS - Glassmorphism touch */
    .small-book-card, .book-card {{
        background: {c['card_bg']};
        border-radius: 16px;
        padding: 15px;
        height: 100%;
        min-height: 240px;
        border: 1px solid {c['card_border']};
        transition: all 0.3s ease;
        display: flex; flex-direction: column; justify-content: space-between;
        position: relative;
        overflow: hidden;
    }}
    .small-book-card:hover, .book-card:hover {{
        transform: translateY(-8px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.12);
        border-color: {c['accent']};
    }}
    
    /* BADGES - Pill Shape & Pop */
    .small-badge {{
        position: absolute; top: 10px; right: 10px;
        background: {c['badge_bg']}; 
        color: {c['badge_text']} !important;
        padding: 4px 12px; 
        border-radius: 20px; 
        font-size: 0.7rem; 
        font-weight: 700;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        z-index: 2;
    }}

    /* BUTTONS - BEAUTIFUL GRADIENT & BOLD */
    .stButton > button {{
        width: 100%;
        border-radius: 12px;
        font-weight: 600;
        color: white !important;
        background: {c['btn_grad']} !important;
        border: none;
        height: 48px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }}
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(0,0,0,0.25);
        filter: brightness(1.1);
    }}
    .stButton > button:active {{
        transform: translateY(1px);
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }}

    /* TEXT STYLES */
    .small-title, .book-title {{
        font-size: 0.95rem; font-weight: 700;
        color: {c['text_primary']} !important;
        margin-top: 15px; line-height: 1.4;
    }}
    .small-author, .book-author {{
        font-size: 0.8rem;
        color: {c['text_secondary']} !important;
        font-weight: 500;
        margin-bottom: 10px;
    }}
    
    /* CHAT BUBBLES */
    .chat-bubble {{
        background-color: {c['card_bg']};
        padding: 20px; border-radius: 20px; border-bottom-left-radius: 2px;
        border-left: 5px solid {c['accent']};
        color: {c['text_primary']} !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
    }}
    
    /* SEARCH INPUT */
    input[type="text"] {{
        background-color: {c['card_bg']} !important;
        color: {c['text_primary']} !important;
        border: 2px solid {c['card_border']} !important;
        border-radius: 12px;
        padding: 10px;
    }}
    input[type="text"]:focus {{
        border-color: {c['accent']} !important;
        box-shadow: 0 0 0 3px {c['accent']}33;
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
    try:
        url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=40&langRestrict=en"
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return []
        data = response.json()
        books = []
        if 'items' in data:
            for item in data['items']:
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

# Sidebar Navigation (IMPROVED for Mobile)
st.sidebar.markdown("### 🏛️ منوی اصلی")
nav = st.sidebar.radio("", 
    ["🏆 ۲۰۰ کتاب برتر", "🔍 جستجوی جهانی", "❤️ علاقه‌مندی‌ها", "🌟 تالار مشاهیر", "🗣️ تمرین گفتگو"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.metric(label="کتاب‌های ذخیره شده", value=len(st.session_state.favorites), delta=None)

# Main Header
st.markdown("""
<div class="main-header">
    <h1>🐨 Aria Library AI Hub</h1>
    <p>مرکز هوشمند کتابخانه و ادبیات استرالیا</p>
</div>
""", unsafe_allow_html=True)

# === TAB 1: TOP 200 LIST ===
if nav == "🏆 ۲۰۰ کتاب برتر":
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("🇦🇺 لیست خواندنی‌های ضروری")
    with col2:
        filter_genre = st.selectbox("فیلتر ژانر", ["All", "Fiction", "Non-Fiction", "Classic", "Kids", "YA", "Crime", "Historical"])
    
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
                   <a href="{book['search_link']}" target="_blank" style="text-decoration:none; font-size:0.75rem; color:{c['text_secondary']}; font-weight:600;">🔎 بررسی آنلاین</a>
                </div>
            </div>
            """, unsafe_allow_html=True)
            # Stylish Button
            if st.button("➕ افزودن", key=f"top_{idx}", help="افزودن به علاقه مندی", use_container_width=True):
                add_to_favorites(book)
            st.write("") 

# === TAB 2: SEARCH ===
elif nav == "🔍 جستجوی جهانی":
    st.subheader("🌍 جستجو در گوگل بوکس")
    
    with st.form("search_form"):
        col_s1, col_s2 = st.columns([4, 1])
        with col_s1:
            query = st.text_input("عنوان، نویسنده یا شابک", placeholder="مثال: Tim Winton")
        with col_s2:
            st.write("") # Spacer to align button
            st.write("") 
            submitted = st.form_submit_button("🔎 جستجو")
            
    if submitted and query:
        with st.spinner("در حال اتصال به پایگاه جهانی..."):
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
                    if st.button("❤️ ذخیره", key=f"search_{idx}", help="ذخیره", use_container_width=True):
                        add_to_favorites(book)
                with c_btn2:
                    with st.popover("📖 جزئیات"):
                        st.subheader(book['title'])
                        st.write(book['desc'])
                        st.markdown(f"[مشاهده در گوگل]({book['link']})")

# === TAB 3: FAVORITES ===
elif nav == "❤️ علاقه‌مندی‌ها":
    st.subheader("📚 لیست مطالعه من")
    if not st.session_state.favorites:
        st.info("لیست شما خالی است! از بخش جستجو یا لیست برتر کتاب اضافه کنید.")
    else:
        if st.button("🗑️ پاک کردن همه", type="primary"):
            st.session_state.favorites = []
            st.rerun()
        for fav in st.session_state.favorites:
            with st.container():
                c1, c2 = st.columns([5, 1])
                with c1:
                    st.markdown(f"**{fav['title']}** - {fav['author']}")
                with c2:
                    if st.button("❌ حذف", key=f"del_{fav['title']}"):
                        remove_from_favorites(fav['title'])
            st.divider()

# === TAB 4: HALL OF FAME ===
elif nav == "🌟 تالار مشاهیر":
    st.subheader("🌟 چهره‌های ماندگار")
    col_sel, col_disp = st.columns([1, 2])
    with col_sel:
        name = st.selectbox("انتخاب شخصیت:", st.session_state.hall_of_fame)
        if st.button("نمایش بیوگرافی", type="primary", use_container_width=True):
            with st.spinner("در حال دریافت اطلاعات..."):
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
                    <a href="{bio['url']}" target="_blank" style="color:{c['accent']}; font-weight:bold;">خواندن مقاله کامل</a>
                </div>
            </div>
            """, unsafe_allow_html=True)

# === TAB 5: CHAT ===
elif nav == "🗣️ تمرین گفتگو":
    st.subheader("💬 نقش‌آفرینی کتابدار")
    col_set, col_play = st.columns([1, 2])
    with col_set:
        gender = st.radio("صدای مشتری:", ["خانم", "آقا"], horizontal=True)
        if st.button("🎲 مشتری جدید", type="primary", use_container_width=True):
            book = random.choice(st.session_state.top_books_db)
            g_code = "Female" if gender == "خانم" else "Male"
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
            st.markdown(f"<div class='chat-bubble'><b>مشتری:</b> {st.session_state.chat_text}</div>", unsafe_allow_html=True)
            if st.session_state.get('chat_audio_file'):
                st.audio(st.session_state.chat_audio_file, format='audio/mp3')
