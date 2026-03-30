# Hope & Sarah's Recipe Box — Google Sheets version

This version is public view-only.
You and Hope update recipes in a shared Google Sheet from anywhere.

## What changed
- The app no longer saves to `recipes.csv`
- It reads recipes from a Google Sheet named `Recipes`
- Visitors can browse only
- You and Hope edit the Google Sheet directly

## Sheet columns
Your Google Sheet tab should be named `Recipes` and should have these columns in row 1:

`recipe_name, category, prep_time, ingredients, instructions, notes, favorite, source_link`

A starter CSV template is included as `google_sheet_template.csv`.

## Local run
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Secrets
Create `.streamlit/secrets.toml` from `sample_secrets.toml`.

### Public sheet
If you make the sheet viewable to anyone with the link, you only need:
```toml
[connections.gsheets]
spreadsheet = "YOUR_GOOGLE_SHEET_URL"
```

### Private sheet
If you want the sheet private, use a Google service account and paste the key values into `secrets.toml`.

## Deploy on Streamlit Community Cloud
- Upload this project to GitHub
- In Streamlit Community Cloud, connect the repo
- Add the same secrets under your app settings
- Deploy `app.py`
