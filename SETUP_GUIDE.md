# Setup Guide

## 1. Create a new GitHub repository
Create a new empty repository named:
`equity-research-intelligence-agent`

Keep the existing `filing-signal-agent` repository untouched.

Do not initialize the new repository with a README, .gitignore or license because those files are already included here.

## 2. Upload the project
Extract this ZIP and upload **the contents** into the root of the new GitHub repository. `app.py` and `requirements.txt` must be at repository root.

## 3. Streamlit Community Cloud
Create a new Streamlit app from the new GitHub repository.
- Branch: `main`
- Main file: `app.py`

## 4. Streamlit Secrets
Add:
```toml
GEMINI_API_KEY = "YOUR_NEW_GEMINI_KEY"
GEMINI_MODEL = "gemini-2.5-flash"
```
Never commit the API key to GitHub.

## 5. Use
Open the app, choose NSE or BSE, type any company, and click **RUN LIVE RESEARCH**.
