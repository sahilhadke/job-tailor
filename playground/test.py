import json
from jinja2 import Environment, FileSystemLoader

# Load the JSON data
with open('./playground/resume.json') as f:
    resume_data = json.load(f)

# Set up the Jinja2 environment
file_loader = FileSystemLoader('.')
env = Environment(loader=file_loader)

# Load the LaTeX template
template = env.get_template('./playground/jakes_template.tex')

# Render the template with the data
rendered_tex = template.render(resume_data)

# Write the rendered LaTeX to a file
with open('./playground/jakes_resume.tex', 'w') as f:
    f.write(rendered_tex)