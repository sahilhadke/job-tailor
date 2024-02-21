import google.generativeai as genai
from jobtailor.utils.functions import read_prompt
import os



class JobTailor:
    """
    Input: 
    resume_path - path to the master resume file
    job_description - text of the job description
    url - boolean to indicate if the job_description is a URL (True) or a file path (False)
    output_path - path to the output file
    """
    
    def __init__(self, resume_path, job_description, output_path, gemini_key):
        
        self.resume_path = resume_path
        self.job_description = job_description
        self.output_path = output_path
        self.prompts_dir = "/jobtailor/prompts/"

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
        persona_text = read_prompt(os.getcwd() + self.prompts_dir, "persona.txt")
        return self.get_response(persona_text)
    
    # function to convert job description to json
    def job_description_to_json(self):
        job_description_prompt = read_prompt(os.getcwd() + self.prompts_dir, "job-description-to-json.txt")
        
        res = self.get_response(job_description_prompt + "--" + self.job_description)
        print("Job Description to JSON: ", res)
        return res
    
    def initiate(self):

        # set persona
        self.set_persona()

        # job description to json 
        self.job_description_to_json()

        # resume to json

        # get tailored resume json

        # get cover letter json

        # convert resume json to pdf

        # convert cover letter json to pdf

