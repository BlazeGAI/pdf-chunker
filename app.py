import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
import os

# Function to split PDF
def split_pdf(pdf_file, max_size_mb):
    input_pdf = PdfReader(pdf_file)
    total_pages = len(input_pdf.pages)
    output_files = []
    part_num = 1

    temp_pdf_writer = PdfWriter()
    temp_size = 0

    for page_num in range(total_pages):
        temp_pdf_writer.add_page(input_pdf.pages[page_num])
        temp_path = f"temp_part_{part_num}.pdf"

        with open(temp_path, "wb") as temp_file:
            temp_pdf_writer.write(temp_file)

        temp_size = os.path.getsize(temp_path) / (1024 * 1024)  # size in MB

        if temp_size > max_size_mb:
            temp_pdf_writer.remove_page(-1)  # Remove the last page
            output_path = f"part_{part_num}.pdf"
            with open(output_path, "wb") as output_file:
                temp_pdf_writer.write(output_file)
            output_files.append(output_path)
            os.remove(temp_path)

            # Start a new writer for the next part
            part_num += 1
            temp_pdf_writer = PdfWriter()
            temp_pdf_writer.add_page(input_pdf.pages[page_num])

    # Write the remaining pages to the last part
    if len(temp_pdf_writer.pages) > 0:
        output_path = f"part_{part_num}.pdf"
        with open(output_path, "wb") as output_file:
            temp_pdf_writer.write(output_file)
        output_files.append(output_path)

    return output_files

st.title("PDF Splitter")
st.write("Upload a PDF file to split it into pieces no larger than 9MB.")

pdf_file = st.file_uploader("Choose a PDF file", type="pdf")

if pdf_file is not None:
    max_size_mb = 9
    output_files = split_pdf(pdf_file, max_size_mb)

    st.write(f"PDF split into {len(output_files)} parts.")
    for output_file in output_files:
        with open(output_file, "rb") as file:
            st.download_button(
                label=f"Download {output_file}",
                data=file,
                file_name=output_file,
                mime="application/pdf"
            )
        os.remove(output_file)
