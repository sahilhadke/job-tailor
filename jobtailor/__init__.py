import google.generativeai as genai
from jobtailor.utils.functions import read_prompt
import os
import ast
import PyPDF2
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
nltk.download('punkt')
nltk.download('stopwords')

class JobTailor:
    """
    Input: 
    resume_path - path to the master resume file
    job_description - text of the job description
    url - boolean to indicate if the job_description is a URL (True) or a file path (False)
    output_path - path to the output file
    """
    
    def __init__(self, resume_path, job_description, output_path, gemini_key):
        
        print("===called constructor===")
        self.resume_path = resume_path
        self.job_description = job_description
        self.output_path = output_path
        self.prompts_dir = "/jobtailor/prompts/"

        self.job_description_json = {}
        self.resume_json = {}

        genai.configure(api_key=gemini_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.chat = self.model.start_chat(history=[])

        self.initiate()

    # function to send prompt to gpt and get response
    def get_response(self, prompt):
        try:
            response = self.chat.send_message(prompt)
            return response.text
        except Exception as e:
            return str(e)
    
    def set_persona(self):
        print("===called set_persona===")
        persona_text = read_prompt(os.getcwd() + self.prompts_dir, "persona.txt")
        return self.get_response(persona_text)
    
    # function to convert job description to json
    def job_description_to_json(self):
        print("===called job_description_to_json===")
        job_description_prompt = read_prompt(os.getcwd() + self.prompts_dir, "extract-job.txt")
        
        res = self.get_response(job_description_prompt + "--" + self.job_description)

        data_list = ast.literal_eval(res.replace("```json", "").replace("```", "").strip())
        
        # print("Job Description JSON: ", data_list)

        return data_list
    
    # function to convert resume to json
    def resume_to_json(self):
        print("===called resume_to_json===")
        
        # convert resume to text
        with open(self.resume_path, "rb") as file:
        # Create a PDF reader object
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Initialize a variable to store all the text
            full_text = ""
            
            # Iterate through each page in the PDF file
            for page in pdf_reader.pages:
                # Extract text from the page and add it to the full_text variable
                full_text += page.extract_text() + "\n"
        
            print("Full Text: ", full_text)

            # remove stopwords
            stop_words = set(stopwords.words('english'))
            word_tokens = word_tokenize(full_text)
            filtered_text = [w for w in word_tokens if not w.lower() in stop_words]
            filtered_resume = ' '.join(filtered_text)
            print("Filtered Resume Text: ", filtered_resume)


    def initiate(self):
        print("===called initiate===")
        # set persona
        self.set_persona()

        # job description to json 
        self.job_description_json = (self.job_description_to_json())

        # resume to json
        self.resume_to_json()
        # get tailored resume json

        # get cover letter json

        # convert resume json to pdf

        # convert cover letter json to pdf

