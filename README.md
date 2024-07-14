# JobTailor - Personalized Resume and Cover Letter Solution


![Logo](https://github.com/sahilhadke/job-tailor/blob/main/resources/jobtailor-architecture.jpg)

JobTailor is a Python package that helps you create a customized resume and cover letter based on a master resume and a specific job description. It leverages the Gemini LLM to generate tailored documents that align with the job requirements.

## Features

- **Input your master resume and job description**: JobTailor takes these inputs and processes them.
- **Generate curated resume and cover letter**: The output is a resume and cover letter customized to match the job description.
- **Easy to use**: Simple commands to generate your documents.

## How to download JobTailor?

- You can install the package from: https://pypi.org/project/jobtailor/
- Alternatively, you can download the source code from: https://github.com/sahilhadke/job-tailor/

## Installation

Here’s how you can install and use JobTailor to generate a tailored resume and cover letter:

#### Prerequisites

- OS : Linux, Mac
- Python : 3.11 and above
- LLM API key: [Gemini API](https://ai.google.dev/)

#### Package Installation and Usage

```bash
pip install jobtailor
```

```python
from jobtailor import JobTailor

jt = JobTailor(
    resume_path='<resume_path>', 
    job_description='<job_description_text>', 
    gemini_key='<gemini_key>', 
    optional_params={
        "output_dir": "<output_dir>", # Default: "./output/"
        "pdflatex_path": "<pdflatex_installation_path>/pdflatex", # Default is "pdflatex" global access
        "resume_output_file_name": "<desired_resume_output_file_name>.pdf", # Default: jobtailor-curated-resume.pdf 
        "coverletter_output_file_name": "<desired_coverletter_output_file_name>.docx" # Default: jobtailor-curated-coverletter.docx
    }
)

print("FINAL RESUME = " + jt.tailored_resume_path)
print("FINAL COVERLETTER = " + jt.tailored_coverletter_path)
```
