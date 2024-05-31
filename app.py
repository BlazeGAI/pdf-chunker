import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
import os
from zipfile import ZipFile

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

        if temp_size > max_size_mb and page_num > 0:
            current_writer = PdfWriter()  # Start a new writer without adding the current page
            current_writer.add_page(input_pdf.pages[page_num])  # Add the current page to the new writer

            # Write the previous writer's content to a new part file
            output_path = f"part_{part_num}.pdf"
            with open(output_path, "wb") as output_file:
                current_writer.write(output_file)
            output_files.append(output_path)

            part_num += 1
            current_writer = PdfWriter()
            current_size = temp_size  # Reset the size for the new part
        else:
            current_size = temp_size

        os.remove(temp_path)  # Remove the temporary file

    if len(current_writer.pages) > 0:
        output_path = f"part_{part_num}.pdf"
        with open(output_path, "wb") as output_file:
            current_writer.write(output_file)
        output_files.append(output_path)

    return output_files

# Function to create a zip file from a list of files
def create_zip(output_files, zip_name="output.zip"):
    with ZipFile(zip_name, 'w') as zipf:
        for file in output_files:
            zipf.write(file)
            os.remove(file)
    return zip_name

st.title("PDF Splitter")
st.write("Upload a PDF file to split it into pieces no larger than 9MB.")

pdf_file = st.file_uploader("Choose a PDF file", type="pdf")

if pdf_file is not None:
    max_size_mb = 9
    output_files = split_pdf(pdf_file, max_size_mb)
    
    zip_name = "pdf_parts.zip"
    zip_path = create_zip(output_files, zip_name)
    
    with open(zip_path, "rb") as zip_file:
        st.download_button(
            label="Download ZIP file",
            data=zip_file,
            file_name=zip_name,
            mime="application/zip"
        )
    
    os.remove(zip_path)  # Remove the zip file after download
