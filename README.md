# 🎓 Internship Finder

Finding internships is honestly one of those things that sounds easy until you actually start doing it.

You end up opening a million tabs, checking if you're even eligible, figuring out whether the internship is actually related to what you want to do, and then trying to remember where you found it.

So I made **Internship Finder** to make that process a little less annoying.

Basically, you upload your resume, tell it where you're able to apply and what fields you're interested in, and it finds internships and checks how well they match your profile.

---

## What does it actually do?

You upload your **resume** and the app looks for things like your skills and degree level.

Then you can choose things like:

- 🌎 Countries you can apply to
- 🧬 Fields you're interested in
- 📍 City
- 💻 Online / Hybrid / Offline
- 🔎 Keywords
- 💰 Whether you only want internships with stipend/pay information

For every internship, it gives you a rough idea of how well it matches you:

**Eligible** → looks like a good match

**Partial** → you match some of it, but there are things you're missing

**Unlikely** → probably not worth prioritising right now

It also shows your **match percentage**, the skills you already have, and some **skills you could work on**.

And when you actually find something you like, the **Apply** button takes you to the original listing.

---

## Where does it get the internships from?

I connected it to a few different job APIs:

- **Remotive**
- **Arbeitnow**
- **Adzuna**
- **Jooble**

The app combines the listings and removes duplicates, so you don't keep seeing the same internship over and over.

Some of these APIs need an API key and some don't.

---

## 🧠 How does the matching work?

This part is probably the most interesting part of the project for me.

The app takes the skills it finds in your resume and compares them with the skills mentioned in each internship listing.

For example, if an internship asks for:

```text
Python
SQL
Machine Learning
Git
```

and your resume has:

```text
Python
Git
```

the app can recognise that you already have some of the required skills and show you what you're missing.

It also looks at your degree level. So if an internship specifically requires a PhD and you're currently doing a Bachelor's degree, it won't pretend that you're a perfect match.

It's **not supposed to decide whether you should apply or not**. It's just meant to help you quickly figure out which listings are worth looking at.

---

## 🛠️ What I used to build it

- **Python**
- **FastAPI** — backend
- **HTML/CSS/JavaScript** — frontend
- **APIs** — internship data
- **PDF / Word / text parsing** — resume reading
- **JSON** — sample data and profile information

---

## 📂 Project structure

```text
internship-finder/
│
├── app.py
├── sources.py
├── matcher.py
├── sample_internships.json
├── requirements.txt
├── .env.example
├── .gitignore
│
└── static/
    └── index.html
```

### What the main files do

**`app.py`**  
This is basically where everything comes together. It runs the backend and connects the different parts of the app.

**`sources.py`**  
Gets internship listings from the different APIs and cleans the data.

**`matcher.py`**  
Reads the resume and compares its skills with the requirements of each internship.

**`static/index.html`**  
The actual webpage you interact with.

**`sample_internships.json`**  
A small sample dataset so the app can be tested without immediately fetching new listings.

---

## 🚀 Running it locally

Clone the repository:

```bash
git clone <your-repo-url>
cd internship-finder
```

Create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

On Windows:

```bash
venv\Scripts\activate
```

Install the requirements:

```bash
pip install -r requirements.txt
```

Create your `.env` file:

```bash
cp .env.example .env
```

Then add your API keys.

Start the app:

```bash
uvicorn app:app --reload
```

Then open:

**http://127.0.0.1:8000**

Upload your resume and click **Fetch latest listings**.

There's also a small sample dataset included, so you can test the app before fetching live listings.

---

## 🔑 API keys

The project uses:

**Adzuna**  
https://developer.adzuna.com

**Jooble**  
https://jooble.org/api/about

Remotive and Arbeitnow don't require API keys.

The free API tiers have limits, so this isn't really meant to continuously hammer the APIs. Fetching listings once or twice a day is enough for normal use.

---

## 🔒 Privacy

One thing I specifically wanted to avoid was sending someone's entire resume somewhere unnecessarily.

The resume is processed locally and only the detected skills are saved in `profile.json`.

Your `.env` file and `profile.json` are also included in `.gitignore`, so they aren't uploaded to GitHub.

---

## ⚠️ Current limitations

This isn't a perfect internship search engine (yet).

A few things to keep in mind:

- Free APIs don't contain every internship that exists
- Some internships don't mention their salary/stipend
- Scanned/image-only PDFs aren't currently supported
- The matching system is only a guide, so you should still read the actual internship description before applying

---

## 💭 Why I made this

I'm a student looking for internships too, and I got tired of the whole process being:

**search → open 17 tabs → read requirements → realise I'm not eligible → repeat**

I wanted to make something that could do at least some of that sorting for me.

It also gave me a reason to actually learn how APIs, backend code, data handling and matching logic work instead of just learning them separately through tutorials.

So this project is basically me trying to solve a problem I was having while learning how to build things.

And honestly, that's probably how I want to keep learning — **find something annoying, build something to fix it, and figure out the technology along the way.**
