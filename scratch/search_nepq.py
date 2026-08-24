import pypdf

pdf_path = r"c:\Python\WHOP AUTOMATION AGENTIC\scratch\NEPQ-Black-Book-of-Questions.pdf"
reader = pypdf.PdfReader(pdf_path)

print("--- TABLE OF CONTENTS / INTRO PAGES (PAGES 6 to 12) ---")
for i in range(5, 12):
    print(f"--- PAGE {i+1} ---")
    print(reader.pages[i].extract_text())

print("\n--- SEARCHING FOR KEYWORDS ---")
keywords = ["consequence", "permission", "solving", "prevent", "lose", "effect"]
for kw in keywords:
    matches = []
    for page_num in range(len(reader.pages)):
        text = reader.pages[page_num].extract_text()
        if kw.lower() in text.lower():
            matches.append(page_num + 1)
    print(f"Keyword '{kw}': matches found in pages: {matches[:15]} (Total matches: {len(matches)})")
