import re
import html
import zipfile
from pypdf import PdfReader

SKILLS = [
    "python", "java", "javascript", "c++", "sql", "matlab", "html", "css",
    "react", "flask", "fastapi", "django", "streamlit", "git", "github", "docker",
    "linux", "aws", "tensorflow", "pytorch", "pandas", "numpy", "matplotlib",
    "scikit-learn", "machine learning", "deep learning", "nlp", "llm",
    "generative ai", "gemini api", "openai api", "prompt engineering", "api",
    "artificial intelligence", "data analysis", "data science",
    "data visualization", "statistics", "tableau", "power bi", "excel",
    "signal processing", "ecg", "biomedical", "healthcare",
    "bioinformatics", "computational biology", "genomics", "proteomics",
    "biotechnology", "molecular biology", "cell culture", "pcr", "crispr",
    "sequencing", "biopython", "drug discovery", "microbiology", "biochemistry",
    "public relations", "social media", "content writing", "copywriting",
    "seo", "marketing", "canva", "figma", "video editing", "communication",
    "leadership", "project management", "research", "latex",
]


def read_resume(file_path):
    """Reads PDF, Word (.docx) or text, by checking what the file really is."""
    with open(file_path, "rb") as f:
        start = f.read(4)
    if start == b"PK\x03\x04":
        with zipfile.ZipFile(file_path) as z:
            xml = z.read("word/document.xml").decode("utf-8", errors="ignore")
        xml = xml.replace("</w:p>", "\n")
        return html.unescape(re.sub(r"<[^>]+>", "", xml))
    if start == b"%PDF":
        reader = PdfReader(file_path)
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    with open(file_path, encoding="utf-8", errors="ignore") as f:
        return f.read()


def find_skills(text):
    found = []
    for skill in SKILLS:
        pattern = r"(?<![\w+#])" + re.escape(skill) + r"(?![\w+#])"
        if re.search(pattern, text, re.IGNORECASE):
            found.append(skill)
    return found


def find_level(text):
    t = text.lower()
    if re.search(r"\bph\.?d\b|doctoral", t):
        return "PhD"
    if re.search(r"\bm\.?tech\b|\bm\.?sc\b|\bmaster|\bmba\b", t):
        return "Master"
    if re.search(r"\bb\.?tech\b|\bb\.?sc\b|\bbachelor|undergraduate", t):
        return "Bachelor"
    return ""


def score_job(job, skills, level):
    text = job["title"] + " " + job["description"]
    needed = set(find_skills(text))
    have = set(skills)
    matched = sorted(needed & have)
    missing = sorted(needed - have)

    percent = 100 * len(matched) / len(needed) if needed else (35 if have else 0)
    if any(s in job["title"].lower() for s in have):
        percent += 15
    percent = min(100, round(percent))

    t = text.lower()
    note = ""
    if level != "PhD" and re.search(r"(ph\.?d|doctoral)[^.]{0,40}(student|candidate|required)", t):
        note = "Looks like it needs a PhD student"
    elif level in ("Bachelor", "") and re.search(r"master'?s?[^.]{0,40}(student|required|degree)", t):
        note = "Looks like it needs a Master's student"

    if note:
        status = "Unlikely"
    elif percent >= 40:
        status = "Eligible"
    else:
        status = "Partial"
    return {"match": percent, "status": status, "matched": matched,
            "missing": missing[:8], "note": note}
