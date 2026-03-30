import shutil
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Hope & Sarah's Recipe Box",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_TITLE = "Hope & Sarah's Recipe Box"
APP_TAGLINE = "Plant-based recipes for everyone to enjoy."
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_FILE = DATA_DIR / "recipes.csv"
BACKUP_DIR = DATA_DIR / "backups"

RECIPE_COLUMNS = [
    "recipe_name",
    "category",
    "prep_time",
    "ingredients",
    "instructions",
    "notes",
    "favorite",
    "source_link",
    "rating",
    "tags",
]

DEFAULT_TAGS = [
    "asian",
    "indian",
    "italian",
    "mexican",
    "soup",
    "salad",
    "dessert",
    "breakfast",
    "lunch",
    "dinner",
    "quick",
    "high protein",
    "tofu",
    "pasta",
]


def inject_css():
    st.markdown(
        """
        <style>
            .stApp {
                background: linear-gradient(180deg, #eef4fb 0%, #f7f9fc 100%);
            }
            .block-container {
                max-width: 1380px;
                padding-top: 1rem;
                padding-bottom: 2rem;
            }
            .hero {
                background: rgba(255,255,255,0.92);
                border: 1px solid rgba(30,58,95,.08);
                border-radius: 24px;
                padding: 1.2rem 1.3rem 1rem 1.3rem;
                box-shadow: 0 12px 28px rgba(30,58,95,.07);
                margin-bottom: 1rem;
            }
            .soft-panel {
                background: rgba(255,255,255,.92);
                border: 1px solid rgba(30,58,95,.08);
                border-radius: 18px;
                box-shadow: 0 8px 22px rgba(30,58,95,.05);
                padding: .8rem .9rem .35rem .9rem;
                margin-bottom: .9rem;
            }
            .stat-pill {
                background: white;
                border: 1px solid rgba(30,58,95,.08);
                border-radius: 16px;
                padding: .85rem 1rem;
                box-shadow: 0 8px 22px rgba(30,58,95,.05);
                text-align: center;
            }
            .stat-number {
                font-size: 1.55rem;
                font-weight: 700;
                color: #183153;
                line-height: 1.1;
            }
            .stat-label {
                font-size: .9rem;
                color: #66758a;
            }
            .stTextInput input,
            .stTextArea textarea,
            .stSelectbox div[data-baseweb="select"] > div,
            .stMultiSelect div[data-baseweb="select"] > div {
                border-radius: 14px !important;
            }
            .stButton > button {
                border-radius: 999px;
                font-weight: 600;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def normalize_bool(value) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def normalize_tags(tags_value: str) -> str:
    if pd.isna(tags_value):
        return ""
    parts = [t.strip().lower() for t in str(tags_value).split(",") if t.strip()]
    deduped = []
    for part in parts:
        if part not in deduped:
            deduped.append(part)
    return ", ".join(deduped)


def ensure_data_file():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        pd.DataFrame(columns=RECIPE_COLUMNS).to_csv(DATA_FILE, index=False)


@st.cache_data(ttl=10)
def load_recipes():
    ensure_data_file()
    df = pd.read_csv(DATA_FILE)
    for col in RECIPE_COLUMNS:
        if col not in df.columns:
            df[col] = ""
    df = df[RECIPE_COLUMNS].fillna("")
    df["tags"] = df["tags"].apply(normalize_tags)
    return df


def backup_file():
    if DATA_FILE.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copy2(DATA_FILE, BACKUP_DIR / f"recipes_backup_{timestamp}.csv")


def save_recipes(df):
    ensure_data_file()
    backup_file()
    out = df.copy()
    out["favorite"] = out["favorite"].apply(lambda x: "TRUE" if normalize_bool(x) else "FALSE")
    out["tags"] = out["tags"].apply(normalize_tags)
    out.to_csv(DATA_FILE, index=False)
    load_recipes.clear()


def stars(rating):
    try:
        rating = int(float(rating))
    except Exception:
        return ""
    rating = max(0, min(5, rating))
    return "★" * rating + "☆" * (5 - rating) if rating else ""


def get_all_tags(df):
    tags = set(DEFAULT_TAGS)
    if "tags" in df.columns:
        for value in df["tags"].tolist():
            for t in str(value).split(","):
                cleaned = t.strip().lower()
                if cleaned:
                    tags.add(cleaned)
    return sorted(tags)


def preview_text(text, limit=135):
    text = str(text).strip().replace("\n", " ")
    return text if len(text) <= limit else text[:limit].rstrip() + "..."


def clean_html_text(text):
    text = str(text)
    for junk in [
        '<div class="section-label">Ingredients</div>',
        '<div class="section-label">Instructions</div>',
        '<div class="preview-text">',
        "</div>",
    ]:
        text = text.replace(junk, "")
    return text.strip()


def render_header():
    left, right = st.columns([5, 1.8], vertical_alignment="center")
    with left:
        st.markdown('<div class="hero">', unsafe_allow_html=True)
        st.markdown(f"## {APP_TITLE}")
        st.caption(APP_TAGLINE)
        st.markdown("</div>", unsafe_allow_html=True)
    with right:
        label = "Admin unlocked" if st.session_state.get("admin") else "Browse mode"
        detail = (
            "Add, edit, and delete recipes below."
            if st.session_state.get("admin")
            else "Open any tile to view details."
        )
        st.markdown('<div class="hero">', unsafe_allow_html=True)
        st.markdown(f"**{label}**")
        st.caption(detail)
        st.markdown("</div>", unsafe_allow_html=True)


def render_stats(df, shown_count):
    fav_count = int(df["favorite"].apply(normalize_bool).sum()) if not df.empty else 0
    cols = st.columns(3)
    stats = [(len(df), "recipes saved"), (shown_count, "showing"), (fav_count, "favorites")]
    for col, (num, label) in zip(cols, stats):
        with col:
            st.markdown(
                f"""
                <div class="stat-pill">
                    <div class="stat-number">{num}</div>
                    <div class="stat-label">{label}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_recipe_tile(recipe):
    with st.container(border=True):
        top_left, top_right = st.columns([4, 1])
        with top_left:
            st.markdown(f"### {recipe.get('recipe_name', 'Untitled Recipe')}")
            meta = f"{recipe.get('category', 'Uncategorized')} • {recipe.get('prep_time', '')}"
            st.caption(meta)
        with top_right:
            rating_text = stars(recipe.get("rating", ""))
            if rating_text:
                st.markdown(f"**{rating_text}**")
            if normalize_bool(recipe.get("favorite", False)):
                st.markdown("**♥ Favorite**")

        tags = [t.strip() for t in str(recipe.get("tags", "")).split(",") if t.strip()]
        if tags:
            st.caption(" • ".join(tags[:4]))

        ingredients_preview = preview_text(clean_html_text(recipe.get("ingredients", "")), 120)
        instructions_preview = preview_text(clean_html_text(recipe.get("instructions", "")), 125)

        st.markdown("**Ingredients**")
        st.write(ingredients_preview or "No ingredients yet.")
        st.markdown("**Instructions**")
        st.write(instructions_preview or "No instructions yet.")


def admin_login():
    if "admin" not in st.session_state:
        st.session_state.admin = False

    with st.sidebar:
        st.markdown("## Admin")
        if st.session_state.admin:
            st.success("Admin unlocked")
            if st.button("Log out", use_container_width=True):
                st.session_state.admin = False
                st.rerun()
        else:
            password = st.text_input("Password", type="password")
            if st.button("Unlock admin", use_container_width=True):
                if password == st.secrets.get("admin_password"):
                    st.session_state.admin = True
                    st.rerun()
                else:
                    st.error("Wrong password")


def build_filters(df):
    st.markdown('<div class="soft-panel">', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([2.4, 1.2, 1.5, 1])

    with c1:
        search = st.text_input("Search", placeholder="Search by recipe name, ingredient, note, or tag")
    with c2:
        categories = ["All"] + sorted([c for c in df["category"].astype(str).unique().tolist() if c.strip()])
        category = st.selectbox("Category", categories)
    with c3:
        all_tags = ["All"] + get_all_tags(df)
        tag = st.selectbox("Tag", all_tags)
    with c4:
        favorites_only = st.checkbox("Favorites")

    st.markdown("</div>", unsafe_allow_html=True)
    return search, category, tag, favorites_only


def filter_recipes(df, search, category, tag, favorites_only):
    filtered = df.copy()

    if search:
        term = search.lower()
        filtered = filtered[
            filtered.apply(lambda row: term in " ".join(map(str, row.values)).lower(), axis=1)
        ]

    if category != "All":
        filtered = filtered[filtered["category"].astype(str) == category]

    if tag != "All":
        filtered = filtered[
            filtered["tags"].astype(str).str.lower().apply(
                lambda v: tag.lower() in [x.strip() for x in v.split(",") if x.strip()]
            )
        ]

    if favorites_only:
        filtered = filtered[filtered["favorite"].apply(normalize_bool)]

    sort_rating = pd.to_numeric(filtered["rating"], errors="coerce").fillna(0)
    filtered = (
        filtered.assign(_sort_rating=sort_rating)
        .sort_values(by=["favorite", "_sort_rating", "recipe_name"], ascending=[False, False, True])
        .drop(columns="_sort_rating")
    )

    return filtered


def parse_multiselect_tags(selected_tags, manual_tags):
    parts = [t.strip().lower() for t in selected_tags if t.strip()]
    if manual_tags.strip():
        parts.extend([t.strip().lower() for t in manual_tags.split(",") if t.strip()])

    deduped = []
    for part in parts:
        if part not in deduped:
            deduped.append(part)

    return ", ".join(deduped)


def admin_forms(recipes_df):
    st.divider()
    st.markdown("## Admin")
    tab1, tab2 = st.tabs(["Add recipe", "Edit recipe"])
    all_tags = get_all_tags(recipes_df)

    with tab1:
        with st.form("add_form", clear_on_submit=True):
            a, b, c = st.columns([2.2, 1.2, 1])
            with a:
                recipe_name = st.text_input("Recipe name*")
            with b:
                category = st.text_input("Category")
            with c:
                prep_time = st.text_input("Prep time", placeholder="20 min")

            d, e = st.columns(2)
            with d:
                rating = st.selectbox("Rating", ["", "1", "2", "3", "4", "5"])
            with e:
                favorite = st.checkbox("Favorite")

            tags_selected = st.multiselect("Tags", all_tags)
            tags_manual = st.text_input("Add custom tags", placeholder="asian, indian, quick")

            ingredients = st.text_area("Ingredients", height=180)
            instructions = st.text_area("Instructions", height=200)
            notes = st.text_area("Notes", height=120)
            source_link = st.text_input("Source link")

            submitted = st.form_submit_button("Save recipe", use_container_width=True)

            if submitted:
                if not recipe_name.strip():
                    st.error("Recipe name is required.")
                else:
                    new_row = pd.DataFrame(
                        [
                            {
                                "recipe_name": recipe_name.strip(),
                                "category": category.strip(),
                                "prep_time": prep_time.strip(),
                                "ingredients": ingredients.strip(),
                                "instructions": instructions.strip(),
                                "notes": notes.strip(),
                                "favorite": favorite,
                                "source_link": source_link.strip(),
                                "rating": rating,
                                "tags": parse_multiselect_tags(tags_selected, tags_manual),
                            }
                        ]
                    )
                    updated = pd.concat([recipes_df, new_row], ignore_index=True)
                    save_recipes(updated)
                    st.success("Recipe added.")
                    st.rerun()

    with tab2:
        if recipes_df.empty:
            st.info("No recipes to edit yet.")
        else:
            labels = recipes_df["recipe_name"].fillna("").astype(str).tolist()
            selected_recipe = st.selectbox("Choose recipe", labels)
            idx = recipes_df.index[recipes_df["recipe_name"].astype(str) == selected_recipe][0]
            current = recipes_df.loc[idx]

            current_tags = [t.strip() for t in str(current.get("tags", "")).split(",") if t.strip()]
            current_tags_in_list = [t for t in current_tags if t in all_tags]
            current_custom_tags = ", ".join([t for t in current_tags if t not in all_tags])

            with st.form("edit_form"):
                a, b, c = st.columns([2.2, 1.2, 1])
                with a:
                    recipe_name = st.text_input("Recipe name*", value=current.get("recipe_name", ""))
                with b:
                    category = st.text_input("Category", value=current.get("category", ""))
                with c:
                    prep_time = st.text_input("Prep time", value=current.get("prep_time", ""))

                d, e = st.columns(2)
                with d:
                    rating_options = ["", "1", "2", "3", "4", "5"]
                    current_rating = str(current.get("rating", ""))
                    rating = st.selectbox(
                        "Rating",
                        rating_options,
                        index=rating_options.index(current_rating) if current_rating in rating_options else 0,
                    )
                with e:
                    favorite = st.checkbox("Favorite", value=normalize_bool(current.get("favorite", False)))

                tags_selected = st.multiselect("Tags", all_tags, default=current_tags_in_list)
                tags_manual = st.text_input("Add custom tags", value=current_custom_tags)

                ingredients = st.text_area("Ingredients", value=clean_html_text(current.get("ingredients", "")), height=180)
                instructions = st.text_area("Instructions", value=clean_html_text(current.get("instructions", "")), height=200)
                notes = st.text_area("Notes", value=current.get("notes", ""), height=120)
                source_link = st.text_input("Source link", value=current.get("source_link", ""))

                x, y = st.columns(2)
                save = x.form_submit_button("Update recipe", use_container_width=True)
                delete = y.form_submit_button("Delete recipe", use_container_width=True)

                if save:
                    recipes_df.at[idx, "recipe_name"] = recipe_name.strip()
                    recipes_df.at[idx, "category"] = category.strip()
                    recipes_df.at[idx, "prep_time"] = prep_time.strip()
                    recipes_df.at[idx, "rating"] = rating
                    recipes_df.at[idx, "favorite"] = favorite
                    recipes_df.at[idx, "tags"] = parse_multiselect_tags(tags_selected, tags_manual)
                    recipes_df.at[idx, "ingredients"] = ingredients.strip()
                    recipes_df.at[idx, "instructions"] = instructions.strip()
                    recipes_df.at[idx, "notes"] = notes.strip()
                    recipes_df.at[idx, "source_link"] = source_link.strip()
                    save_recipes(recipes_df)
                    st.success("Recipe updated.")
                    st.rerun()

                if delete:
                    recipes_df = recipes_df.drop(index=idx).reset_index(drop=True)
                    save_recipes(recipes_df)
                    st.success("Recipe deleted.")
                    st.rerun()


inject_css()
admin_login()
recipes = load_recipes()

with st.sidebar:
    st.markdown("## Browse")
    st.caption("Filter recipes and tap a tile for details.")
    if st.button("Refresh recipes", use_container_width=True):
        load_recipes.clear()
        st.rerun()

render_header()
search, category, tag, favorites_only = build_filters(recipes)
filtered = filter_recipes(recipes, search, category, tag, favorites_only)
render_stats(recipes, len(filtered))
st.markdown("<div style='height:.6rem;'></div>", unsafe_allow_html=True)

if filtered.empty:
    st.info("No recipes match your filters.")
else:
    cols = st.columns(3)
    for i, (_, recipe) in enumerate(filtered.iterrows()):
        with cols[i % 3]:
            render_recipe_tile(recipe)
            with st.expander("Open recipe"):
                top1, top2 = st.columns([2, 1])
                with top1:
                    st.markdown(f"### {recipe.get('recipe_name', '')}")
                    st.caption(f"{recipe.get('category', '')} • {recipe.get('prep_time', '')}")
                with top2:
                    if str(recipe.get("rating", "")).strip():
                        st.markdown(f"**Rating:** {stars(recipe.get('rating', ''))}")
                    if normalize_bool(recipe.get("favorite", False)):
                        st.markdown("**Favorite** ♥")
                if str(recipe.get("tags", "")).strip():
                    st.markdown("**Tags:** " + recipe.get("tags", ""))
                st.markdown("**Ingredients**")
                st.text(clean_html_text(recipe.get("ingredients", "")))
                st.markdown("**Instructions**")
                st.text(clean_html_text(recipe.get("instructions", "")))
                if str(recipe.get("notes", "")).strip():
                    st.markdown("**Notes**")
                    st.write(recipe.get("notes", ""))
                if str(recipe.get("source_link", "")).strip():
                    st.link_button("Open source", recipe.get("source_link", ""))

if st.session_state.get("admin"):
    admin_forms(recipes)
