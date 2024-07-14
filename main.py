import os
from jobtailor import JobTailor
from dotenv import load_dotenv

env = load_dotenv('.env')

gemini_key = (os.getenv("GEMINI_KEY"))
resume_path = "./resources/master_resume.pdf"
job_description = """
As a Software Developer Intern, you will build advanced trading and risk applications leveraging cutting-edge technology. DRW enables our Software Developer Interns to develop computationally intensive software under the guidance of senior technologists with the goal of deployment during your ten weeks. While your days will have you immersed in complex projects directly driving DRW’s progress, your evenings will be spent exploring the city with organized social events to truly discover what it is like to live and work in Chicago. 

How you will make an impact...

Design, develop, test, and deploy proprietary software development solutions across the firm. Examples include creating: 
Decoders to receive raw packet data from various exchanges and translate it into a more accessible form.
Normalizers which take decoded data and build a book for each instrument traded on that exchange. 
Applications to facilitate communication around executed trades to our compliance team. 
Identify innovative solutions to complex problems and advocate for their implementation to your team by communicating your ideas in a clear and concise manner.
Conduct robust research using a data driven approach to employ statistical analytics on large data sets.
Collaborate with other software developers, quantitative traders, and researchers as well as business analysts in cross-functional team environments
What you bring to the team...

Are pursuing a bachelor’s, master’s, or PhD in computer science, electrical engineering, computer engineering, physics, mathematics or any related science discipline and have an expected graduation date between December 2025 and June 2026
Have exposure to network programming (TCP/IP), multi‐threaded applications, computational intelligence, algorithms, real‐time programming or GUI programming
Have strong understanding of object-oriented design, data structures, and algorithms
Exhibit excellent software development skills in C++, Python, Java, C#, or C and a deep curiosity to learn and absorb new technologies quickly
"""

optional_params = {
    "output_dir": "./output/",
    "pdflatex_path": "/usr/local/texlive/2024/bin/universal-darwin/pdflatex",
    "resume_output_file_name": "Sahil Hadke - Resume - DRW.pdf",
    "coverletter_output_file_name": "Sahil Hadke - Coverletter - DRW.docx"
}

jt = JobTailor(resume_path, job_description, gemini_key, optional_params)

print("FINAL RESUME = " + jt.tailored_resume_path)
print("FINAL COVERLETTER = " + jt.tailored_coverletter_path)