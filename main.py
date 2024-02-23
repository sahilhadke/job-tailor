import os
from jobtailor import JobTailor
from dotenv import load_dotenv

env = load_dotenv("./.env")

gemini_key = (os.getenv("GEMINI_KEY"))
output_dir = "/Users/sahilhadke/Desktop/JobTailor/job-tailor/"
resume_path = "/Users/sahilhadke/Desktop/JobTailor/job-tailor/resources/sahilhadke_resume_technical.pdf"
job_description = """
SOFTWARE ENGINEER INTERN

11596
Chandler, Arizona
Core Business Hours
Intern
Overview

We are seeking a full-time Software Engineer Intern  in our Chandler, AZ location. In this role, you will be responsible for learning and training to develop software for Garmin's communication and navigation products under supervision.
Essential Functions
Learn to develop software using C, C++, C#, Java, assembly language, or other selected languages
Learn to test software using debuggers, emulators, simulators, and logic analyzers
Learn to perform software releases and software quality assurance activities
Learn to perform maintenance activities for products already in production in addition to new product software design
Basic Qualifications
Completed coursework in Computer Science, Electrical Engineering, Computer Engineering, or a related field
Excellent academics (cumulative GPA greater than or equal to 3.0 as a general rule)
Must possess relevant experience and/or training in languages such as C, C++, C# or Java
Must possess relevant experience and/or training in data structures or object oriented design methodology
Desired Qualifications
Outstanding academics (cumulative GPA greater than or equal to 3.5)
"""

jt = JobTailor(resume_path, job_description, output_dir, gemini_key)
print(jt.job_description_json)

# resume_path_new = jt.get_tailored_resume()
# coverletter_path_new = jt.get_tailored_cover_letter()
# jt.get_metrics()