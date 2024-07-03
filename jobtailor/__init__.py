import google.generativeai as genai
import os
import PyPDF2
import json
from jinja2 import Environment, FileSystemLoader
import shutil
from docx import Document
import time
# from utils.functions import read_prompt, process_json, replace_placeholders
from .utils.functions import process_json, replace_placeholders, read_prompt

module_dir = os.path.dirname(__file__)
output_dir_default = os.path.join(module_dir, "output/")
class JobTailor:
    """
    Input: 
    resume_path - path to the master resume file
    job_description - text of the job description
    url - boolean to indicate if the job_description is a URL (True) or a file path (False)
    pdflatex_path (optional) - path to the pdflatex executable - Default - pdflatex

    Output:
    tailored_resume_path - path to the tailored resume file
    tailored_coverletter_path - path to the tailored cover letter file
    """
    
    def __init__(self, resume_path, job_description, gemini_key, output_dir=output_dir_default, pdflatex_path='pdflatex'):
        
        print("===called constructor===")

        self.resume_path = resume_path
        self.job_description = job_description
        self.prompts_dir = os.path.join(module_dir, "prompts/")
        self.resources_dir = os.path.join(module_dir, "resources/")
        self.output_dir = output_dir
        # if directory not present, create it
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        # self.output_dir = os.path.join(module_dir, "output/")
        self.pdflatex_path = pdflatex_path

        # initialize genai
        genai.configure(api_key=gemini_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.chat = self.model.start_chat()

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

        # generate cover letter
        self.tailored_coverletter_path = self.get_tailored_coverletter()


    # function to send prompt to gpt and get response
    def get_response(self, prompt):
        time.sleep(5)
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

        return res.replace("```json", "").replace("```JSON", "").replace("```", "")
    
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


            resume_extract_prompt = read_prompt(self.prompts_dir, "extract-resume.txt")
        
            res = self.get_response(resume_extract_prompt + "--" + full_text)

            res = res.replace("```json", "").replace("```JSON", "").replace("```", "").replace("None","").replace("JSON\n", "")

            data = json.loads(res)

            return data
        
    def get_tailored_resume(self):
        print("===called get_tailored_resume===")
        tailored_resume = self.resume_json

        # get tailored skills
        """"""
        print("===tailoring the skills===")

        skills_json = {"skills": tailored_resume["skills"]}

        tailored_resume_skills_prompt = read_prompt(self.prompts_dir, "tailored-skills.txt")
        
        tailord_skills_response = self.get_response(tailored_resume_skills_prompt + "--\n<JOB_DETAIL>" + json.dumps(self.job_description_json) + "\n</JOB_DETAIL>\n--\n<SKILLS>" + json.dumps(skills_json) + "\n</SKILLS>")

        tailord_skills_json = json.loads(tailord_skills_response.replace("```json", "").replace("```JSON", "").replace("```", ""))
        
        tailored_resume["skills"] = tailord_skills_json["skills"]

        print("===tailoring the work experience===")
        work_exp_json = {"work_experience": tailored_resume["work_experience"]}

        tailored_resume_workex_prompt = read_prompt(self.prompts_dir, "tailored-experience.txt")
        
        tailord_workex_response = self.get_response(tailored_resume_workex_prompt + "--\n<JOB_DETAIL>" + json.dumps(self.job_description_json) + "\n</JOB_DETAIL>\n--\n<WORK>" + json.dumps(work_exp_json) + "\n</WORK>")

        tailord_workex_json = json.loads(tailord_workex_response.replace("```json", "").replace("```JSON", "").replace("```", ""))
        
        tailored_resume["work_experience"] = tailord_workex_json["work_experience"]

        print("===tailoring the projects===")
        projects_json = {"projects": tailored_resume["projects"]}

        tailored_resume_project_prompt = read_prompt(self.prompts_dir, "tailored-projects.txt")

        tailord_projects_response = self.get_response(tailored_resume_project_prompt + "--\n<JOB_DETAIL>" +  json.dumps(self.job_description_json) + "\n</JOB_DETAIL>\n--\n<PROJECTS>" + json.dumps(projects_json) + "\n</PROJECTS>")

        tailord_projects_json = json.loads(tailord_projects_response.replace("```json", "").replace("```JSON", "").replace("```", ""))
        tailored_resume["projects"] = tailord_projects_json["projects"]
        
        return tailored_resume

    def generate_resume_pdf(self):

        # Set up the Jinja2 environment
        template_dir = os.path.join(module_dir, "resources")
        env = Environment(loader=FileSystemLoader(template_dir))
        # file_loader = FileSystemLoader('.')
        # env = Environment(loader=file_loader)

        # Load the LaTeX template
        try:

            # template_path = os.path.join(self.resources_dir, "jakes_template.tex")
            # template = env.get_template(template_path)
            # Render the template with the data
            # jakes_template_path = os.path.join("./resources", "jakes_template.tex")
            template = env.get_template("jakes_template.tex")
            rendered_tex = template.render(process_json(self.tailored_resume))
        except Exception as e:
            print(f"Error: {e}")
            print(f"Current working directory: {os.getcwd()}")
        
        # Write the rendered LaTeX to a file
        output_tex_path = os.path.join(self.output_dir, "curated_template.tex")
        with open(output_tex_path, 'w') as f:
            f.write(rendered_tex)

        # compile the latex file
        pdflatex_command = f"'{self.pdflatex_path}' -output-directory '{self.output_dir}' '{output_tex_path}'"
        os.system(pdflatex_command)

        # delete the intermediate files
        intermediate_files = ["curated_template.aux", "curated_template.log", "curated_template.out", "curated_template.tex"]
        for file in intermediate_files:
            file_path = os.path.join(self.output_dir, file)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

        # rename pdf file
        os.rename(os.path.join(self.output_dir, "curated_template.pdf"), os.path.join(self.output_dir, "jobtailor-curated-resume.pdf"))
        

        return os.path.join(self.output_dir, "jobtailor-curated-resume.pdf")
        # return resume_path_ne

    # function to get the paragraph for the cover letter
    def get_tailored_coverletter(self):
        print("===get_tailored_coverletter===")
        tailored_coverletter_prompt = read_prompt(self.prompts_dir, "extract-coverletter.txt")
        
        # tailord_coverletter_content = self.get_response(tailored_coverletter_prompt + "--\n<JOB_DETAIL>" + json.dumps(self.job_description_json) + "\n</JOB_DETAIL>\n")
        tailord_coverletter_content = self.get_response(tailored_coverletter_prompt + "--\n<JOB_DETAIL>" + json.dumps(self.job_description_json) + "\n</JOB_DETAIL>\n--\n<WORK_INFORMATION>" + json.dumps(self.tailored_resume) + "\n</WORK_INFORMATION>")
        tailord_coverletter_content = tailord_coverletter_content.replace("```json", "").replace("```JSON", "").replace("```", "")

        replacements = {
            "{{name}}": self.tailored_resume["name"],
            "{{location}}": self.tailored_resume["location"],
            "{{email}}": self.tailored_resume["email"],
            "{{phone}}": self.tailored_resume["phone"],
            "{{website}}": self.tailored_resume["website"],
            "{{coverletter_content}}": tailord_coverletter_content
        }

        coverletter_template_path = os.path.join(self.resources_dir, "jobtailor-coverletter.docx")
        coverletter_curated_path = os.path.join(self.output_dir, "jobtailor-curated-coverletter.docx")
        doc = Document(coverletter_template_path)

        # Replace placeholders with actual values
        replace_placeholders(doc, replacements)

        # Save the resulting document
        doc.save(coverletter_curated_path)

        return coverletter_curated_path