import pypdf

pdf_path = r"c:\Python\WHOP AUTOMATION AGENTIC\scratch\NEPQ-Black-Book-of-Questions.pdf"
reader = pypdf.PdfReader(pdf_path)

pages_to_read = [65, 66]
for p in pages_to_read:
    print(f"================ PAGE {p} ================")
    print(reader.pages[p - 1].extract_text()[:1500])
