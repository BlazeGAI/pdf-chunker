import streamlit as st
from pdfminer.high_level import extract_text
import os
from zipfile import ZipFile
import re

# Function to clean text
def clean_text(text):
    # Remove non-printable characters
    text = re.sub(r'[^\x20-\x7E\n]', '', text)
    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    # Replace multiple newlines with a single newline
    text = re.sub(r'\n+', '\n', text)
    return text.strip()

# Function to split text into files
def split_text_to_files(text, max_size_mb):
    max_size_bytes = max_size_mb * 1024 * 1024
    output_files = []
    part_num = 1
    start = 0

    while start < len(text):
        end = start + max_size_bytes
        part_text = text[start:end]
        while len(part_text.encode('utf-8')) > max_size_bytes:
            end -= 1
            part_text = text[start:end]
        
        output_path = f"part_{part_num}.txt"
        with open(output_path, "w", encoding="utf-8") as output_file:
            output_file.write(part_text)
        output_files.append(output_path)
        
        start = end
        part_num += 1

    return output_files

# Function to create a zip file from a list of files
def create_zip(output_files, zip_name="output.zip"):
    with ZipFile(zip_name, 'w') as zipf:
        for file in output_files:
            zipf.write(file)
            os.remove(file)
    return zip_name

st.title("PDF to Clean Text Splitter")
st.write("Upload a PDF file to convert it to clean text and split it into pieces no larger than 10MB.")

pdf_file = st.file_uploader("Choose a PDF file", type="pdf")

if pdf_file is not None:
    # Extract text from PDF
    text = extract_text(pdf_file)
    
    # Clean the extracted text
    clean_text_data = clean_text(text)
    
    max_size_mb = 10
    output_files = split_text_to_files(clean_text_data, max_size_mb)
    
    zip_name = "text_parts.zip"
    zip_path = create_zip(output_files, zip_name)
    
    with open(zip_path, "rb") as zip_file:
        st.download_button(
            label="Download ZIP file",
            data=zip_file,
            file_name=zip_name,
            mime="application/zip"
        )
    
    os.remove(zip_path)  # Remove the zip file after download
