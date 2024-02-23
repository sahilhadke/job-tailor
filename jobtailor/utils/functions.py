import PyPDF2

# function to take directory and file name as input and return the txt file contents as string
def read_prompt(file_path, fiel_name):
    try:
        with open(file_path + fiel_name, 'r') as file:
            return file.read()
    except Exception as e:
        return str(e)
    

def pdf_to_text(pdf_path):
    text = ''
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
    return text
