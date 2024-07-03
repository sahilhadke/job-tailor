from setuptools import setup, find_packages

setup(
    name='jobtailor',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'python-dotenv',
        'google.generativeai',
        'PyPDF2',
        'jinja2',  
        'python-docx'
    ]
)