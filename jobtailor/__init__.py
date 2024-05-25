import google.generativeai as genai
from jobtailor.utils.functions import read_prompt
import os
import PyPDF2
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
nltk.download('punkt')
nltk.download('stopwords')
import json

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

        # initialize genai
        genai.configure(api_key=gemini_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.chat = self.model.start_chat(history=[])

        # set persona
        self.set_persona()

        # extract job description and resume to json
        self.job_description_json = self.job_description_to_json()
        self.resume_json = self.resume_to_json()
        self.tailored_resume = self.get_tailored_resume()
        self.tailored_resume_path = self.generate_resume_pdf()


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

        return res.replace("```json", "").replace("```", "")
    
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

            # remove stopwords
            stop_words = set(stopwords.words('english'))
            word_tokens = word_tokenize(full_text)
            filtered_text = [w for w in word_tokens if not w.lower() in stop_words]
            filtered_resume = ' '.join(filtered_text)

            resume_extract_prompt = read_prompt(os.getcwd() + self.prompts_dir, "extract-resume.txt")
        
            res = self.get_response(resume_extract_prompt + "--" + filtered_resume)

            res = res.replace("```json", "").replace("```", "")

            print(res)

            data = json.loads(res)

            return data
        
    def get_tailored_resume(self):
        print("===called get_tailored_resume===")
        tailored_resume = self.resume_json

        # get tailored skills
        print("===tailoring the skills===")
        skills_json = {"skills": tailored_resume["skills"]}

        tailored_resume_skills_prompt = read_prompt(os.getcwd() + self.prompts_dir, "tailored-skills.txt")
        
        tailord_skills = self.get_response(tailored_resume_skills_prompt + "--\n<given_job_description>" + json.dumps(self.job_description_json) + "\n</given_job_description>\n--\n<given_skills>" + json.dumps(skills_json) + "\n</given_skills>")

        tailord_skills = tailord_skills.replace("```json", "").replace("```", "")
        tailord_skills_json = json.loads(tailord_skills)

        tailored_resume["skills"] = tailord_skills_json["skills"]


        print("===tailoring the work experience===")
        work_exp_json = {"work_experience": tailored_resume["work_experience"]}

        tailored_resume_workex_prompt = read_prompt(os.getcwd() + self.prompts_dir, "tailored-experience.txt")
        
        tailord_workex = self.get_response(tailored_resume_workex_prompt + "--\n<given_job_description>" + json.dumps(self.job_description_json) + "\n</given_job_description>\n--\n<given_work_experience>" + json.dumps(work_exp_json) + "\n</given_work_experience>")

        tailord_workex = tailord_workex.replace("```json", "").replace("```", "")
        tailord_workex_json = json.loads(tailord_workex)

        tailored_resume["work_experience"] = tailord_workex_json["work_experience"]

        print("===tailoring the projects===")
        projects_json = {"projects": tailored_resume["projects"]}

        tailored_resume_project_prompt = read_prompt(os.getcwd() + self.prompts_dir, "tailored-projects.txt")
        
        tailord_projects = self.get_response(tailored_resume_project_prompt + "--\n<given_job_description>" + json.dumps(self.job_description_json) + "\n</given_job_description>\n--\n<projects>" + json.dumps(projects_json) + "\n</projects>")

        tailord_projects = tailord_projects.replace("```json", "").replace("```", "")
        tailord_projects_json = json.loads(tailord_projects)

        tailored_resume["projects"] = tailord_projects_json["projects"]

        return tailored_resume

    def generate_resume_pdf(self):
        pass
        # return resume_path_new