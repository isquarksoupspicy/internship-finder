"""Internship Finder backend. Run with: uvicorn app:app --reload"""
import json
import os
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import sources
import matcher

app = FastAPI()
PROFILE = "profile.json"


def load_profile():
    if os.path.exists(PROFILE):
        with open(PROFILE) as f:
            return json.load(f)
    return {"skills": [], "level": ""}


@app.get("/")
def home():
    return FileResponse("static/index.html")


@app.post("/api/refresh")
def refresh():
    jobs = sources.fetch_all()
    if jobs:
        sources.save_jobs(jobs)
    return {"saved": len(jobs)}


@app.get("/api/profile")
def get_profile():
    return load_profile()


@app.post("/api/resume")
async def upload_resume(file: UploadFile = File(...)):
    data = await file.read()
    if len(data) > 5_000_000:
        raise HTTPException(400, "File too large (max 5 MB)")
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(data)
        path = tmp.name
    try:
        text = matcher.read_resume(path)
    except Exception:
        raise HTTPException(400, "Could not read this file. Use a PDF, Word or .txt file")
    finally:
        os.remove(path)
    if len(text.strip()) < 30:
        raise HTTPException(400, "No text found. Scanned PDFs are not supported")
    profile = {"skills": matcher.find_skills(text), "level": matcher.find_level(text)}
    with open(PROFILE, "w") as f:
        json.dump(profile, f)
    return profile


@app.get("/api/facets")
def facets():
    jobs = sources.load_jobs()
    return {"countries": sorted({j["country"] for j in jobs}),
            "types": sorted({j["type"] for j in jobs})}


@app.get("/api/internships")
def search(city: str = "", mode: str = "", q: str = "", can_work_in: str = "",
           types: str = "", paid_only: bool = False, hide_unlikely: bool = True):
    jobs = sources.load_jobs()
    profile = load_profile()
    allowed = [c for c in can_work_in.split(",") if c]
    wanted = [t for t in types.split(",") if t]

    results = []
    for job in jobs:
        if allowed and not (job.get("global_remote") or job["country"] in allowed):
            continue
        if wanted and job["type"] not in wanted:
            continue
        if city and job["city"].lower() != city.lower():
            continue
        if mode and job["mode"] != mode:
            continue
        if q and q.lower() not in (job["title"] + " " + job["description"]).lower():
            continue
        if paid_only and job.get("pay") not in ("listed", "mentioned"):
            continue
        info = matcher.score_job(job, profile["skills"], profile["level"])
        if hide_unlikely and info["status"] == "Unlikely":
            continue
        results.append({**job, **info})

    order = {"Eligible": 0, "Partial": 1, "Unlikely": 2}
    results.sort(key=lambda r: (order[r["status"]], -r["match"]))
    return {"count": len(results), "results": results}
