# 🎓 Internship Finder

A simple web tool that finds internships worldwide and shows which ones fit **your resume**, with pay info where available.

## Features
- Upload your resume (PDF, Word or text). Skills and degree level are detected automatically
- Choose the countries you can apply from. Jobs you can't apply to are hidden (remote jobs open worldwide are always shown)
- Pick the fields you like. Your choices are remembered in your browser
- Filter by city, Online / Hybrid / Offline and keyword
- "Only with stipend / pay info" filter
- Each listing shows an **Eligible / Partial / Unlikely** tag, a match %, matching skills and skills to build
- Apply button opens the original listing
- Sources: Remotive, Arbeitnow, Adzuna and Jooble. Duplicates are removed

## Setup
```bash
git clone <your-repo-url>
cd internship-finder
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # then add your free keys (see below)
uvicorn app:app --reload
```
Open http://127.0.0.1:8000, upload your resume, then click **Fetch latest listings**.
It works with a small sample dataset before you fetch.

## Free API keys (put them in `.env`)
- **Adzuna** (14 countries): https://developer.adzuna.com
- **Jooble** (60+ countries, strong in India): https://jooble.org/api/about

Remotive and Arbeitnow need no key. Free tiers have limits, so fetch once or twice a day.

## How matching works
`matcher.py` finds known skills in your resume and in each listing, then compares them. A listing that needs a PhD when you're a Bachelor student is marked Unlikely. It is a guide, so always read the listing too. Add your own skills to the `SKILLS` list.

## Project structure
```
app.py                 backend (FastAPI)
sources.py             fetches and cleans listings from the APIs
matcher.py             resume reading and matching
static/index.html      the web page
sample_internships.json  sample data
```

## Privacy
Your resume is processed locally. Only detected skills are saved (`profile.json`), and it is git-ignored along with `.env`.

## Limitations
- Free APIs don't cover every listing, and many postings don't state pay
- Scanned (image-only) PDFs are not supported
