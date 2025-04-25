import os
import tempfile
import fitz  # PyMuPDF
from PIL import Image
import io

def generate_preview(pdf_path, filename):
    """Generate a preview of a PDF file including thumbnail, excerpt, and TOC"""
    result = {
        "thumbnail": None,
        "excerpt": None,
        "toc": None
    }
    
    try:
        doc = fitz.open(pdf_path)
        
        # Generate thumbnail from first page
        if doc.page_count > 0:
            page = doc[0]
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img_data = pix.tobytes("ppm")
            img = Image.open(io.BytesIO(img_data))
            thumb_path = f"thumbnails/{os.path.splitext(filename)[0]}.jpg"
            img.save(thumb_path)
            result["thumbnail"] = thumb_path
        
        # Extract text excerpt
        if doc.page_count > 0:
            text = doc[0].get_text().strip()
            # Get first 300 characters as excerpt
            if text:
                result["excerpt"] = (text[:300] + "...") if len(text) > 300 else text
        
        # Get table of contents
        toc = doc.get_toc()
        if toc:
            result["toc"] = [{"level": level, "title": title, "page": page} 
                              for level, title, page in toc]
        
        doc.close()
    except Exception as e:
        print(f"Error generating preview: {e}")
    
    return result