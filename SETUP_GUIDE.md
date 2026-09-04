# GitHub + Streamlit setup — exact steps

## 1. Create a new GitHub repository

Go to GitHub and sign in.

1. Click the **+** button in the top-right.
2. Click **New repository**.
3. Repository name: `equity-research-intelligence-agent`
4. Description: `AI-powered equity research intelligence dashboard`
5. Choose **Private** if this is for your own project, or **Public** if you need to showcase the code.
6. Leave **Add a README file** unchecked because this ZIP already contains a README.
7. Leave `.gitignore` as **None** because the ZIP already contains one.
8. Click **Create repository**.

## 2. Upload the ZIP contents

GitHub's web uploader can accept folders through drag-and-drop in many browsers, but the most reliable route is GitHub Desktop or Git command line.

### Easiest route: GitHub Desktop

1. Install GitHub Desktop.
2. Sign in to your GitHub account.
3. Clone the new empty repository.
4. Unzip this project ZIP.
5. Copy the **contents** of the unzipped folder into the cloned repository folder.
6. Open GitHub Desktop.
7. You should see the new files under Changes.
8. Commit message: `Initial equity research intelligence agent`.
9. Click **Commit to main**.
10. Click **Push origin**.

## 3. Deploy to Streamlit Community Cloud

1. Open Streamlit Community Cloud.
2. Sign in with GitHub.
3. Click **Create app**.
4. Select your new repository.
5. Branch: `main`.
6. Main file path: `app.py`.
7. Deploy.

## 4. Add the Gemini key

After the app is created:

1. Open the app.
2. Open **Manage app** / app settings.
3. Find **Secrets**.
4. Paste:

```toml
GEMINI_API_KEY = "YOUR_NEW_KEY"
GEMINI_MODEL = "gemini-2.5-flash"
WATCHLIST = "AAPL,MSFT,NVDA,JPM,RELIANCE.NS"
MAX_COMPANIES_PER_RUN = "5"
```

5. Save.
6. Reboot/re-run the app if requested.

## 5. Never put the API key in GitHub

Do not put the key in:
- `app.py`
- `config.py`
- `README.md`
- GitHub Issues
- screenshots
- `.streamlit/config.toml`

The `.gitignore` already excludes `.streamlit/secrets.toml`.
