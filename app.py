import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime

st.set_page_config(
    page_title="Hope & Sarah's Recipe Box",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_TITLE = "Hope & Sarah's Recipe Box"
APP_TAGLINE = "Your personal collection of plant-based recipes, all in one place."
BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "recipes.csv"
LOGO_FILE = BASE_DIR / "assets" / "logo.png"

COLUMNS = [
    "id",
    "date_added",
    "recipe_name",
    "ingredients",
    "instructions",
    "notes",
    "favorite",
    "category",
    "prep_time",
    "source_link",
]


def init_data() -> pd.DataFrame:
    if DATA_FILE.exists():
        df = pd.read_csv(DATA_FILE)
    else:
        seed = [
            {
                "id": 1,
                "date_added": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "recipe_name": "Chickpea Salad Sandwich",
                "ingredients": "1 can chickpeas\n2 tbsp vegan mayo\n1 celery stalk, diced\n1 tbsp dill\nSalt and pepper\nBread or toast",
                "instructions": "Mash the chickpeas, then mix with the rest of the ingredients. Serve on toasted bread.",
                "notes": "Great for a quick lunch.",
                "favorite": True,
                "category": "Lunch",
                "prep_time": "10 min",
                "source_link": "",
            },
            {
                "id": 2,
                "date_added": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "recipe_name": "Quinoa & Veggie Stir-Fry",
                "ingredients": "1 cup cooked quinoa\n2 cups mixed vegetables\n1 block tofu\n2 tbsp soy sauce\n1 tsp garlic\n1 tsp sesame oil",
                "instructions": "Cook quinoa. Sauté veggies and tofu. Add quinoa and sauce, then stir until hot.",
                "notes": "Use tamari instead of soy sauce for gluten-free.",
                "favorite": True,
                "category": "Dinner",
                "prep_time": "25 min",
                "source_link": "",
            },
            {
                "id": 3,
                "date_added": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "recipe_name": "Creamy Avocado Pasta",
                "ingredients": "8 oz pasta\n2 ripe avocados\n2 garlic cloves\n2 tbsp lemon juice\nFresh basil\nSalt and pepper",
                "instructions": "Blend avocado, garlic, lemon, basil, salt, and pepper. Toss with warm pasta.",
                "notes": "Quick and easy dinner.",
                "favorite": False,
                "category": "Dinner",
                "prep_time": "20 min",
                "source_link": "",
            },
        ]
        df = pd.DataFrame(seed)

    for col in COLUMNS:
        if col not in df.columns:
            df[col] = ""
    return df[COLUMNS].fillna("")

def save_data(df: pd.DataFrame) -> None:
    df.to_csv(DATA_FILE, index=False)

def next_id(df: pd.DataFrame) -> int:
    if df.empty:
        return 1
    ids = pd.to_numeric(df["id"], errors="coerce").dropna()
    return int(ids.max()) + 1 if not ids.empty else 1

def truthy(value) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes", "y"}

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

def inject_css() -> None:
    st.markdown(
        """
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
                background: rgba(255,255,255,0.85);
                border: 1px solid rgba(30,58,95,.08);
                border-radius: 24px;
                padding: 1.4rem 1.4rem 1rem 1.4rem;
                box-shadow: 0 10px 28px rgba(30,58,95,.07);
                margin-bottom: 1rem;
            }
            .search-wrap {
                background: rgba(255,255,255,0.85);
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
                font-size: 1.65rem;
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
            .stButton > button {
                border-radius: 999px;
                border: none;
                padding: .65rem 1.15rem;
                font-weight: 600;
                box-shadow: 0 8px 20px rgba(59,130,246,.18);
            }
            .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div {
                border-radius: 14px !important;
            }
            .sidebar-note {
                color: #6a7990;
                font-size: .93rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

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
            st.markdown(f"<div style='font-size:1.25rem;color:#64748b;margin-top:.15rem'>{APP_TAGLINE}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with right:
        st.page_link("https://github.com", label="GitHub later", icon="🔗")

def render_stats(df: pd.DataFrame, shown_count: int):
    c1, c2, c3 = st.columns(3)
    fav_count = int(df["favorite"].apply(truthy).sum()) if not df.empty else 0
    for col, number, label in [
        (c1, len(df), "recipes saved"),
        (c2, shown_count, "showing now"),
        (c3, fav_count, "favorites"),
    ]:
        with col:
            st.markdown(
                f"""
                <div class="stat-pill">
                    <div class="stat-number">{number}</div>
                    <div class="stat-label">{label}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

def render_card(recipe: pd.Series):
    heart = '<span class="heart">♥</span>' if truthy(recipe.get("favorite", False)) else ""
    preview = str(recipe.get("instructions", "")).strip().split("\n")[0]
    if len(preview) > 120:
        preview = preview[:117] + "..."
    note = str(recipe.get("notes", "")).strip()
    note_html = f"<div class='recipe-note'>Recipe: {note}</div>" if note else "<div class='recipe-note'>&nbsp;</div>"

    st.markdown(
        f"""
        <div class="recipe-card">
            <div class="recipe-title">{recipe.get("recipe_name","")}{heart}</div>
            <div class="recipe-meta">{recipe.get("category","Uncategorized")} • {recipe.get("prep_time","")} </div>
            <div class="section-label">Ingredients</div>
            <div class="recipe-preview">{str(recipe.get("ingredients","")).replace(chr(10), "<br>")[:170]}{'...' if len(str(recipe.get("ingredients",""))) > 170 else ''}</div>
            <div class="section-label">Instructions</div>
            <div class="recipe-preview">{preview or "No instructions yet."}</div>
            {note_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

df = init_data()
inject_css()

with st.sidebar:
    st.markdown("## 📖 Recipe Box")
    st.markdown('<div class="sidebar-note">A clean place to keep your favorite plant-based recipes.</div>', unsafe_allow_html=True)
    page = st.radio("Navigate", ["Browse", "Add Recipe", "Edit Recipe"], label_visibility="visible")
    category_options = ["All"] + sorted([c for c in df["category"].astype(str).unique().tolist() if c.strip()])
    category_filter = st.selectbox("Category filter", category_options, index=0)
    favorites_only = st.checkbox("Favorites only")
    st.divider()
    st.caption("When you're happy with it, upload this folder to GitHub and deploy on Streamlit Community Cloud.")

render_header()

if page == "Browse":
    st.markdown('<div class="search-wrap">', unsafe_allow_html=True)
    search_text = st.text_input("Search recipes", placeholder="Search recipes...", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    filtered = df.copy()
    if category_filter != "All":
        filtered = filtered[filtered["category"].astype(str) == category_filter]
    if favorites_only:
        filtered = filtered[filtered["favorite"].apply(truthy)]
    filtered = filtered[filtered.apply(lambda row: matches_search(row, search_text), axis=1)]
    filtered = filtered.sort_values(by=["favorite", "recipe_name"], ascending=[False, True])

    render_stats(df, len(filtered))
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

elif page == "Add Recipe":
    st.subheader("Add a new recipe")
    with st.form("add_recipe_form", clear_on_submit=True):
        c1, c2 = st.columns([2, 1])
        with c1:
            recipe_name = st.text_input("Recipe name*")
        with c2:
            category = st.text_input("Category", placeholder="Dinner")
        c3, c4 = st.columns(2)
        with c3:
            prep_time = st.text_input("Prep time", placeholder="20 min")
        with c4:
            favorite = st.checkbox("Favorite")
        ingredients = st.text_area("Ingredients", height=180, placeholder="1 can chickpeas\n2 tbsp vegan mayo\n...")
        instructions = st.text_area("Instructions", height=200, placeholder="1. Mash the chickpeas...\n2. Mix everything together...")
        notes = st.text_area("Notes", height=110, placeholder="Anything you want to remember next time.")
        source_link = st.text_input("Source link", placeholder="https://...")
        submitted = st.form_submit_button("Save recipe", use_container_width=True)

        if submitted:
            if not recipe_name.strip():
                st.error("Recipe name is required.")
            else:
                new_row = {
                    "id": next_id(df),
                    "date_added": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "recipe_name": recipe_name.strip(),
                    "ingredients": ingredients.strip(),
                    "instructions": instructions.strip(),
                    "notes": notes.strip(),
                    "favorite": favorite,
                    "category": category.strip(),
                    "prep_time": prep_time.strip(),
                    "source_link": source_link.strip(),
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                save_data(df)
                st.success("Recipe saved. Head to Browse to see it in your recipe box.")
                st.rerun()

elif page == "Edit Recipe":
    st.subheader("Edit a saved recipe")
    if df.empty:
        st.info("No recipes to edit yet.")
    else:
        labels = (df["recipe_name"].astype(str) + " — ID " + df["id"].astype(str)).tolist()
        selected_label = st.selectbox("Choose a recipe", labels)
        selected_id = int(selected_label.split(" — ID ")[-1])
        idx = df.index[pd.to_numeric(df["id"], errors="coerce") == selected_id][0]
        current = df.loc[idx]

        with st.form("edit_recipe_form"):
            c1, c2 = st.columns([2, 1])
            with c1:
                recipe_name = st.text_input("Recipe name*", value=current.get("recipe_name", ""))
            with c2:
                category = st.text_input("Category", value=current.get("category", ""))
            c3, c4 = st.columns(2)
            with c3:
                prep_time = st.text_input("Prep time", value=current.get("prep_time", ""))
            with c4:
                favorite = st.checkbox("Favorite", value=truthy(current.get("favorite", False)))
            ingredients = st.text_area("Ingredients", value=current.get("ingredients", ""), height=180)
            instructions = st.text_area("Instructions", value=current.get("instructions", ""), height=200)
            notes = st.text_area("Notes", value=current.get("notes", ""), height=110)
            source_link = st.text_input("Source link", value=current.get("source_link", ""))
            saved = st.form_submit_button("Update recipe", use_container_width=True)

            if saved:
                df.at[idx, "recipe_name"] = recipe_name.strip()
                df.at[idx, "category"] = category.strip()
                df.at[idx, "prep_time"] = prep_time.strip()
                df.at[idx, "favorite"] = favorite
                df.at[idx, "ingredients"] = ingredients.strip()
                df.at[idx, "instructions"] = instructions.strip()
                df.at[idx, "notes"] = notes.strip()
                df.at[idx, "source_link"] = source_link.strip()
                save_data(df)
                st.success("Recipe updated.")
                st.rerun()
