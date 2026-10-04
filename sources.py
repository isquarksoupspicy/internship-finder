"""Fetches internships from several free APIs and puts them in one format."""
import os
import re
import json
import html
import time
import requests
from dotenv import load_dotenv

load_dotenv()

COUNTRY_ALIASES = {
    "de": "Germany", "germany": "Germany", "deutschland": "Germany",
    "usa": "United States", "us": "United States", "united states": "United States",
    "uk": "United Kingdom", "united kingdom": "United Kingdom",
    "france": "France", "fr": "France", "india": "India", "canada": "Canada",
    "netherlands": "Netherlands", "spain": "Spain", "ireland": "Ireland",
    "singapore": "Singapore", "switzerland": "Switzerland", "austria": "Austria",
    "worldwide": "Worldwide", "europe": "Europe",
}
CITY_TO_COUNTRY = {
    "berlin": "Germany", "münchen": "Germany", "munich": "Germany",
    "hamburg": "Germany", "frankfurt": "Germany", "darmstadt": "Germany",
    "köln": "Germany", "paris": "France", "london": "United Kingdom",
    "amsterdam": "Netherlands", "madrid": "Spain", "dublin": "Ireland",
    "zurich": "Switzerland", "vienna": "Austria", "wien": "Austria",
    "bangalore": "India", "bengaluru": "India", "chennai": "India",
}
TYPE_KEYWORDS = {
    "Data / AI": ["data", "machine learning", "analytics", "ai "],
    "Software / Engineering": ["software", "developer", "engineer", "backend", "frontend", "cloud", "devops"],
    "Biotech / Research": ["bio", "genom", "laborator", "research", "pharma", "clinical", "chemi"],
    "Marketing / PR / Content": ["marketing", "social media", "content", "communications", "brand", "pr "],
    "Design": ["design", "ux", "creative"],
    "Business / Finance": ["business", "finance", "sales", "consult", "product manager", "operations"],
}
ADZUNA_COUNTRIES = {
    "in": "India", "gb": "United Kingdom", "us": "United States",
    "ca": "Canada", "au": "Australia", "de": "Germany", "fr": "France",
    "nl": "Netherlands", "sg": "Singapore", "it": "Italy", "es": "Spain",
    "at": "Austria", "pl": "Poland", "br": "Brazil",
}
CURRENCY = {
    "India": "₹", "United Kingdom": "£", "United States": "$", "Canada": "$",
    "Australia": "$", "Germany": "€", "France": "€", "Netherlands": "€",
    "Singapore": "$", "Italy": "€", "Spain": "€", "Austria": "€",
    "Poland": "zł", "Brazil": "R$",
}
INDIA_EXTRA_WORDS = ["data intern", "python intern", "research intern",
                     "biotech intern", "machine learning intern", "bioinformatics intern"]
JOOBLE_SEARCHES = [
    ("intern", "India"), ("internship", "India"),
    ("intern", "Chennai"), ("intern", "Bangalore"), ("intern", "Mumbai"),
    ("intern", "Delhi"), ("intern", "Hyderabad"), ("intern", "Pune"),
    ("data intern", "India"), ("python intern", "India"),
    ("research intern", "India"), ("biotech intern", "India"),
    ("machine learning intern", "India"), ("bioinformatics intern", "India"),
    ("intern", "United Kingdom"), ("intern", "United States"),
    ("intern", "Canada"), ("intern", "Australia"),
    ("intern", "Singapore"), ("intern", "Germany"),
]


def is_internship(title):
    pattern = r"\b(intern|interns|internship|trainee|working student)\b"
    return re.search(pattern, title or "", re.IGNORECASE) is not None


def clean_text(text):
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()[:2000]


def split_location(location):
    country, city = "Unknown", ""
    for part in [p.strip() for p in (location or "").split(",") if p.strip()]:
        if part.lower() in COUNTRY_ALIASES:
            if country == "Unknown":
                country = COUNTRY_ALIASES[part.lower()]
        elif city == "":
            city = part
    if country == "Unknown" and city.lower() in CITY_TO_COUNTRY:
        country = CITY_TO_COUNTRY[city.lower()]
    return country, city


def guess_type(text):
    text = " " + text.lower() + " "
    best_type, best_score = "Other", 0
    for job_type, words in TYPE_KEYWORDS.items():
        score = sum(1 for w in words if w in text)
        if score > best_score:
            best_type, best_score = job_type, score
    return best_type


def build_job(title, company, location, description, url, source, remote):
    description = clean_text(description)
    country, city = split_location(location)
    if "hybrid" in (title + " " + description).lower():
        mode = "Hybrid"
    elif remote:
        mode = "Online"
    else:
        mode = "Offline"
    if mode == "Online":
        city = ""
    global_remote = bool(remote and re.search(r"worldwide|anywhere|global|\basia\b|apac|india",
                                              location or "", re.IGNORECASE))
    return {
        "title": title, "company": company, "country": country, "city": city,
        "mode": mode, "type": guess_type(title + " " + description[:400]),
        "description": description, "url": url, "source": source,
        "global_remote": global_remote, "pay": "unknown", "pay_text": "",
    }


def add_pay(job, salary_min=None, salary_max=None, predicted=False, salary_text=""):
    symbol = CURRENCY.get(job["country"], "")
    text = (job["title"] + " " + job["description"]).lower()
    if (salary_min or salary_max) and not predicted:
        low = salary_min or salary_max
        high = salary_max or salary_min
        job["pay"] = "listed"
        if low == high:
            job["pay_text"] = f"{symbol}{low:,.0f} per year"
        else:
            job["pay_text"] = f"{symbol}{low:,.0f} to {symbol}{high:,.0f} per year"
    elif salary_text:
        job["pay"], job["pay_text"] = "listed", salary_text
    elif re.search(r"\b(unpaid|no stipend|voluntary)\b", text):
        job["pay"] = "unpaid"
    elif re.search(r"stipend|paid internship|compensation|salary|per month|/month|a month", text):
        job["pay"], job["pay_text"] = "mentioned", "Pay mentioned in the description"


def fetch_remotive():
    response = requests.get("https://remotive.com/api/remote-jobs",
                            params={"search": "intern"}, timeout=20)
    results = []
    for job in response.json()["jobs"]:
        if is_internship(job["title"]):
            built = build_job(job["title"], job["company_name"],
                              job["candidate_required_location"], job["description"],
                              job["url"], "Remotive", remote=True)
            add_pay(built, salary_text=job.get("salary", ""))
            results.append(built)
    return results


def fetch_arbeitnow():
    results = []
    for page in [1, 2, 3]:
        response = requests.get("https://www.arbeitnow.com/api/job-board-api",
                                params={"page": page}, timeout=20)
        for job in response.json()["data"]:
            if is_internship(job["title"]):
                built = build_job(job["title"], job["company_name"], job["location"],
                                  job["description"], job["url"], "Arbeitnow",
                                  remote=job["remote"])
                add_pay(built)
                results.append(built)
    return results


def fetch_adzuna():
    app_id = os.getenv("ADZUNA_APP_ID")
    app_key = os.getenv("ADZUNA_APP_KEY")
    if not app_id or not app_key:
        print("Adzuna keys missing, skipping")
        return []
    tasks = [(c, w, 1) for c in ADZUNA_COUNTRIES for w in ["intern", "internship"]]
    tasks += [("in", "internship", p) for p in [2, 3]]
    tasks += [("in", w, 1) for w in INDIA_EXTRA_WORDS]

    results, seen = [], set()
    for code, word, page in tasks:
        try:
            data = requests.get(
                f"https://api.adzuna.com/v1/api/jobs/{code}/search/{page}",
                params={"app_id": app_id, "app_key": app_key,
                        "results_per_page": 50, "what": word}, timeout=20).json()
        except Exception as e:
            print("Adzuna failed for", code, word, e)
            continue
        time.sleep(0.4)
        for job in data.get("results", []):
            if not is_internship(job["title"]) or job["redirect_url"] in seen:
                continue
            seen.add(job["redirect_url"])
            area = job["location"].get("area", [])
            location = job["location"]["display_name"]
            text = (job["title"] + " " + job["description"]).lower()
            built = build_job(job["title"], job.get("company", {}).get("display_name", "Unknown"),
                              location, job["description"], job["redirect_url"], "Adzuna",
                              remote="remote" in text)
            built["country"] = ADZUNA_COUNTRIES[code]
            if built["mode"] != "Online":
                built["city"] = area[-1] if len(area) >= 3 else location.split(",")[0]
            predicted = str(job.get("salary_is_predicted", "0")) == "1"
            add_pay(built, job.get("salary_min"), job.get("salary_max"), predicted)
            results.append(built)
    return results


def fetch_jooble():
    key = os.getenv("JOOBLE_API_KEY")
    if not key:
        print("Jooble key missing, skipping")
        return []
    results, seen = [], set()
    for word, place in JOOBLE_SEARCHES:
        try:
            data = requests.post(f"https://jooble.org/api/{key}",
                                 json={"keywords": word, "location": place, "page": 1},
                                 timeout=20).json()
        except Exception as e:
            print("Jooble failed for", word, place, e)
            continue
        time.sleep(0.4)
        for job in data.get("jobs", []):
            link = job.get("link", "")
            if not is_internship(job.get("title", "")) or link in seen:
                continue
            seen.add(link)
            location = job.get("location", "") or place
            text = (job.get("title", "") + " " + job.get("snippet", "")).lower()
            built = build_job(job.get("title", ""), job.get("company", "Unknown"), location,
                              job.get("snippet", ""), link, "Jooble", remote="remote" in text)
            built["country"] = place if place in CURRENCY else split_location(location)[0]
            if built["mode"] != "Online":
                built["city"] = location.split(",")[0].strip()
            add_pay(built, salary_text=(job.get("salary") or "").strip())
            results.append(built)
    return results


def remove_duplicates(jobs):
    seen, unique = set(), []
    for job in jobs:
        key = (job["title"].lower().strip(), job["company"].lower().strip(), job["country"])
        if key not in seen:
            seen.add(key)
            unique.append(job)
    return unique


def fetch_all():
    jobs = []
    for name, fn in [("Remotive", fetch_remotive), ("Arbeitnow", fetch_arbeitnow),
                     ("Adzuna", fetch_adzuna), ("Jooble", fetch_jooble)]:
        try:
            found = fn()
            print(name, "gave", len(found), "internships")
            jobs += found
        except Exception as e:
            print(name, "failed:", e)
    return remove_duplicates(jobs)


def save_jobs(jobs, path="internships.json"):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)


def load_jobs(path="internships.json"):
    """Uses your fetched listings, or the small sample file if you haven't fetched yet."""
    if not os.path.exists(path):
        path = "sample_internships.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    jobs = fetch_all()
    if jobs:
        save_jobs(jobs)
    india = [j for j in jobs if j["country"] == "India"]
    print("Saved", len(jobs), "internships | India:", len(india),
          "| with pay info:", len([j for j in jobs if j["pay"] in ("listed", "mentioned")]))
