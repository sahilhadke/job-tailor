import os
from jobtailor import JobTailor
from dotenv import load_dotenv

env = load_dotenv('.env')

gemini_key = (os.getenv("GEMINI_KEY"))
resume_path = "./resources/master_resume.pdf"
pdflatex_path = os.getenv("PDFLATEX_PATH")
output_dir = "./output/"

job_description = """
Overview
Are you interested in our summer 2025 Software Engineering internship? Apply here, and we will reach out to you in late summer when recruiting begins.

 

SIG is looking for highly motivated full-time students for our 10-week software engineering summer internship program. As a software engineering intern, you’ll be part of a team that builds some of the most powerful trading systems in the finance industry. You will work alongside our experienced software engineers on the development, delivery, support, and enhancements of our trading systems and infrastructure.

 

Throughout the summer, you will have the chance to work on challenging projects that will be pushed into production. You’ll also meet with senior technologists to learn about SIG technology and how it impacts our trading strategies.

 

To learn more about what it’s like to work at SIG, check out our campus programs site, where you can take a virtual office tour, meet some of our employees, and learn more about our unique culture!

 


What we're looking for
Students pursuing a BS or MS in Computer Science, Computer Engineering or a similar major
Intention to graduate with a bachelor’s or master’s degree within one year of the internship program
Strong software development skills in any object oriented language (we use C++, Python, and C# the most)
Knowledge of algorithms, data structures, and object-oriented design patterns
A passion for technology and a tinkering spirit
Exceptional problem solving skills
This internship will be a fully in-person experience in our Philadelphia-area headquarters.

 

INTERN PERKS:

Fully-furnished housing provided for duration of internship
Relaxed dress code: jeans and sneakers are the norm and shorts all summer long
A 9,000 square-foot gym with cardio, cross fit, and strength machines
Social events such as dinners in Philadelphia, sporting events, and more!
Discounts for shopping, travel, dining, entertainment, and attractions
On-site services such as dry cleaning, auto repair and detailing, barber, and ATM
On-site Wellness Center staffed with full-time Nurse Practitioner
Follow us on Instagram at @workingatsig to check out what our interns have been up to this summer!

 

ABOUT SIG:

 

SIG is a global quantitative trading firm founded with a growth mindset and an analytical approach to decision making. As one of the largest proprietary trading firms in the world, SIG benefits the financial markets by providing liquidity and ensuring competitive prices for buyers and sellers. SIG brings together the brightest minds, the best technology, and an expansive library of data to design and implement quantitative trading strategies that make us leaders in the financial markets. Beyond trading, SIG is active in global private equity, institutional brokerage, sports analytics, and structured capital.

 

SIG does not accept unsolicited resumes from recruiters or search firms. Any resume or referral submitted in the absence of a signed agreement will become the property of SIG and no fee will be paid.
"""

optional_params = {
    "output_dir": "./output/",
    "pdflatex_path": "/usr/local/texlive/2024/bin/universal-darwin/pdflatex",
}
jt = JobTailor(resume_path, job_description, gemini_key, optional_params)
print("FINAL RESUME = " + jt.tailored_resume_path)
print("FINAL COVERLETTER = " + jt.tailored_coverletter_path)