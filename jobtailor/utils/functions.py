
# function to take directory and file name as input and return the txt file contents as string
def read_prompt(file_path, fiel_name):
    try:
        with open(file_path + fiel_name, 'r') as file:
            return file.read()
    except Exception as e:
        return str(e)