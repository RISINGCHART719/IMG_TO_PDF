import os
from reportlab.pdfgen import canvas
from PyPDF2 import PdfMerger

# Create folder if it doesn't exist
pdf_path = './pdf_output'
os.makedirs(pdf_path, exist_ok=True)

# temp code: delete later =====================================
for i in range(1, 6):
    filepath = os.path.join(pdf_path, f"{'pdf' + str(i)}.pdf")
    c = canvas.Canvas(filepath)
    c.drawString(100, 750, f"This should be page {i} in the pdf")
    c.save()
# temp code: delete later =====================================

# Sorting the pdfs alphabetically if not done automatically
pdf_files = sorted([f for f in os.listdir(pdf_path) if f.lower().endswith('.pdf')])

# Checking that PDFs exist
if not pdf_files:
    print("Error: no pdf files found")
    exit()

# Merge PDFs
merger = PdfMerger()
for pdf in pdf_files:
    merger.append(os.path.join(pdf_path, pdf))

# Create the merge pdf in the folder
output_path = os.path.join(pdf_path, "merged.pdf")
merger.write(output_path)
merger.close()

# delete everything in the folder but the merged pdf
for pdf in pdf_files:
    file = os.path.join(pdf_path, pdf)
    if pdf != "merged.pdf":
        os.remove(file)