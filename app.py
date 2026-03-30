import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from pathlib import Path

st.set_page_config(
    page_title="Hope & Sarah's Recipe Box",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_TITLE = "Hope & Sarah's Recipe Box"
APP_TAGLINE = "A cozy plant-based recipe box you and Hope can update from anywhere."
BASE_DIR = Path(__file__).parent
LOGO_FILE = BASE_DIR / "assets" / "logo.png"

SHEET_COLUMNS = [
    "recipe_name",
    "category",
    "prep_time",
    "ingredients",
    "instructions",
    "notes",
    "favorite",
    "source_link",
]

def inject_css():
    st.markdown(
        '''
        <style>
            .stApp {
                background: linear-gradient(180deg, #f4f7fb 0%, #eef3f8 100%);
            }
            .block-container {
                padding-top: 1.25rem;
                padding-bottom: 2rem;
                max-width: 1350px;
            }
            .hero {
                background: rgba(255,255,255,0.88);
                border: 1px solid rgba(30,58,95,.08);
                border-radius: 24px;
                padding: 1.35rem 1.4rem 1rem 1.4rem;
                box-shadow: 0 10px 28px rgba(30,58,95,.07);
                margin-bottom: 1rem;
            }
            .search-wrap {
                background: rgba(255,255,255,0.88);
                border: 1px solid rgba(30,58,95,.08);
                border-radius: 20px;
                padding: .35rem .8rem .15rem .8rem;
                box-shadow: 0 8px 22px rgba(30,58,95,.05);
                margin-bottom: 1.1rem;
            }
            .stat-pill {
                background: white;
                border: 1px solid rgba(30,58,95,.08);
                border-radius: 16px;
                padding: .8rem 1rem;
                box-shadow: 0 6px 18px rgba(30,58,95,.05);
                text-align: center;
            }
            .stat-number {
                font-size: 1.6rem;
                font-weight: 700;
                color: #183153;
                line-height: 1.1;
            }
            .stat-label {
                font-size: .9rem;
                color: #66758a;
            }
            .recipe-card {
                background: rgba(255,255,255,.96);
                border: 1px solid rgba(30,58,95,.08);
                border-radius: 22px;
                padding: 1rem 1rem .8rem 1rem;
                box-shadow: 0 10px 26px rgba(30,58,95,.06);
                min-height: 385px;
                margin-bottom: 1rem;
            }
            .recipe-title {
                font-size: 1.55rem;
                line-height: 1.15;
                font-weight: 700;
                color: #1b3256;
                margin-bottom: .35rem;
            }
            .recipe-meta {
                font-size: .94rem;
                color: #6b7a90;
                margin-bottom: .75rem;
            }
            .section-label {
                color: #66758a;
                font-size: 1rem;
                font-weight: 600;
                margin-top: .4rem;
                margin-bottom: .3rem;
            }
            .recipe-preview {
                color: #30445f;
                font-size: 1.02rem;
                min-height: 76px;
            }
            .recipe-note {
                color: #6a7990;
                font-style: italic;
                margin-top: .65rem;
                min-height: 40px;
            }
            .heart {
                color: #f4b400;
                font-size: 1.2rem;
                font-weight: 700;
                float: right;
                margin-top: -.1rem;
            }
            .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {
                border-radius: 14px !important;
            }
            .sidebar-note {
                color: #6a7990;
                font-size: .93rem;
            }
        </style>
        ''',
        unsafe_allow_html=True,
    )

def normalize_bool(value) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes", "y"}

@st.cache_data(ttl="5m")
def load_recipes() -> pd.DataFrame:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl="5m")
    if df is None or df.empty:
        return pd.DataFrame(columns=SHEET_COLUMNS)
    for col in SHEET_COLUMNS:
        if col not in df.columns:
            df[col] = ""
    df = df[SHEET_COLUMNS].fillna("")
    return df

def render_header():
    left, right = st.columns([5, 1.5], vertical_alignment="center")
    with left:
        st.markdown('<div class="hero">', unsafe_allow_html=True)
        h1, h2 = st.columns([1.2, 5], vertical_alignment="center")
        with h1:
            if LOGO_FILE.exists():
                st.image(str(LOGO_FILE), use_container_width=True)
        with h2:
            st.markdown(f"<h1 style='margin-bottom:.1rem;color:#1c3558;'>{APP_TITLE}</h1>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size:1.2rem;color:#64748b;margin-top:.15rem'>{APP_TAGLINE}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with right:
        st.markdown(
            '''
            <div class="hero" style="text-align:center;">
                <div style="color:#1c3558;font-weight:700;font-size:1.1rem;">View only</div>
                <div style="color:#64748b;">You and Hope edit the shared Google Sheet.</div>
            </div>
            ''',
            unsafe_allow_html=True,
        )

def render_stats(df: pd.DataFrame, shown_count: int):
    fav_count = int(df["favorite"].apply(normalize_bool).sum()) if not df.empty else 0
    c1, c2, c3 = st.columns(3)
    stats = [(len(df), "recipes saved"), (shown_count, "showing now"), (fav_count, "favorites")]
    for col, (number, label) in zip((c1, c2, c3), stats):
        with col:
            st.markdown(
                f'''
                <div class="stat-pill">
                    <div class="stat-number">{number}</div>
                    <div class="stat-label">{label}</div>
                </div>
                ''',
                unsafe_allow_html=True,
            )

def matches_search(row: pd.Series, query: str) -> bool:
    if not query.strip():
        return True
    haystack = " ".join(
        [
            str(row.get("recipe_name", "")),
            str(row.get("ingredients", "")),
            str(row.get("instructions", "")),
            str(row.get("notes", "")),
            str(row.get("category", "")),
        ]
    ).lower()
    return query.lower() in haystack

def render_card(recipe: pd.Series):
    heart = '<span class="heart">♥</span>' if normalize_bool(recipe.get("favorite", False)) else ""
    ingredients = str(recipe.get("ingredients", ""))
    preview_ing = ingredients.replace("\n", "<br>")
    if len(ingredients) > 170:
        preview_ing = ingredients[:170].replace("\n", "<br>") + "..."
    preview_step = str(recipe.get("instructions", "")).strip().split("\n")[0]
    if len(preview_step) > 120:
        preview_step = preview_step[:117] + "..."
    note = str(recipe.get("notes", "")).strip()
    note_html = f"<div class='recipe-note'>Recipe note: {note}</div>" if note else "<div class='recipe-note'>&nbsp;</div>"

    st.markdown(
        f'''
        <div class="recipe-card">
            <div class="recipe-title">{recipe.get("recipe_name","Untitled Recipe")}{heart}</div>
            <div class="recipe-meta">{recipe.get("category","Uncategorized")} • {recipe.get("prep_time","")} </div>
            <div class="section-label">Ingredients</div>
            <div class="recipe-preview">{preview_ing or "No ingredients yet."}</div>
            <div class="section-label">Instructions</div>
            <div class="recipe-preview">{preview_step or "No instructions yet."}</div>
            {note_html}
        </div>
        ''',
        unsafe_allow_html=True,
    )

inject_css()

with st.sidebar:
    st.markdown("## 📖 Recipe Box")
    st.markdown('<div class="sidebar-note">The site is read-only. You and Hope update recipes in the shared Google Sheet.</div>', unsafe_allow_html=True)
    st.divider()

recipes = load_recipes()
category_options = ["All"] + sorted([c for c in recipes["category"].astype(str).unique().tolist() if c.strip()])

with st.sidebar:
    category_filter = st.selectbox("Category filter", category_options, index=0)
    favorites_only = st.checkbox("Favorites only")
    if st.button("Refresh from sheet", use_container_width=True):
        load_recipes.clear()
        st.rerun()

render_header()

st.markdown('<div class="search-wrap">', unsafe_allow_html=True)
search_text = st.text_input("Search recipes", placeholder="Search recipes...", label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

filtered = recipes.copy()
if category_filter != "All":
    filtered = filtered[filtered["category"].astype(str) == category_filter]
if favorites_only:
    filtered = filtered[filtered["favorite"].apply(normalize_bool)]
filtered = filtered[filtered.apply(lambda row: matches_search(row, search_text), axis=1)]
filtered = filtered.sort_values(by=["favorite", "recipe_name"], ascending=[False, True])

render_stats(recipes, len(filtered))
st.markdown("<div style='height:.75rem'></div>", unsafe_allow_html=True)

if filtered.empty:
    st.info("No recipes match your search yet.")
else:
    cols = st.columns(3)
    for idx, (_, recipe) in enumerate(filtered.iterrows()):
        with cols[idx % 3]:
            render_card(recipe)
            with st.expander("View full recipe"):
                st.markdown("### Ingredients")
                st.text(recipe.get("ingredients", ""))
                st.markdown("### Instructions")
                st.text(recipe.get("instructions", ""))
                if str(recipe.get("notes", "")).strip():
                    st.markdown("### Notes")
                    st.write(recipe.get("notes", ""))
                if str(recipe.get("source_link", "")).strip():
                    st.link_button("Open source", recipe.get("source_link", ""))
