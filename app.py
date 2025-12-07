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
# Define color palettes for different themes
themes = {
    "Ocean 🌊": {
        "bg_gradient": "linear-gradient(90deg, #264653 0%, #2a9d8f 100%)",
        "sidebar_bg": "#f8f9fa",
        "sidebar_text": "#264653",
        "card_bg": "#ffffff",
        "card_border": "#e0e0e0",
        "text_primary": "#264653",
        "text_secondary": "#e76f51",
        "accent": "#2a9d8f",
        "badge": "#e9c46a"
    },
    "Midnight 🌑": {
        "bg_gradient": "linear-gradient(90deg, #0f2027 0%, #203a43 50%, #2c5364 100%)",
        "sidebar_bg": "#1e1e1e",
        "sidebar_text": "#ffffff",
        "card_bg": "#2d2d2d",
        "card_border": "#404040",
        "text_primary": "#e0e0e0",
        "text_secondary": "#4db6ac",
        "accent": "#80cbc4",
        "badge": "#ffca28"
    },
    "Autumn 🍂": {
        "bg_gradient": "linear-gradient(90deg, #d35400 0%, #e67e22 100%)",
        "sidebar_bg": "#fdf2e9",
        "sidebar_text": "#6e2c00",
        "card_bg": "#ffffff",
        "card_border": "#edbb99",
        "text_primary": "#873600",
        "text_secondary": "#d35400",
        "accent": "#e67e22",
        "badge": "#f5b041"
    }
}

# Initialize Session State for Theme
if 'current_theme' not in st.session_state:
    st.session_state.current_theme = "Ocean 🌊"

# --- SIDEBAR & THEME SELECTOR ---
st.sidebar.markdown("### 🎨 Appearance")
selected_theme_name = st.sidebar.selectbox("Choose Theme:", list(themes.keys()), index=0)
st.session_state.current_theme = selected_theme_name
current_colors = themes[st.session_state.current_theme]

# --- DYNAMIC CSS STYLING ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Poppins', sans-serif;
    }}
    
    /* Main Header Gradient */
    .main-header {{
        background: {current_colors['bg_gradient']};
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        text-align: center;
    }}
    
    /* Sidebar Styling - Dynamic */
    section[data-testid="stSidebar"] {{
        background-color: {current_colors['sidebar_bg']};
    }}
    
    section[data-testid="stSidebar"] .stMarkdown, 
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3, 
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span {{
        color: {current_colors['sidebar_text']} !important;
    }}
    
    /* Card Design */
    .small-book-card, .book-card {{
        background: {current_colors['card_bg']};
        border-radius: 12px;
        padding: 12px;
        height: 100%;
        min-height: 220px;
        border: 1px solid {current_colors['card_border']};
        transition: transform 0.2s, box-shadow 0.2s;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        color: {current_colors['text_primary']};
    }}
    
    .small-book-card:hover, .book-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 6px 15px rgba(0,0,0,0.15);
        border-color: {current_colors['accent']};
    }}
    
    .small-title, .book-title {{
        font-size: 0.9rem;
        font-weight: 600;
        color: {current_colors['text_primary']};
        margin-top: 15px;
        line-height: 1.3;
    }}
    
    .small-author, .book-author {{
        font-size: 0.8rem;
        color: {current_colors['text_secondary']};
        margin-bottom: 8px;
    }}
    
    .small-badge {{
        position: absolute;
        top: 8px;
        right: 8px;
        background: {current_colors['badge']};
        color: #333;
        padding: 3px 8px;
        border-radius: 10px;
        font-size: 0.65rem;
        font-weight: bold;
    }}
    
    /* Search Result Images */
    .book-cover-img {{
        width: 100%;
        height: 180px;
        object-fit: cover;
        border-radius: 8px;
        margin-bottom: 10px;
    }}
    
    /* Chat Bubbles */
    .chat-bubble {{
        background-color: {current_colors['card_bg']};
        border-radius: 15px;
        border-bottom-left-radius: 0;
        padding: 15px;
        margin: 10px 0;
        border-left: 5px solid {current_colors['accent']};
        color: {current_colors['text_primary']};
        border: 1px solid {current_colors['card_border']};
    }}
    
    /* Buttons */
    .stButton>button {{
        border-radius: 8px;
        font-weight: 600;
        border: 1px solid {current_colors['accent']};
    }}
    .stButton>button:hover {{
        border-color: {current_colors['text_secondary']};
        color: {current_colors['text_secondary']};
    }}
    
    /* Override Streamlit Dark Mode Default Texts */
    p, h1, h2, h3, h4, h5, li {{
        color: {current_colors['text_primary']};
    }}
    
</style>
""", unsafe_allow_html=True)

# --- 1. DATA & STATE ---
if 'favorites' not in st.session_state:
    st.session_state.favorites = []

# --- DATA GENERATION (200 BOOKS) ---
def get_top_200_books():
    base_list = [
        # --- Australian Classics & Modern Classics ---
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
        # --- Contemporary Australian Fiction ---
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
        # --- Non-Fiction / Biography / History ---
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
        # --- Kids & YA ---
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
        # --- International Bestsellers Popular in Australia ---
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

# Sidebar Navigation
st.sidebar.markdown("### 🏛️ Library Menu")
nav = st.sidebar.radio("", 
    ["🏆 Top 200 Books", "🔍 Global Search", "❤️ My Favorites", "🌟 Hall of Fame", "🗣️ Practice Chat"],
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

# === TAB 1: TOP 200 LIST (COMPACT GRID) ===
if nav == "🏆 Top 200 Books":
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("🇦🇺 Top 200 Essential Reading")
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
                   <a href="{book['search_link']}" target="_blank" style="text-decoration:none; font-size:0.7rem; color:{current_colors['accent']};">🔎 Verify</a>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("➕", key=f"top_{idx}", help="Add to Favorites", use_container_width=True):
                add_to_favorites(book)
            st.write("") 

# === TAB 2: SEARCH ===
elif nav == "🔍 Global Search":
    st.subheader("🌍 Global Library Catalog (Google Books)")
    
    with st.form("search_form"):
        col_s1, col_s2 = st.columns([4, 1])
        with col_s1:
            query = st.text_input("Title, Author, or ISBN", placeholder="e.g. Tim Winton")
        with col_s2:
            submitted = st.form_submit_button("Search")
            
    if submitted and query:
        with st.spinner("Connecting to global archives..."):
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
                    if st.button("❤️", key=f"search_{idx}", help="Save", use_container_width=True):
                        add_to_favorites(book)
                with c_btn2:
                    with st.popover("📖"):
                        st.subheader(book['title'])
                        st.write(book['desc'])
                        st.markdown(f"[View on Google Books]({book['link']})")

# === TAB 3: FAVORITES ===
elif nav == "❤️ My Favorites":
    st.subheader("📚 My Reading List")
    if not st.session_state.favorites:
        st.info("Your list is empty! Go to 'Top 200' or 'Search' to add books.")
    else:
        if st.button("🗑️ Clear List", type="primary"):
            st.session_state.favorites = []
            st.rerun()
        for fav in st.session_state.favorites:
            with st.container():
                c1, c2 = st.columns([5, 1])
                with c1:
                    st.markdown(f"**{fav['title']}** - {fav['author']}")
                with c2:
                    if st.button("❌", key=f"del_{fav['title']}"):
                        remove_from_favorites(fav['title'])
            st.divider()

# === TAB 4: HALL OF FAME ===
elif nav == "🌟 Hall of Fame":
    st.subheader("🌟 Aria's Hall of Fame")
    col_sel, col_disp = st.columns([1, 2])
    with col_sel:
        name = st.selectbox("Select Personality:", st.session_state.hall_of_fame)
        if st.button("Load Bio", type="primary", use_container_width=True):
            with st.spinner("Fetching..."):
                st.session_state.wiki_bio = get_wiki_bio(name)
    with col_disp:
        if 'wiki_bio' in st.session_state and st.session_state.wiki_bio:
            bio = st.session_state.wiki_bio
            st.markdown(f"""
            <div class="book-card" style="display:flex; gap:20px; align-items:start; flex-direction:row;">
                <img src="{bio['image']}" style="width:120px; height:120px; object-fit:cover; border-radius:50%; border:4px solid {current_colors['accent']}; flex-shrink:0;">
                <div>
                    <h2 style="color:{current_colors['text_primary']}; margin-top:0;">{bio['title']}</h2>
                    <p style="color:{current_colors['text_primary']};">{bio['summary']}</p>
                    <a href="{bio['url']}" target="_blank" style="color:{current_colors['accent']}">Read Full Article</a>
                </div>
            </div>
            """, unsafe_allow_html=True)

# === TAB 5: CHAT ===
elif nav == "🗣️ Practice Chat":
    st.subheader("💬 Patron Roleplay")
    col_set, col_play = st.columns([1, 2])
    with col_set:
        gender = st.radio("Voice:", ["Female", "Male"], horizontal=True)
        if st.button("🎲 New Customer", type="primary", use_container_width=True):
            book = random.choice(st.session_state.top_books_db)
            templates = [
                f"Hi! Do you have '{book['title']}'? I heard it's great.",
                f"I'm looking for '{book['title']}' by {book['author']}.",
                f"Can you help me find the section for {book['genre']} books?"
            ]
            st.session_state.chat_text = random.choice(templates)
            st.session_state.chat_audio_file = get_audio(st.session_state.chat_text, gender)
            st.rerun()
    with col_play:
        if 'chat_text' in st.session_state:
            st.markdown(f"<div class='chat-bubble'><b>Patron:</b> {st.session_state.chat_text}</div>", unsafe_allow_html=True)
            if st.session_state.get('chat_audio_file'):
                st.audio(st.session_state.chat_audio_file, format='audio/mp3')
