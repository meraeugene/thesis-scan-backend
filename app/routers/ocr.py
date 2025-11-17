from fastapi import APIRouter, UploadFile, File
import numpy as np
import cv2
import re

router = APIRouter()

# ------------------------------
# Try to import PaddleOCR only if available
# ------------------------------
try:
    from paddleocr import PaddleOCR
    OCR_AVAILABLE = True
    ocr = PaddleOCR(use_angle_cls=True, lang='en')
except ImportError:
    OCR_AVAILABLE = False
    ocr = None

# ------------------------------
# UTILITIES
# ------------------------------
def _read_image(file: UploadFile):
    contents = file.file.read()
    arr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    h, w = img.shape[:2]
    if w > 1024:
        scale = 1024 / w
        img = cv2.resize(img, (1024, int(h * scale)), interpolation=cv2.INTER_AREA)
    return img

def _ocr_image(img):
    if not OCR_AVAILABLE:
        return [], 0
    result = ocr.ocr(img)
    texts, confidences = [], []
    if not result:
        return texts, 0
    for block in result:
        rec_texts = block.get("rec_texts", [])
        rec_scores = block.get("rec_scores", [])
        for text, conf in zip(rec_texts, rec_scores):
            if text and text.strip():
                texts.append(text.strip())
                confidences.append(float(conf))
    avg_conf = round(np.mean(confidences) * 100, 2) if confidences else 0
    return texts, avg_conf

def abbreviate_program(program: str) -> str:
    if not program: return None
    skip = {"of", "the", "in", "and"}
    words = [w for w in program.split() if w.lower() not in skip]
    if not words: return None
    return "".join(w[0].upper() for w in words)

def extract_title(text_lines):
    lines = [line.strip() for line in text_lines if len(line.strip()) > 3]
    if not lines:
        return None
    return re.sub(r'\s+', ' ', " ".join(lines)).strip()

def extract_authors(text_lines):
    lines = [line.strip() for line in text_lines if len(line.strip()) > 1]
    if not lines:
        return None
    authors_text = ", ".join(lines)
    authors_text = re.sub(r'\s*,\s*', ', ', authors_text)
    return re.sub(r'\s+', ' ', authors_text).strip()

def extract_program_and_date(text_lines):
    program_name = None
    date_published = None
    for line in text_lines:
        date_match = re.search(r'([A-Z][a-z]+ \d{4})', line)
        if date_match:
            date_published = date_match.group(1)
        if re.search(r'(Bachelor|Master|BS|MS|Doctor|PhD)', line, re.I):
            program_name = line.strip()
    return program_name, date_published

def extract_abstract(text_lines):
    if not text_lines: return None
    abstract_text = " ".join([line.strip() for line in text_lines if line.strip()])
    return re.sub(r'\s+', ' ', abstract_text).strip() if abstract_text else None

def extract_keywords(text_lines):
    keywords_list = []
    capture = False
    for line in text_lines:
        if re.search(r'(?i)keywords?', line):
            capture = True
            line = re.sub(r'(?i)keywords?\s*[:\-]?\s*', '', line)
            if line: keywords_list.append(line)
            continue
        if capture:
            if re.match(r'(?i)(abstract|chapter|introduction)', line):
                break
            keywords_list.append(line.strip())
    if not keywords_list: return None
    keywords_text = ", ".join([k.replace(";", ",").strip() for k in keywords_list])
    return re.sub(r'\s*,\s*', ', ', keywords_text)

# ------------------------------
# OCR Endpoints (conditionally enabled)
# ------------------------------
if OCR_AVAILABLE:
    @router.post("/ocr/title/")
    async def ocr_title(images: list[UploadFile] = File(...)):
        all_lines, confidences = [], []
        for f in images:
            img = _read_image(f)
            texts, avg_conf = _ocr_image(img)
            all_lines.extend(texts)
            confidences.append(avg_conf)
        title = extract_title(all_lines)
        return {"title": title, "accuracy": round(np.mean(confidences), 2) if confidences else 0}

    @router.post("/ocr/authors/")
    async def ocr_authors(images: list[UploadFile] = File(...)):
        all_lines, confidences = [], []
        for f in images:
            img = _read_image(f)
            texts, avg_conf = _ocr_image(img)
            all_lines.extend(texts)
            confidences.append(avg_conf)
        authors = extract_authors(all_lines)
        return {"authors": authors, "accuracy": round(np.mean(confidences), 2) if confidences else 0}

    @router.post("/ocr/program-date/")
    async def ocr_program_date(images: list[UploadFile] = File(...)):
        all_lines, confidences = [], []
        for f in images:
            img = _read_image(f)
            texts, avg_conf = _ocr_image(img)
            all_lines.extend(texts)
            confidences.append(avg_conf)
        program, date = extract_program_and_date(all_lines)
        return {
            "program_course": abbreviate_program(program),
            "program_name": program,
            "date_published": date,
            "accuracy": round(np.mean(confidences), 2) if confidences else 0
        }

    @router.post("/ocr/abstract/")
    async def ocr_abstract(images: list[UploadFile] = File(...)):
        all_lines, confidences = [], []
        for f in images:
            img = _read_image(f)
            texts, avg_conf = _ocr_image(img)
            all_lines.extend(texts)
            confidences.append(avg_conf)
        abstract = extract_abstract(all_lines)
        return {"abstract": abstract, "accuracy": round(np.mean(confidences), 2) if confidences else 0}

    @router.post("/ocr/keywords/")
    async def ocr_keywords(images: list[UploadFile] = File(...)):
        all_lines, confidences = [], []
        for f in images:
            img = _read_image(f)
            texts, avg_conf = _ocr_image(img)
            all_lines.extend(texts)
            confidences.append(avg_conf)
        keywords = extract_keywords(all_lines)
        return {"keywords": keywords, "accuracy": round(np.mean(confidences), 2) if confidences else 0}
else:
    # Optional: dummy endpoints that return error if someone calls OCR in deployment
    @router.post("/ocr/{any_path:path}")
    async def ocr_not_available(any_path: str):
        return {"error": "OCR endpoints are not available in this deployment."}
