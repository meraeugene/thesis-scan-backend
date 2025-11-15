from fastapi import APIRouter, UploadFile, File
import numpy as np
import cv2
import easyocr
import re

router = APIRouter()

# ------------------------------
# Optimized EasyOCR reader
# ------------------------------
reader = easyocr.Reader(['en'], gpu=False)

# ------------------------------
# UTILITIES
# ------------------------------
def _read_image(file: UploadFile, max_width=800):
    """
    Fast image preprocessing for OCR:
    - Resize early
    - Convert to grayscale
    - Apply light thresholding
    """
    # 1️⃣ Read bytes
    contents = file.file.read()
    
    # 2️⃣ Decode image
    arr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    
    # 3️⃣ Resize if too wide
    h, w = img.shape[:2]
    if w > max_width:
        scale = max_width / w
        img = cv2.resize(img, (max_width, int(h * scale)), interpolation=cv2.INTER_AREA)
    
    # 4️⃣ Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 5️⃣ Fast denoising and threshold
    gray = cv2.medianBlur(gray, 3)  # lighter than Gaussian
    _, gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    return gray


def _ocr_with_confidence(img_gray, keyword_mode=False):
    """
    Fast EasyOCR for speed:
    - Use lower mag_ratio
    - Reduce thresholds for faster text detection
    """
    # Optional: lightweight denoise for keywords
    if keyword_mode:
        img_gray = cv2.bilateralFilter(img_gray, 3, 30, 30)

    # Convert to RGB for EasyOCR
    if len(img_gray.shape) == 2:
        img_rgb = cv2.cvtColor(img_gray, cv2.COLOR_GRAY2RGB)
    else:
        img_rgb = img_gray

    # OCR
    results = reader.readtext(
        img_rgb,
        detail=1,
        paragraph=False,
        mag_ratio=0.4,              # smaller magnification = faster
        text_threshold=0.2,         # slightly lower to detect faint text
        low_text=0.2,               # faster detection
        link_threshold=0.25,        # lower for speed
        contrast_ths=0.05,          # minimal contrast adjustment
        adjust_contrast=0.4
    )

    texts, confidences = [], []
    for _, text, conf in results:
        text = text.strip()
        if text:
            texts.append(text)
            confidences.append(conf)

    avg_conf = round(np.mean(confidences) * 100, 2) if confidences else 0
    return texts, avg_conf



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
