# ASK MY CFO — M1 Automation

Runs entirely on GitHub — no server needed. GitHub Pages hosts the frontend, GitHub Actions runs the pipeline.

## How It Works

```
You upload PDFs → GitHub Actions runs the pipeline → You download Excel reports

┌──────────────┐     ┌────────────────────────┐     ┌──────────────┐
│ GitHub Pages  │────▶│  GitHub Actions Runner  │────▶│  Artifacts   │
│ (frontend)    │     │  1. Detect pages        │     │  (download)  │
│              │     │  2. Extract tables       │     │              │
│              │     │  3. GPT-4o mapping       │     │              │
└──────────────┘     └────────────────────────┘     └──────────────┘
```

## Setup (one-time, 5 minutes)

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "initial"
git remote add origin https://github.com/YOUR_USERNAME/ask-my-cfo.git
git branch -M main
git push -u origin main
```

### 2. Add OpenAI secret

Go to your repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

- Name: `OPENAI_API_KEY`
- Value: `sk-...` (your OpenAI key)

### 3. Enable GitHub Pages

Go to **Settings** → **Pages** → Source: **GitHub Actions**

### 4. Create Personal Access Token

Go to https://github.com/settings/tokens/new
- Note: `ASK MY CFO`
- Scopes: ✅ `repo`, ✅ `workflow`
- Click **Generate token**, copy it

### 5. Open the frontend

Your frontend is live at: `https://YOUR_USERNAME.github.io/ask-my-cfo/`

Enter your repo name and token, click **Save**.

## Usage

### Option A: Web UI (recommended)

1. Open your GitHub Pages URL
2. Drop PDF files
3. Click **Upload & Run Pipeline**
4. Wait for completion, download output

### Option B: Git push

```bash
# Copy PDFs into input/
cp annual_report.pdf input/

# Push
git add input/
git commit -m "Add PDFs"
git push
```

Then go to **Actions** tab → latest run → download **Artifacts**.

### Option C: Manual trigger

Go to **Actions** tab → **Run Pipeline** → **Run workflow**

## Project Structure

```
├── docs/
│   └── index.html           # Frontend (→ GitHub Pages)
├── input/                    # Drop PDFs here
├── modules/
│   ├── page_detector.py     # Stage 1
│   ├── extract_tables.py    # Stage 2
│   └── bs_pl_mapper.py      # Stage 3
├── run_pipeline.py           # Pipeline runner
├── requirements.txt
└── .github/workflows/
    ├── pipeline.yml          # Runs pipeline on push to input/
    └── pages.yml             # Deploys frontend
```

## Free Tier Limits

- **GitHub Actions**: 2,000 minutes/month (free for public repos, unlimited)
- **Artifacts**: stored 90 days, up to 500 MB
- **GitHub Pages**: free for public repos

A typical annual report takes 2-4 minutes to process.
