import logfire

def parse_text(file_path:str):
    """
    Parse plain text

    Args:
        file_path (str): file name
    """
    with logfire.span("Text Parsing",file_name = file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logfire.error("Error occurred while parsing text file", error=e)
            raise e
