# 🎓 Internship Finder

Finding internships is honestly annoying.

You end up going through a bunch of websites, opening random listings, checking if you're even eligible, figuring out whether the internship matches your skills, and then doing it all over again.

So I made **Internship Finder** to make that process a little easier.

You upload your resume, choose what you're interested in and where you can apply, and the app finds internships and gives you a rough idea of how well they match your profile.

### 🌐 Try it out

**[→ Open Internship Finder](YOUR-RENDER-URL-HERE)**

---

## What does it actually do?

You upload your **resume** and the app looks for things like your skills and degree level.

You can then choose:

- 🌎 Countries you can apply to
- 🧬 Fields you're interested in
- 📍 City
- 💻 Online / Hybrid / Offline
- 🔎 Keywords
- 💰 Whether you want internships with stipend/pay information

For each internship, it gives you:

- **Eligible / Partial / Unlikely** match
- A match percentage
- Skills you already have
- Skills you might need to build
- The original listing so you can actually apply

---

## Where does it get internships from?

I connected it to different internship/job APIs:

- **Adzuna**
- **Jooble**
- **Arbeitnow**
- **Remotive**

The app combines the listings and removes duplicates.

---

## 🧠 How does the matching work?

The basic idea is pretty simple.

The app takes the skills it finds in your resume and compares them with the skills mentioned in an internship listing.

So if an internship asks for:

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

the app can show you that you already match some of the requirements and what you could work on.

It also checks things like degree level. So if something specifically requires a PhD and you're doing a Bachelor's, it won't pretend you're a perfect match.

It's not meant to decide whether you **shouldn't** apply. It's just meant to help you sort through internships faster.

---

## 🛠️ What I used

- Python
- FastAPI
- HTML / CSS / JavaScript
- REST APIs
- PDF / Word / text parsing
- JSON

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

### The main files

**`app.py`**  
The backend that brings everything together.

**`sources.py`**  
Gets internship listings from the different APIs and puts them into one format.

**`matcher.py`**  
Reads the resume and compares its skills with internship requirements.

**`static/index.html`**  
The actual webpage.

---

## 🚀 Run it locally

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

Install the requirements:

```bash
pip install -r requirements.txt
```

Create your `.env`:

```bash
cp .env.example .env
```

Add your own API keys and run:

```bash
uvicorn app:app --reload
```

Then open:

```text
http://127.0.0.1:8000
```

---

## 🔒 Privacy

The resume is processed locally and only the detected skills are saved.

API keys and the generated profile are kept out of GitHub using `.gitignore`.

---

## ⚠️ Limitations

This isn't a perfect internship search engine.

- Free APIs don't contain every internship
- Some listings don't mention pay
- Scanned/image-only PDFs aren't currently supported
- The matching system is only a guide, so you should still read the actual internship description

---

## 💭 Why I made it

I'm a student looking for internships too, and I got tired of the whole:

**search → open 20 tabs → read requirements → realise I'm not eligible → repeat**

cycle.

I wanted to build something that could do some of that sorting for me.

It also gave me a reason to actually learn about APIs, backend development, data handling and matching logic by **building something I would genuinely use**.

And honestly, that's how I want to keep learning — find something annoying, build something to fix it, and figure out the technology along the way.
