import streamlit as st
import fitz  # PyMuPDF
import nltk
import time

nltk.download('punkt')

def extract_text_from_pdf(pdf_file):
    pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
    full_text = ""
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        full_text += page.get_text("text")
    return full_text

def chunk_text(text, max_length=1000):
    sentences = nltk.sent_tokenize(text)
    chunks = []
    current_chunk = []

    for sentence in sentences:
        if len(' '.join(current_chunk)) + len(sentence) <= max_length:
            current_chunk.append(sentence)
        else:
            chunks.append(' '.join(current_chunk))
            current_chunk = [sentence]
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

def process_chunk(chunk):
    # Simulate processing time
    start_time = time.time()
    # Simulate processing by sleeping (replace with actual processing logic)
    time.sleep(1)
    processing_time = time.time() - start_time
    return f"Processed chunk in {processing_time:.2f} seconds."

def main():
    st.title("PDF Text Chunker and Processor")

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file is not None:
        with st.spinner('Extracting text from PDF...'):
            text = extract_text_from_pdf(uploaded_file)
        st.success('Text extracted from PDF.')
        
        max_length = st.slider("Select maximum chunk length (number of characters)", min_value=500, max_value=5000, value=1000, step=500)
        
        chunks = chunk_text(text, max_length=max_length)
        
        st.write(f"Total chunks created: {len(chunks)}")

        process_results = []
        for i, chunk in enumerate(chunks):
            result = process_chunk(chunk)
            process_results.append(result)
            st.write(f"Chunk {i+1}: {result}")

if __name__ == "__main__":
    main()
