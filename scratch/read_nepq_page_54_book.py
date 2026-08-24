import pypdf

pdf_path = r"c:\Python\WHOP AUTOMATION AGENTIC\scratch\NEPQ-Black-Book-of-Questions.pdf"
reader = pypdf.PdfReader(pdf_path)

# Let's search for "THE TRANSITION STAGE" page in the PDF
for i in range(len(reader.pages)):
    text = reader.pages[i].extract_text()
    if "THE TRANSITION STAGE" in text:
        print(f"THE TRANSITION STAGE is on PDF Page: {i + 1}")
        print(text[:1500])
        break
