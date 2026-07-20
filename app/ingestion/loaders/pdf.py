import io
import logfire
from pypdf import PdfReader, PdfWriter
from google.cloud import documentai
from app.config import settings

client = documentai.DocumentProcessorServiceClient()
MAX_PAGE_PER_REQUEST = 15

def parse_pdf(file_path:str):
    ''''
    Parse Pdf using Google Cloud Document ai 
    Automatically splits large pdf into multiple requests if the number of pages exceeds the limit of 15 pages per request.
    '''
    with logfire.span("Document AI PDF Parsing"):
        try:
            reader = PdfReader(file_path)
            total_pages = len(reader.pages)
            logfire.info(f"Total pages in PDF: {total_pages}")

            name = client.processor_path(
                settings.PROJECT_ID,
                settings.GCP_DOC_AI_LOCATION,
                settings.GCP_DOC_AI_PROCESSOR_ID
            )

            full_text = ""

            if total_pages <= MAX_PAGE_PER_REQUEST:
                with open(file_path,"rb") as f:
                    image_content = f.read()

                full_text = process_document_chunk(image_content,name)
            else:
                logfire.info(f"PDF Page exceeds {MAX_PAGE_PER_REQUEST} pages. Splitting into chuncks ...")

                for i in range(0, total_pages, MAX_PAGE_PER_REQUEST):
                    writer = PdfWriter()
                    chunk_end = min(i+MAX_PAGE_PER_REQUEST, total_pages)

                    for page_num in range(i,chunk_end):
                        writer.add_page(reader.pages[page_num])

                    with io.BytesIO() as byte_stream:
                        writer.write(byte_stream)
                        chunk_bytes = byte_stream.getvalue()

                    with logfire.span(f"Processing pages {i+1} to {chunk_end}"):
                        chunk_text = process_document_chunk(chunk_bytes,name)
                        full_text += chunk_text + "\n"
            if not full_text.strip():
                logfire.warning(f"Document AI returned empty text for {file_path}")
            else:
                logfire.info(f"Document ai succefully parsed {len(full_text)} char")
            
            return full_text
        except Exception as e:
            logfire.error(f"Error parsing PDF: {e}")
            logfire.info("Ensure the Processor ID is correct and the API is enabled.")
            raise e
        
def process_document_chunk(image_content: bytes, name: str )->str:
    """
    Process a chunk of the PDF using Google Cloud Document AI.

    Args:
        chunk_bytes (bytes): The bytes of the PDF chunk.
        name (str): The processor path for Document AI.

    Returns:
        str: The extracted text from the PDF chunk.
    """
    raw_document = documentai.RawDocument(
        content=image_content,
        mime_type="application/pdf"
    )

    request = documentai.ProcessRequest(
        name=name,
        raw_document=raw_document
    )

    result = client.process_document(request=request)

    
    return result.document.text
        







