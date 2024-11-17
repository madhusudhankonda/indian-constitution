import os
from chroma_utils import ChromaDBClient
from typing import List
import PyPDF2
import uuid
import logging

logging.basicConfig(level=logging.INFO)

def split_pdf_into_chunks(pdf_path: str, chunk_size: int = 1000) -> List[tuple]:
    """Split PDF into chunks with metadata"""
    chunks = []
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            current_chunk = ""
            current_page = 1
            chunk_start_page = 1
            
            for page_num, page in enumerate(pdf_reader.pages, 1):
                text = page.extract_text()
                current_chunk += text
                
                if len(current_chunk) >= chunk_size:
                    chunks.append((
                        current_chunk.strip(),
                        {
                            "source": os.path.basename(pdf_path),
                            "page_range": f"{chunk_start_page}-{page_num}",
                            "chunk_id": str(len(chunks))
                        }
                    ))
                    current_chunk = ""
                    chunk_start_page = page_num + 1
            
            # Add remaining text if any
            if current_chunk:
                chunks.append((
                    current_chunk.strip(),
                    {
                        "source": os.path.basename(pdf_path),
                        "page_range": f"{chunk_start_page}-{page_num}",
                        "chunk_id": str(len(chunks))
                    }
                ))
    except Exception as e:
        logging.error(f"Error processing PDF {pdf_path}: {str(e)}")
        raise
    
    return chunks

def initialize_chroma_db():
    """Initialize ChromaDB with constitution documents"""
    # Create ChromaDB client with persistent storage
    persist_dir = os.path.join(os.getcwd(), "chroma_db")
    os.makedirs(persist_dir, exist_ok=True)
    
    client = ChromaDBClient(persist_directory=persist_dir)
    
    # List of supported languages and their PDF files
    languages = {
        "English": "the_ic.pdf",
        # "Hindi": "ic-hindi.pdf",
        # "Telugu": "ic-telugu.pdf",
        # "Tamil": "ic-tamil.pdf",
        # "Marathi": "ic-marathi.pdf",
        # "Gujarati": "ic-gujarati.pdf",
        # "Kannada": "ic-kannada.pdf",
        # "Malayalam": "ic-malayalam.pdf"
    }
    
    for language, pdf_file in languages.items():
        try:
            pdf_path = os.path.join("src", "images", pdf_file)
            
            if not os.path.exists(pdf_path):
                logging.warning(f"PDF file not found: {pdf_file}")
                continue
            
            logging.info(f"Processing {language} constitution...")
            
            # Create collection for language
            collection = client.create_collection(
                collection_name=f"constitution_{language.lower()}",
                language=language
            )
            
            # Split PDF into chunks
            chunks = split_pdf_into_chunks(pdf_path)
            
            if not chunks:
                logging.warning(f"No content extracted from {pdf_file}")
                continue
            
            # Prepare data for insertion
            texts = [chunk[0] for chunk in chunks]
            metadata = [chunk[1] for chunk in chunks]
            ids = [str(uuid.uuid4()) for _ in chunks]
            
            # Add documents to collection
            client.add_documents(
                collection_name=f"constitution_{language.lower()}",
                texts=texts,
                metadata=metadata,
                ids=ids
            )
            
            logging.info(f"Successfully initialized {language} collection with {len(chunks)} chunks")
            
        except Exception as e:
            logging.error(f"Error processing {language}: {str(e)}")
            continue

if __name__ == "__main__":
    try:
        initialize_chroma_db()
        logging.info("ChromaDB initialization completed successfully")
    except Exception as e:
        logging.error(f"ChromaDB initialization failed: {str(e)}")