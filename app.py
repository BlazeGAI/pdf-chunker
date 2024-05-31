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

# Function to split text into chapters
def split_text_into_chapters(text):
    # Use a regular expression to find chapter headings
    chapter_pattern = re.compile(r'(?i)(Chapter \d+)', re.IGNORECASE)
    matches = list(chapter_pattern.finditer(text))
    output_files = []

    if not matches:
        # If no chapters are found, save the whole text as one file
        output_path = "full_text.txt"
        with open(output_path, "w", encoding="utf-8") as output_file:
            output_file.write(text)
        output_files.append(output_path)
        return output_files

    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        chapter_text = text[start:end].strip()

        chapter_title = match.group(1).replace(" ", "_")
        output_path = f"{chapter_title}.txt"
        with open(output_path, "w", encoding="utf-8") as output_file:
            output_file.write(chapter_text)
        output_files.append(output_path)

    return output_files

# Function to create a zip file from a list of files
def create_zip(output_files, zip_name="output.zip"):
    with ZipFile(zip_name, 'w') as zipf:
        for file in output_files:
            zipf.write(file)
    return zip_name

st.title("PDF to Clean Text Splitter by Chapter")
st.write("Upload a PDF file to convert it to clean text and split it into chapters.")

pdf_file = st.file_uploader("Choose a PDF file", type="pdf")

if pdf_file is not None:
    # Extract text from PDF
    text = extract_text(pdf_file)

    # Print text for debugging
    st.write(f"Extracted Text: {text[:2000]}...")  # Display first 2000 characters for debugging
    
    # Clean the extracted text
    clean_text_data = clean_text(text)
    
    # Print cleaned text for debugging
    st.write(f"Cleaned Text: {clean_text_data[:2000]}...")  # Display first 2000 characters for debugging
    
    # Split text into chapters
    output_files = split_text_into_chapters(clean_text_data)
    
    # Print output files for debugging
    st.write(f"Output Files: {output_files}")
    
    # Create a zip file
    zip_name = "chapters.zip"
    zip_path = create_zip(output_files, zip_name)
    
    with open(zip_path, "rb") as zip_file:
        st.download_button(
            label="Download ZIP file",
            data=zip_file,
            file_name=zip_name,
            mime="application/zip"
        )
    
    # Remove the text files and zip file after download
    for file in output_files:
        if os.path.exists(file):
            os.remove(file)
    if os.path.exists(zip_path):
        os.remove(zip_path)
