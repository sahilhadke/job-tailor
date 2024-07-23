from setuptools import setup, find_packages

setup(
    name='jobtailor',
    version='0.1.5',
    packages=find_packages(),
    include_package_data=True,
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=[
        'python-dotenv',
        'google.generativeai',
        'PyPDF2',
        'jinja2',  
        'python-docx'
    ]
)