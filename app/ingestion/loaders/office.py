import logfire
from unstructured.partition.auto import partition


def parse_office(file_path: str) -> str:
    """
    Parse an office document (e.g., Word, Excel, PowerPoint) and extract its text content.

    Args:
        file_path (str): The path to the office document.

    Returns:
        str: The extracted text content from the office document.
    """
    with logfire.span("Office Document Parsing"):
        try:
            elements = partition(filename=file_path)
            text_content = "\n".join([element.text for element in elements])
            if not text_content.strip():
                logfire.warning(f"Office document returned empty text for {file_path}")
            else:
                logfire.info(f"Office document successfully parsed {len(text_content)} characters")
            return text_content
        except Exception as e:
            logfire.error(f"Error parsing office document: {e}")
            raise e