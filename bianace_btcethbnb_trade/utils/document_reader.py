from docx import Document
from config.settings import TRADE_RULE_DOCX_PATH


def read_document(file_path=None):
    """
    Read content from a DOCX file
    
    Args:
        file_path (str): Path to the DOCX file. Uses default if None.
    
    Returns:
        str: Content of the document
    """
    if file_path is None:
        file_path = TRADE_RULE_DOCX_PATH
    
    try:
        doc = Document(file_path)
        full_text = []
        for paragraph in doc.paragraphs:
            full_text.append(paragraph.text)
        return '\n'.join(full_text)
    except Exception as e:
        print(f"Error reading document: {e}")
        return ""