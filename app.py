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

# Function to locate the ToC and extract chapter headings
def extract_chapter_headings(text):
    # Identify the start of the ToC by looking for the ToC header
    toc_start = text.lower().find('table of contents')
    if toc_start == -1:
        return None
    
    # Define an end marker for ToC, this might be a common phrase or chapter 1
    toc_end = text.lower().find('chapter 1', toc_start)
    if toc_end == -1:
        toc_end = text.lower().find('chapter i', toc_start)
    if toc_end == -1:
        toc_end = text.lower().find('1.', toc_start)

    if toc_end == -1:
        return None
    
    toc_text = text[toc_start:toc_end]
    chapter_pattern = re.compile(r'(Chapter \d+)', re.IGNORECASE)
    chapter_headings = chapter_pattern.findall(toc_text)
    
    return chapter_headings

# Function to split text based on chapter headings
def split_text_by_chapters(text, chapter_headings):
    chapters = {}
    for i, heading in enumerate(chapter_headings):
        start = text.lower().find(heading.lower())
        end = text.lower().find(chapter_headings[i + 1].lower()) if i + 1 < len(chapter_headings) else len(text)
        if start != -1:
            chapters[heading] = text[start:end].strip()
    
    return chapters

# Function to create a zip file from a list of files
def create_zip(chapters, zip_name="output.zip"):
    with ZipFile(zip_name, 'w') as zipf:
        for chapter, content in chapters.items():
            file_name = f"{chapter.replace(' ', '_')}.txt"
            with open(file_name, "w", encoding="utf-8") as output_file:
                output_file.write(content)
            zipf.write(file_name)
            os.remove(file_name)
    return zip_name

st.title("PDF to Clean Text Splitter by Chapter")
st.write("Upload a PDF file to convert it to clean text and split it into chapters.")

pdf_file = st.file_uploader("Choose a PDF file", type="pdf")

if pdf_file is not None:
    # Extract text from PDF
    text = extract_text(pdf_file)

    # Debugging output to check the extracted text
    st.write(f"Extracted Text: {text[:2000]}...")  # Display first 2000 characters

    # Locate the ToC and extract chapter headings
    chapter_headings = extract_chapter_headings(text)
    if not chapter_headings:
        st.write("Could not find Table of Contents or Chapter Headings")
    else:
        # Debugging output to check chapter headings
        st.write(f"Chapter Headings: {chapter_headings}")
        
        # Split text by chapters
        chapters = split_text_by_chapters(text, chapter_headings)
        
        # Debugging output to check the split chapters
        st.write(f"Chapters Found: {list(chapters.keys())}")
        
        # Clean the chapter texts
        cleaned_chapters = {k: clean_text(v) for k, v in chapters.items()}
        
        # Create a zip file
        zip_name = "chapters.zip"
        zip_path = create_zip(cleaned_chapters, zip_name)
        
        with open(zip_path, "rb") as zip_file:
            st.download_button(
                label="Download ZIP file",
                data=zip_file,
                file_name=zip_name,
                mime="application/zip"
            )
        
        # Optionally, do not remove the zip file immediately to avoid reprocessing
        # os.remove(zip_path)
