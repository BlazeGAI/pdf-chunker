import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
import os

# Function to split PDF
def split_pdf(pdf_file, max_size_mb):
    input_pdf = PdfReader(pdf_file)
    total_pages = len(input_pdf.pages)
    output_files = []
    part_num = 1

    current_writer = PdfWriter()
    current_size = 0

    for page_num in range(total_pages):
        current_writer.add_page(input_pdf.pages[page_num])
        temp_path = f"temp_part_{part_num}.pdf"

        with open(temp_path, "wb") as temp_file:
            current_writer.write(temp_file)

        temp_size = os.path.getsize(temp_path) / (1024 * 1024)  # size in MB
        os.remove(temp_path)
        
        if temp_size > max_size_mb:
            # Remove the last page added to the writer
            current_writer.pages.pop()
            
            # Save the current part without the last page
            output_path = f"part_{part_num}.pdf"
            with open(output_path, "wb") as output_file:
                current_writer.write(output_file)
            output_files.append(output_path)

            # Start a new part
            part_num += 1
            current_writer = PdfWriter()
            current_writer.add_page(input_pdf.pages[page_num])

            # Recalculate the size of the new part
            with open(temp_path, "wb") as temp_file:
                current_writer.write(temp_file)
            current_size = os.path.getsize(temp_path) / (1024 * 1024)
            os.remove(temp_path)
        else:
            current_size = temp_size

    if len(current_writer.pages) > 0:
        output_path = f"part_{part_num}.pdf"
        with open(output_path, "wb") as output_file:
            current_writer.write(output_file)
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
