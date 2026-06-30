from bs4 import BeautifulSoup
import logfire

def parse_html(file_path:str):
    """
    Parse HTML file using BeautifulSoup.
    CLeans scripts, styles and extract readable text from HTML content.

    Args:
        file_path (str): file name
    """
    with logfire.span("HTML Parsing",file_name = file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            soup = BeautifulSoup(content, "html.parser")

            for script in soup(["script", "style", "noscript","meta"]):
                script.decompose()  # Remove scripts and styles
            
            text = soup.get_text(separator='\n')

            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text_clean = '\n'.join(chunk for chunk in chunks if chunk)

            return text_clean
        except Exception as e:
            logfire.error("Error occurred while parsing HTML file", error=e)
            raise e