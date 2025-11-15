from fastapi import APIRouter, UploadFile, File
import numpy as np
import cv2
import easyocr
import re

router = APIRouter()

# ------------------------------
# Optimized EasyOCR reader
# ------------------------------
reader = easyocr.Reader(['en'], gpu=True)

# ------------------------------
# UTILITIES
# ------------------------------
def _read_image(file: UploadFile):
    """Read uploaded file, convert to grayscale, and resize if needed."""
    contents = file.file.read()
    arr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Resize to max width 1024px
    h, w = gray.shape[:2]
    if w > 1024:
        scale = 1024 / w
        gray = cv2.resize(gray, (1024, int(h * scale)), interpolation=cv2.INTER_AREA)

    return gray

def _ocr_with_confidence(img_gray, keyword_mode=False):
    """Perform OCR and return extracted texts and average confidence."""
    if keyword_mode:
        img_gray = cv2.bilateralFilter(img_gray, 5, 50, 50)
    rgb = cv2.cvtColor(img_gray, cv2.COLOR_GRAY2RGB)
    results = reader.readtext(
        rgb,
        detail=1,
        paragraph=False,
        mag_ratio=1.0,
        text_threshold=0.25 if keyword_mode else 0.3,
        low_text=0.25 if keyword_mode else 0.3,
        link_threshold=0.3,
        contrast_ths=0.1,
        adjust_contrast=0.5
    )
    texts, confidences = [], []
    for (_, text, conf) in results:
        t = text.strip()
        if t:
            texts.append(t)
            confidences.append(conf)
    avg_conf = np.mean(confidences) * 100 if confidences else 0
    return texts, round(avg_conf, 2)

def _fix_text_punctuation(text: str) -> str:
    """Fix OCR punctuation: convert ; to , where appropriate and fix missing periods."""
    text = re.sub(r';(?=\s*[a-zA-Z0-9])', ',', text)
    text = re.sub(r'(?<!\d):(?!\d)', '.', text)  # replace colon with period if not numeric
    text = re.sub(r'\s*,\s*', ', ', text)
    text = re.sub(r'\s*\.\s*', '. ', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    if not text.endswith('.'):
        text += '.'
    return text

def abbreviate_department(dept_name: str) -> str:
    """
    Convert full department name to abbreviation.
    Example: "Department of Information Technology" -> "BSIT"
    """
    if not dept_name:
        return None
    
    # Split words and skip small words like 'of', 'the', 'and'
    skip_words = {"of", "the", "and"}
    words = [w for w in dept_name.split() if w.lower() not in skip_words]
    
    # Take first letter of each remaining word
    letters = [w[0].upper() for w in words]
    
    # Prefix with BS (for Bachelor of Science)
    return "BS" + "".join(letters[1:])  # skip 'D' in 'Department'



# ------------------------------
# 1) TITLE + AUTHORS
# ------------------------------
@router.post("/ocr/title-authors/")
async def ocr_title_authors(images: list[UploadFile] = File(...)):
    all_lines, confidences = [], []
    for f in images:
        img = _read_image(f)
        texts, avg_conf = _ocr_with_confidence(img)
        all_lines.extend(texts)
        confidences.append(avg_conf)
    title_lines, authors = [], []
    for line in all_lines:
        if re.search(r'([A-Z][a-z]+.*,)|([A-Z][a-z]+ [A-Z]\.)', line):
            authors.append(line)
        else:
            if not authors:
                title_lines.append(line)
    step_accuracy = round(np.mean(confidences), 2) if confidences else 0
    return {
        "title": " ".join(title_lines) if title_lines else None,
        "authors": ", ".join([a.rstrip(',') for a in authors]) if authors else None,
        "accuracy": step_accuracy
    }

# ------------------------------
# 2) PROGRAM / COURSE / DATE
# ------------------------------
@router.post("/ocr/program-date/")
async def ocr_program_date(images: list[UploadFile] = File(...)):
    all_lines, confidences = [], []
    for f in images:
        img = _read_image(f)
        texts, avg_conf = _ocr_with_confidence(img)
        all_lines.extend(texts)
        confidences.append(avg_conf)

    department_text, course, date_published = None, None, None

    for s in all_lines:
        s = s.strip()
        # Extract department and course
        if "department" in s.lower() and "college" in s.lower() and not department_text and not course:
            d_idx = s.lower().find("department")
            c_idx = s.lower().find("college")
            department_text = s[d_idx:c_idx].strip()
            course = s[c_idx:].strip()
            continue

        # Fallback: department on one line, college on another
        if not department_text and s.lower().startswith("department"):
            department_text = s
        elif department_text and not course and s.lower().startswith("college"):
            course = s

        # Extract date
        if not date_published:
            m = re.search(r"([A-Z][a-z]+ \d{4})", s)
            if m:
                date_published = m.group(1)

    # Convert department to abbreviation
    program_abbrev = abbreviate_department(department_text)

    # Combine program and course
    program_course = program_abbrev or department_text
    if course:
        program_course += f", {course}"

    step_accuracy = round(np.mean(confidences), 2) if confidences else 0

    return {
        "program_course": program_course or None,
        "date_published": date_published,
        "accuracy": step_accuracy
    }

# ------------------------------
# 3) ABSTRACT
# ------------------------------
@router.post("/ocr/abstract/")
async def ocr_abstract(images: list[UploadFile] = File(...)):
    all_lines, confidences = [], []
    for f in images:
        img = _read_image(f)
        texts, avg_conf = _ocr_with_confidence(img)
        all_lines.extend(texts)
        confidences.append(avg_conf)
    abstract_lines = []
    for line in all_lines:
        s = line.strip()
        if not s: continue
        if re.match(r"(?i)keywords?\s*[:\-]?", s): break
        if "keywords" in s.lower(): continue
        abstract_lines.append(s)
    abstract_text = " ".join(abstract_lines)
    abstract_text = _fix_text_punctuation(abstract_text)
    step_accuracy = round(np.mean(confidences), 2) if confidences else 0
    return {"abstract": abstract_text if abstract_text else None, "accuracy": step_accuracy}

# ------------------------------
# 4) KEYWORDS
# ------------------------------
@router.post("/ocr/keywords/")
async def ocr_keywords(images: list[UploadFile] = File(...)):
    all_lines, confidences = [], []
    for f in images:
        img = _read_image(f)
        texts, avg_conf = _ocr_with_confidence(img, keyword_mode=True)
        all_lines.extend(texts)
        confidences.append(avg_conf)
    keywords_list = []
    capture = False
    for s in all_lines:
        if "keyword" in s.lower():
            capture = True
            extracted = re.sub(r'(?i)keywords?\s*[:\-]?\s*', "", s)
            if extracted:
                keywords_list.append(extracted)
            continue
        if capture:
            if re.match(r"(?i)(abstract|chapter|introduction)", s):
                break
            keywords_list.append(s)
    # join lines, replace ; with , and remove duplicates
    keywords_text = ", ".join([k.replace(";", ",").strip() for k in keywords_list if k.strip()])
    keywords_text = re.sub(r'\s*,\s*', ', ', keywords_text)
    step_accuracy = round(np.mean(confidences), 2) if confidences else 0
    return {"keywords": keywords_text if keywords_text else None, "accuracy": step_accuracy}
