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
from jinja2 import Environment, FileSystemLoader
import shutil

module_dir = os.path.dirname(__file__)
pdflatex_path = "/usr/local/texlive/2024/bin/universal-darwin/pdflatex"
jakes_template = os.path.join(module_dir, "resources", "jakes_template.tex")

class JobTailor:
    """
    Input: 
    resume_path - path to the master resume file
    job_description - text of the job description
    url - boolean to indicate if the job_description is a URL (True) or a file path (False)

    Output:
    tailored_resume_path - path to the tailored resume file
    tailored_coverletter_path - path to the tailored cover letter file
    """
    
    def __init__(self, resume_path, job_description, gemini_key):
        
        print("===called constructor===")

        self.resume_path = resume_path
        self.job_description = job_description
        self.prompts_dir = os.path.join(module_dir, "prompts/")
        self.resources_dir = os.path.join(module_dir, "resources/")
        self.output_dir = os.path.join(module_dir, "output/")

        # initialize genai
        genai.configure(api_key=gemini_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.chat = self.model.start_chat(history=[])

        # set persona
        self.set_persona()

        # delete existing files in output directory
        for filename in os.listdir(self.output_dir):
            file_path = os.path.join(self.output_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

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
        persona_text = read_prompt(self.prompts_dir, "persona.txt")
        return self.get_response(persona_text)
    
    # function to convert job description to json
    def job_description_to_json(self):
        print("===called job_description_to_json===")
        job_description_prompt = read_prompt(self.prompts_dir, "extract-job.txt")
        
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

            resume_extract_prompt = read_prompt(self.prompts_dir, "extract-resume.txt")
        
            res = self.get_response(resume_extract_prompt + "--" + filtered_resume)

            res = res.replace("```json", "").replace("```", "").replace("None","").replace("JSON\n", "")

            print(res)

            data = json.loads(res)

            return data
        
    def get_tailored_resume(self):
        print("===called get_tailored_resume===")
        tailored_resume = self.resume_json

        # get tailored skills
        print("===tailoring the skills===")

        skills_json = {"skills": tailored_resume["skills"]}

        tailored_resume_skills_prompt = read_prompt(self.prompts_dir, "tailored-skills.txt")
        
        tailord_skills = self.get_response(tailored_resume_skills_prompt + "--\n<JOB_DETAIL>" + json.dumps(self.job_description_json) + "\n</JOB_DETAIL>\n--\n<SKILLS>" + json.dumps(skills_json) + "\n</SKILLS>")

        tailord_skills = tailord_skills.replace("```json", "").replace("```", "")
        tailord_skills_json = json.loads(tailord_skills)

        # tailored_resume["skills"] = tailord_skills_json["skills"]


        print("===tailoring the work experience===")
        work_exp_json = {"work_experience": tailored_resume["work_experience"]}

        tailored_resume_workex_prompt = read_prompt(self.prompts_dir, "tailored-experience.txt")
        
        tailord_workex = self.get_response(tailored_resume_workex_prompt + "--\n<JOB_DETAIL>" + json.dumps(self.job_description_json) + "\n</JOB_DETAIL>\n--\n<WORK>" + json.dumps(work_exp_json) + "\n</WORK>")

        tailord_workex = tailord_workex.replace("```json", "").replace("```", "")
        tailord_workex_json = json.loads(tailord_workex)

        tailored_resume["work_experience"] = tailord_workex_json["work_experience"]

        print("===tailoring the projects===")
        projects_json = {"projects": tailored_resume["projects"]}

        tailored_resume_project_prompt = read_prompt(self.prompts_dir, "tailored-projects.txt")
        
        tailord_projects = self.get_response(tailored_resume_project_prompt + "--\n<JOB_DETAIL>" + json.dumps(self.job_description_json) + "\n</JOB_DETAIL>\n--\n<PROJECTS>" + json.dumps(projects_json) + "\n</PROJECTS>")

        tailord_projects = tailord_projects.replace("```json", "").replace("```", "")
        tailord_projects_json = json.loads(tailord_projects)

        tailored_resume["projects"] = tailord_projects_json["projects"]

        return tailored_resume

    def generate_resume_pdf(self):
        # Set up the Jinja2 environment
        file_loader = FileSystemLoader('.')
        env = Environment(loader=file_loader)

        # Load the LaTeX template
       
        try:

            # template_path = os.path.join(self.resources_dir, "jakes_template.tex")
            # template = env.get_template(template_path)
            # Render the template with the data
            template = env.get_template('./jobtailor/resources/jakes_template.tex')
            rendered_tex = template.render(self.tailored_resume)
        except Exception as e:
            print(f"Error: {e}")
            print(f"Current working directory: {os.getcwd()}")
            print(f"Expected template path: {os.path.join(module_dir, 'resources', template_path)}")

        

        # Write the rendered LaTeX to a file
        output_tex_path = os.path.join(self.output_dir, "curated_template.tex")
        with open(output_tex_path, 'w') as f:
            f.write(rendered_tex)

        # compile the latex file
        pdflatex_command = f"'{pdflatex_path}' -output-directory '{self.output_dir}' '{output_tex_path}'"
        os.system(pdflatex_command)

        return os.path.join(self.output_dir, "curated_template.pdf")
        # return resume_path_ne