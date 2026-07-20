from typing import List
import logfire


def chunk_text(text:str, chunk_size:int = 1500) -> List[str]:
    """
    Simple semantic chuncking that splits by paragraphs.
    Ensure chunks do not exceed the specified size.

    Args:
        text (str): text to be chunked
        chunk_size (int, optional): The maximum size of each chunk. Defaults to 1500.

    Returns:
        List[str]: A list of text chunks.
    """
    with logfire.span("Text Chunking ", text_length = len(text)):
        if not text.strip():
            return []
        paragraphs = text.split("\n\n")

        chunks = []

        current_chunk = ""

        for p in paragraphs:
            if len(current_chunk) + len(p) <= chunk_size:
                current_chunk += p + "\n\n"
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                if len(p) > chunk_size:
                    for i in range(0, len(p), chunk_size):
                        chunks.append(p[i:i + chunk_size].strip())
                    current_chunk = ""
                else:
                    current_chunk = p + "\n\n"

        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        valid_chunks = [c for c in chunks if c.strip()]
        return valid_chunks