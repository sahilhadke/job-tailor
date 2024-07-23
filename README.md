# JobTailor - Personalized Resume and Cover Letter Solution

![Logo](https://github.com/sahilhadke/job-tailor/blob/main/resources/jobtailor-architecture.jpg)

JobTailor is a Python package that helps you create a customized resume and cover letter based on a master resume and a specific job description. It leverages the Gemini LLM to generate tailored documents that align with the job requirements.

## Table of Contents

- [What's New](#whats-new)
- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Contributing](#contributing)

## What's New

### Version 0.1.5 - 2024-07-23

- Fixed bug in creating default output folder if not present

## Installation

Here’s how you can install and use JobTailor to generate a tailored resume and cover letter:

#### Prerequisites

- OS : Linux, Mac
- Python : 3.11 and above
- LLM API key: [Gemini API](https://ai.google.dev/)
- pdflatex installed on the machine

#### How to download JobTailor?

- You can install the package from: https://pypi.org/project/jobtailor/
- Alternatively, you can download the source code from: https://github.com/sahilhadke/job-tailor/

#### Package Installation

```bash
pip install jobtailor
```

### Usage

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


## Features

- **Input your master resume and job description**: JobTailor takes these inputs and processes them.
- **Generate curated resume and cover letter**: The output is a resume and cover letter customized to match the job description.
- **Easy to use**: Simple commands to generate your documents.

## Contributing

If you'd like to contribute to this project, please follow the guidelines below.

1. Fork the repository to your GitHub account.
2. Clone your fork to your local machine:
```bash
git clone https://github.com/sahilhadke/job-tailor.git
```
3. Navigate to the project directory:
```bash
cd job-tailor
```
5. Ensure your changes are tested and follow the project's coding standards.
6. Commit your changes with clear and descriptive messages:
```bash
git commit -m "Add login functionality"
```
7. Push your changes to your fork:
```bash
git push origin your-branch-name
```
8. Open a pull request from your fork's branch to the main repository's main branch.
9. Fill out the pull request with details about your changes.

Thank you for your interest in contributing to this project! Together, we can make it better for everyone.
