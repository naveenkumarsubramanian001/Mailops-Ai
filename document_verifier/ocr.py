import pytesseract
from PIL import Image
from pdf2image import convert_from_path

def extract_text(file_path: str) -> str:
    numbered_text = ""
    
    if file_path.lower().endswith(".pdf"):
        images = convert_from_path(file_path)
        for page_idx, img in enumerate(images, 1):
            page_content = pytesseract.image_to_string(img)
            lines = page_content.split('\n')
            for line_idx, line in enumerate(lines, 1):
                if line.strip():
                    numbered_text += f"[P{page_idx} L{line_idx}] {line}\n"
    else:
        img = Image.open(file_path)
        content = pytesseract.image_to_string(img)
        lines = content.split('\n')
        for line_idx, line in enumerate(lines, 1):
            if line.strip():
                numbered_text += f"[P1 L{line_idx}] {line}\n"
    
    return numbered_text.strip()
