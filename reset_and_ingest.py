"""
Utility script to reset Pinecone index and re-ingest documents with correct metadata structure.
This script will:
1. Delete all existing vectors from Pinecone
2. Re-ingest all documents from the documents/ folder
3. Use the correct metadata structure: source, text, chunk_index, uploaded_at
"""

import os
import sys
import hashlib
from datetime import datetime, timezone
from dotenv import load_dotenv
from docx import Document
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone

load_dotenv(override=True)

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("INDEX_NAME", "sindh-police-docs")
DOCS_FOLDER = "documents"

def read_docx(file_path: str) -> str:
    """Read text content from a DOCX file"""
    try:
        doc = Document(file_path)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return ""

def read_pdf(file_path: str) -> str:
    """Read text content from a PDF file"""
    try:
        pdf_reader = PdfReader(file_path)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return ""

def reset_pinecone_index():
    """Delete all vectors from Pinecone index"""
    print("🔄 Resetting Pinecone index...")
    
    try:
        pc = Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index(INDEX_NAME)
        
        # Delete all vectors by deleting with empty filter (deletes everything)
        # Note: Pinecone delete with no filter deletes all vectors
        index.delete(delete_all=True)
        
        print("✅ Pinecone index reset complete (all vectors deleted)")
        return True
    except Exception as e:
        print(f"❌ Error resetting index: {e}")
        return False

def ingest_documents(docs_folder: str = DOCS_FOLDER):
    """Process all .docx and .pdf files in the docs folder and ingest to Pinecone with correct metadata"""
    
    if not os.path.exists(docs_folder):
        print(f"❌ Docs folder '{docs_folder}' not found!")
        return False
    
    # Get all supported files
    docx_files = [f for f in os.listdir(docs_folder) if f.endswith('.docx')]
    pdf_files = [f for f in os.listdir(docs_folder) if f.endswith('.pdf')]
    all_files = docx_files + pdf_files
    
    if not all_files:
        print(f"❌ No .docx or .pdf files found in '{docs_folder}' folder!")
        return False
    
    print(f"\n📚 Found {len(all_files)} documents to process ({len(docx_files)} DOCX, {len(pdf_files)} PDF)...")
    
    try:
        # Initialize Pinecone and Embeddings
        pc = Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index(INDEX_NAME)
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=OPENAI_API_KEY
        )
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        
        total_chunks = 0
        processed_docs = []
        
        for filename in all_files:
            file_path = os.path.join(docs_folder, filename)
            print(f"\n📄 Processing: {filename}")
            
            # Read document content based on file type
            if filename.endswith('.docx'):
                text = read_docx(file_path)
            elif filename.endswith('.pdf'):
                text = read_pdf(file_path)
            else:
                print(f"  ⚠️  Skipping {filename} (unsupported format)")
                continue
            
            if not text.strip():
                print(f"  ⚠️  Skipping {filename} (empty content)")
                continue
            
            # Split into chunks
            chunks = text_splitter.split_text(text)
            print(f"  📝 Split into {len(chunks)} chunks")
            
            # Generate embeddings and upsert to Pinecone
            vectors = []
            for i, chunk in enumerate(chunks):
                if not chunk.strip():
                    continue
                
                # Create unique ID
                chunk_id = hashlib.md5(f"{filename}_{i}_{chunk[:50]}".encode()).hexdigest()
                
                # Generate embedding
                embedding = embeddings.embed_query(chunk)
                
                vectors.append({
                    "id": chunk_id,
                    "values": embedding,
                    "metadata": {
                        "text": chunk,
                        "source": filename,  # Use "source" for filtering/deletion
                        "chunk_index": i,
                        "uploaded_at": datetime.now(timezone.utc).isoformat(),
                        "uploaded_by": "system_reset"
                    }
                })
            
            # Batch upsert (Pinecone limit is 100)
            for i in range(0, len(vectors), 100):
                batch = vectors[i:i+100]
                index.upsert(vectors=batch)
                print(f"  ✅ Upserted batch {i//100 + 1} ({len(batch)} chunks)")
            
            total_chunks += len(chunks)
            
            # Track document info
            doc_info = {
                "name": filename,
                "chunks": len(chunks),
                "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "uploaded_by": "system_reset"
            }
            processed_docs.append(doc_info)
            
            print(f"  ✅ Completed: {filename} ({len(chunks)} chunks)")
        
        print(f"\n{'='*60}")
        print(f"✅ Ingestion Complete!")
        print(f"   Documents processed: {len(processed_docs)}")
        print(f"   Total chunks created: {total_chunks}")
        print(f"{'='*60}\n")
        
        # Print document summary
        print("📋 Document Summary:")
        for doc in processed_docs:
            print(f"   • {doc['name']}: {doc['chunks']} chunks")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during ingestion: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function to reset and re-ingest documents"""
    print("="*60)
    print("Sindh Police AI Meeting Member - Pinecone Reset & Re-Ingestion")
    print("="*60)
    
    # Confirm action
    print("\n⚠️  WARNING: This will delete ALL existing vectors from Pinecone!")
    response = input("Are you sure you want to continue? (yes/no): ")
    
    if response.lower() not in ['yes', 'y']:
        print("❌ Operation cancelled.")
        return
    
    # Step 1: Reset index
    if not reset_pinecone_index():
        print("❌ Failed to reset index. Aborting.")
        return
    
    # Step 2: Re-ingest documents
    if not ingest_documents():
        print("❌ Failed to ingest documents.")
        return
    
    print("\n✅ All operations completed successfully!")
    print("\n💡 Note: You may need to refresh the admin page to see the updated document list.")

if __name__ == "__main__":
    main()

