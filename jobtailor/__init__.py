import os
import PyPDF2
import json
import shutil
import time
import logging
from docx import Document
from jinja2 import Environment, FileSystemLoader
import google.generativeai as genai
from .utils.functions import process_json, replace_placeholders, read_prompt

# logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename='jobtailor_debug.log', level=logging.DEBUG)
# logging.basicConfig(filename='jobtailor_info.log', level=logging.INFO)
# logging.basicConfig(filename='jobtailor_error.log', level=logging.ERROR)

# get the directory of the module
module_dir = os.path.dirname(__file__)
class JobTailor:
    """
    Input: 
    resume_path - path to the master resume file
    job_description - text of the job description
    gemini_key - API key for generative AI

    Optional Input:
    output_dir - path to the output directory
    pdflatex_path - path to the pdflatex executable
    resume_output_file_name - name of the output resume file
    coverletter_output_file_name - name of the output cover letter file
    write_function - function to write the status

    Output:
    tailored_resume_path - path to the tailored resume file
    tailored_coverletter_path - path to the tailored cover letter file
    """
    
    def __init__(self, resume_path, job_description, gemini_key, optional_params=None):
         
        logger.info("constructur called.")
        logger.debug(f"""
            resume_path: {resume_path},
            job_description: {job_description},
            optional_params: {optional_params}
        """)

        # set mandatory parameters
        self.resume_path = resume_path
        self.job_description = job_description
        self.gemini_key = gemini_key

        # set optional parameters
        self.output_dir = os.path.join(module_dir, "output/")
        self.pdflatex_path = 'pdflatex'
        self.resume_output_file_name = 'jobtailor-curated-resume.pdf'
        self.coverletter_output_file_name = 'jobtailor-curated-coverletter.docx'
        self.write_function = print

        # set default variables
        self.prompts_dir = os.path.join(module_dir, "prompts/")
        self.resources_dir = os.path.join(module_dir, "resources/")

        # if optional parameters are provided, set them
        if optional_params:
            for key, value in optional_params.items():
                if hasattr(self, key):
                    setattr(self, key, value)
                else:
                    setattr(self, key, value)
        
        # if output directory not present, create it
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # initialize genai
        try:
            genai.configure(api_key=self.gemini_key)
            self.model = genai.GenerativeModel('gemini-pro')
            self.chat = self.model.start_chat()
        except Exception as e:
            logger.error(f"Error: error initializing genai.\nDetailed error: {e}")
            return f"Error: error initializing genai"

        # set persona
        try:
            self.set_persona()
        except Exception as e:
            logger.error(f"Error: error setting persona.\nDetailed error: {e}")
            return f"Error: error setting persona"

        # delete existing files in output directory
        for filename in os.listdir(self.output_dir):
            file_path = os.path.join(self.output_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                logger.error(f"Error: error deleting files in output directory.\nDetailed error: {e}")
                return ('Failed to delete %s. Reason: %s' % (file_path, e))

        # extract job description and resume to json
        self.job_description_json = self.job_description_to_json()

        # convert resume pdf to json
        self.resume_json = self.resume_to_json()

        # get tailored resume
        self.tailored_resume = self.get_tailored_resume()

        # generate resume - latex to pdf
        self.tailored_resume_path = self.generate_resume_pdf()

        # generate cover letter
        self.tailored_coverletter_path = self.get_tailored_coverletter()


    # function to send prompt to gpt and get response
    def get_response(self, prompt):

        # timout for 5 seconds
        time.sleep(5)
        try:
            response = self.chat.send_message(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error: error getting response with prompt: {prompt}.\nDetailed error: {e}")
            return f"Error: error getting response with prompt: {prompt}"
    
    def set_persona(self):
        logger.info("set_persona called.")
        persona_text = read_prompt(self.prompts_dir, "persona.txt")
        logger.debug(f"set_persona text: {persona_text}")
        return self.get_response(persona_text)
    
    # function to convert job description to json
    def job_description_to_json(self):
        self.write_function("- converting job description to json -")
        
        logger.info("job_description_to_json called.")

        job_description_prompt = read_prompt(self.prompts_dir, "extract-job.txt")
        logger.debug(f"job_description_prompt: {job_description_prompt}")
        
        res = self.get_response(job_description_prompt + "--" + self.job_description)
        logger.debug(f"job_description_to_json response: {res}")

        try:
            res = res.replace("```json", "").replace("```JSON", "").replace("```", "")
        except Exception as e:
            logger.debug(f"Error: error converting job description to json.\nres:{res}\nDetailed error: {e}")
            logger.error(f"Error: error converting job description to json.\nDetailed error: {e}")
            return f"Error: error converting job description to json"

        return res
    
    # function to convert resume to json
    def resume_to_json(self):
        self.write_function("- converting resume to json -")

        logger.info("resume_to_json called.")

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
            logger.debug(f"resume_extract_prompt: {resume_extract_prompt}")
        
            res = self.get_response(resume_extract_prompt + "--" + full_text)
            logger.debug(f"resume_to_json response: {res}")

            try:
                res = res.replace("```json", "").replace("```JSON", "").replace("```", "").replace("None","").replace("JSON\n", "")
                data = json.loads(res)
                logger.debug(f"resume_to_json data: {data}")
                return data
            except Exception as e:
                logger.error(f"Error: error converting resume to json.\nres:{res}\nDetailed error: {e}")
                return f"Error: error converting resume to json"
            
        
    def get_tailored_resume(self):
        self.write_function('- getting tailored resume from LLM -')

        logger.info("get_tailored_resume called.")
        tailored_resume = self.resume_json

        # get tailored skills
        """"""
        
        logger.info("tailoring the skills")
        skills_json = {"skills": tailored_resume["skills"]}

        tailored_resume_skills_prompt = read_prompt(self.prompts_dir, "tailored-skills.txt")
        logger.debug(f"tailored_resume_skills_prompt: {tailored_resume_skills_prompt}")

        tailord_skills_response = self.get_response(tailored_resume_skills_prompt + "--\n<JOB_DETAIL>" + json.dumps(self.job_description_json) + "\n</JOB_DETAIL>\n--\n<SKILLS>" + json.dumps(skills_json) + "\n</SKILLS>")
        logger.debug(f"tailord_skills_response: {tailord_skills_response}")

        try:
            tailord_skills_json = json.loads(tailord_skills_response.replace("```json", "").replace("```JSON", "").replace("```", ""))
        except Exception as e:
            logger.error(f"Error: error converting skills to json.\nDetailed error: {e}")
            return f"Error: error converting skills to json"

        # converting List to string for skills
        tailord_skills_json["skills"] # [ {}, {}, {} ]
        for skillset in tailord_skills_json["skills"]:
            if type(skillset['skills']) == list:
                converted_string = ", ".join(skillset['skills'])
                skillset['skills'] = converted_string


        tailored_resume["skills"] = tailord_skills_json["skills"]
        logger.info('- tailored skills generated -')

        self.write_function("- tailoring the work experience -")
        work_exp_json = {"work_experience": tailored_resume["work_experience"]}

        tailored_resume_workex_prompt = read_prompt(self.prompts_dir, "tailored-experience.txt")
        logger.debug(f"tailored_resume_workex_prompt: {tailored_resume_workex_prompt}")

        tailord_workex_response = self.get_response(tailored_resume_workex_prompt + "--\n<JOB_DETAIL>" + json.dumps(self.job_description_json) + "\n</JOB_DETAIL>\n--\n<WORK>" + json.dumps(work_exp_json) + "\n</WORK>")
        logger.debug(f"tailord_workex_response: {tailord_workex_response}")

        try:
            tailord_workex_json = json.loads(tailord_workex_response.replace("```json", "").replace("```JSON", "").replace("```", ""))
            tailored_resume["work_experience"] = tailord_workex_json["work_experience"]
        except Exception as e:
            logger.error(f"Error: error converting work experience to json.\nDetailed error: {e}")
            return f"Error: error converting work experience to json"

        self.write_function("- tailoring the projects -")
        projects_json = {"projects": tailored_resume["projects"]}

        tailored_resume_project_prompt = read_prompt(self.prompts_dir, "tailored-projects.txt")
        logger.debug(f"tailored_resume_project_prompt: {tailored_resume_project_prompt}")

        tailord_projects_response = self.get_response(tailored_resume_project_prompt + "--\n<JOB_DETAIL>" +  json.dumps(self.job_description_json) + "\n</JOB_DETAIL>\n--\n<PROJECTS>" + json.dumps(projects_json) + "\n</PROJECTS>")
        logger.debug(f"tailord_projects_response: {tailord_projects_response}")

        try:
            tailord_projects_json = json.loads(tailord_projects_response.replace("```json", "").replace("```JSON", "").replace("```", ""))
            tailored_resume["projects"] = tailord_projects_json["projects"]
        except Exception as e:
            logger.error(f"Error: error converting projects to json.\nDetailed error: {e}")
            return f"Error: error converting projects to json"
        
        self.write_function("- tailored resume JSON generated -")
        return tailored_resume

    def generate_resume_pdf(self):

        self.write_function('- compiling LaTex to generate resume PDF -')
        logger.info("generate_resume_pdf called.")

        # Set up the Jinja2 environment
        template_dir = os.path.join(module_dir, "resources")
        env = Environment(loader=FileSystemLoader(template_dir))
        logger.debug(f"template_dir: {template_dir}")

        # Load the LaTeX template
        try:
            template = env.get_template("jakes_template.tex")
            rendered_tex = template.render(process_json(self.tailored_resume))
        except Exception as e:
            logger.error(f"Error while rendering Latex Template: {e}")
            return f"Error while rendering Latex Template. Check log for more details"
        
        # Write the rendered LaTeX to a file
        output_tex_path = os.path.join(self.output_dir, "curated_template.tex")
        logger.debug(f"output_tex_path: {output_tex_path}")

        with open(output_tex_path, 'w') as f:
            f.write(rendered_tex)

        # compile the latex file
        self.write_function("- System command - compiling LaTex to generate resume PDF -")
        pdflatex_command = f"'{self.pdflatex_path}' -output-directory '{self.output_dir}' '{output_tex_path}'"
        logger.debug(f"pdflatex_command: {pdflatex_command}")

        try:
            logger.info("pdflatex command")
            os.system(pdflatex_command)
        except Exception as e:
            logger.error(f"Error while compiling Latex: {e}")
            return f"Error while compiling Latex. Check log for more details"
        
        # delete the intermediate files
        logger.info('deleting intermediate files')
        intermediate_files = ["curated_template.aux", "curated_template.log", "curated_template.out", "curated_template.tex"]
        for file in intermediate_files:
            file_path = os.path.join(self.output_dir, file)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                logger.error('Failed to delete %s. Reason: %s' % (file_path, e))
                return ('Failed to delete %s. Reason: %s' % (file_path, e))

        # rename pdf file
        logger.info('renaming pdf file to outputfilename')
        os.rename(os.path.join(self.output_dir, "curated_template.pdf"), os.path.join(self.output_dir, self.resume_output_file_name))

        return os.path.join(self.output_dir, self.resume_output_file_name)
        # return resume_path_ne

    # function to get the paragraph for the cover letter
    def get_tailored_coverletter(self):
        self.write_function('- getting tailored cover letter from LLM and generating DOCX -')

        tailored_coverletter_prompt = read_prompt(self.prompts_dir, "extract-coverletter.txt")
        logger.debug(f"tailored_coverletter_prompt: {tailored_coverletter_prompt}")

        # tailord_coverletter_content = self.get_response(tailored_coverletter_prompt + "--\n<JOB_DETAIL>" + json.dumps(self.job_description_json) + "\n</JOB_DETAIL>\n")
        tailord_coverletter_content = self.get_response(tailored_coverletter_prompt + "--\n<JOB_DETAIL>" + json.dumps(self.job_description_json) + "\n</JOB_DETAIL>\n--\n<WORK_INFORMATION>" + json.dumps(self.tailored_resume) + "\n</WORK_INFORMATION>")
        logger.debug(f"tailord_coverletter_content: {tailord_coverletter_content}")

        try:
            tailord_coverletter_content = tailord_coverletter_content.replace("```json", "").replace("```JSON", "").replace("```", "")
        except Exception as e:
            logger.error(f"Error: error getting cover letter content.\nDetailed error: {e}")
            return f"Error: error getting cover letter content"
        
        coverletter_template_path = os.path.join(self.resources_dir, "jobtailor-coverletter.docx")
        coverletter_curated_path = os.path.join(self.output_dir, self.coverletter_output_file_name)
        try:
            replacements = {
                "{{name}}": self.tailored_resume["name"],
                "{{location}}": self.tailored_resume["location"],
                "{{email}}": self.tailored_resume["email"],
                "{{phone}}": self.tailored_resume["phone"],
                "{{website}}": self.tailored_resume["website"],
                "{{coverletter_content}}": tailord_coverletter_content
            }
            
            doc = Document(coverletter_template_path)
            # Replace placeholders with actual values
            replace_placeholders(doc, replacements)

            # Save the resulting document
            doc.save(coverletter_curated_path)
        except Exception as e:
            logger.error(f"Error: error replacing placeholders in cover letter.\nDetailed error: {e}")
            return f"Error: error replacing placeholders in cover letter"
        
        logger.info('tailored cover letter generated')
        self.write_function("- tailored cover letter generated -")
        return coverletter_curated_path