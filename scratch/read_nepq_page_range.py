import pypdf

pdf_path = r"c:\Python\WHOP AUTOMATION AGENTIC\scratch\NEPQ-Black-Book-of-Questions.pdf"
reader = pypdf.PdfReader(pdf_path)

# Let's search pages 80 to 110 for sections
for i in range(80, 110):
    text = reader.pages[i].extract_text()
    first_few_lines = "\n".join(text.split("\n")[:10])
    print(f"=== PDF PAGE {i+1} ===")
    print(first_few_lines)
    print("-" * 30)
