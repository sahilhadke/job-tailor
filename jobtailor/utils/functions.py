
# function to take directory and file name as input and return the txt file contents as string
def read_prompt(file_path, file_name):
    try:
        with open(file_path + file_name, 'r') as file:
            return file.read()
    except Exception as e:
        return f"read_prompt Error reading file:{file_path}\nDetailed Error:{e}"
    
def escape_latex_special_chars(text):
    # List of special characters in LaTeX that need to be escaped
    special_chars = {
        '&': r'and',
        '$': r'\$',
        '#': r'\#'
    }

    # Replace special characters with their escaped versions
    for item in special_chars:
        # Only replace if the character is not already escaped
        # print(f'replacing {item} with {special_chars[item]}')
        text = text.replace(item, special_chars[item])
    
    return text

def process_json(obj):
    if isinstance(obj, dict):
        return {key: process_json(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [process_json(element) for element in obj]
    elif isinstance(obj, str):
        return escape_latex_special_chars(obj)
    else:
        return obj
    
# Function to replace placeholders in the document
def replace_placeholders(doc, replacements):
    for paragraph in doc.paragraphs:
        for key, value in replacements.items():
            if key in paragraph.text:
                inline = paragraph.runs
                for item in inline:
                    if key in item.text:
                        item.text = item.text.replace(key, value)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    for key, value in replacements.items():
                        if key in paragraph.text:
                            inline = paragraph.runs
                            for item in inline:
                                if key in item.text:
                                    item.text = item.text.replace(key, value)