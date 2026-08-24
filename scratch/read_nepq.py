import sys
import os

pdf_path = r"c:\Python\WHOP AUTOMATION AGENTIC\scratch\NEPQ-Black-Book-of-Questions.pdf"

try:
    import pypdf
    print("[INFO] pypdf is installed, trying to extract text...")
    reader = pypdf.PdfReader(pdf_path)
    print(f"Total pages: {len(reader.pages)}")
    # Print first 5 pages
    for i in range(min(5, len(reader.pages))):
        print(f"--- PAGE {i+1} ---")
        print(reader.pages[i].extract_text()[:1500])
except ImportError:
    try:
        import fitz  # PyMuPDF
        print("[INFO] fitz is installed, trying to extract text...")
        doc = fitz.open(pdf_path)
        print(f"Total pages: {len(doc)}")
        for i in range(min(5, len(doc))):
            print(f"--- PAGE {i+1} ---")
            print(doc[i].get_text()[:1500])
    except ImportError:
        print("[ERROR] Neither pypdf nor PyMuPDF is installed. Trying to install pypdf...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pypdf"])
        import pypdf
        reader = pypdf.PdfReader(pdf_path)
        print(f"Total pages: {len(reader.pages)}")
        for i in range(min(5, len(reader.pages))):
            print(f"--- PAGE {i+1} ---")
            print(reader.pages[i].extract_text()[:1500])
