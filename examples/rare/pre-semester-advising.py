import sys
import string
from os.path import basename

# for reading XLSX files
from openpyxl import load_workbook

# for e-mailing
from smtplib import SMTP_SSL, SMTPException
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

# for degree status
import pydpr as dpr 
from MathMajor import create_degree, autodetect_eng_specialization

# ===============================================
termtext    = 'Fall 2016'
suglink     = 'http://signupgenius.com/####'
# ===============================================


# files with student and course histories
studentfile = './records/current-mathmajors.xlsx'
coursesfile = './records/current-coursehistories.xlsx'
catalogfile = './documents/2016-math-catalog.pdf'
advicefile  = './documents/general-advice.pdf'
emailfile   = './documents/pscheck-email-template.txt'


# get the e-mail template
with open(emailfile, 'r') as myfile:
  emailstring = myfile.read()
email_template = string.Template(emailstring)


# open up the database files
wb = load_workbook(studentfile, read_only=True)
ws = wb[wb.get_sheet_names()[0]]
IDS = [a[0].value for a in ws if a[13].value == 'MAJ']
for studentID in IDS:

  # load student information, and identify precise degree type
  try:
    student = dpr.load_student_from_query(studentfile, studentID)
    courses = dpr.load_courses_from_query(coursesfile, studentID)
    autodetect_eng_specialization(student, courses)
  except dpr.MissingStudentError as mse:
    print("StudentID %s not found in course file %s." % (studentID, studentfile))
    print("This shouldn't happen.  Something is very wrong.")
    quit()
    exit()
  except dpr.MissingCoursesError as mce:
    print("StudentID %s not found in course file %s." % (studentID, coursesfile))
    print("Skipping this student.")
    continue


  # create degree plan and check requirements
  degree = create_degree(student.degreecode, student.speccode)
  degree.check(courses)


  print("%s: %s %s." % (student.ID, student.fname, student.lname), end=' ') 

  # Identify any Warnings
  pr = dpr.ProgressReport(student, courses, degree)
  warnings = ''
  if pr.last_credits < 12:
    warnings += "  * last sem. credits = %d \n" % (pr.last_credits)
  if pr.last_GPA < 2.5:
    warnings += "  * last semester GPA = %2.2f \n" % (pr.last_GPA)
  if pr.last_year_fails > 0:
    warnings += "  * fails in the last year = %d \n" % (pr.last_fails)
  if pr.degree_GPA < 2.5:
    warnings += "  * cumulative degree GPA = %2.2f \n" % (pr.degree_GPA)
  if pr.degree_credits_per_semester > 6:
    warnings += "  * needed degree credits / semester = %2.2f \n" % (pr.degree_credits_per_semester)

  if warnings == '':
    print("no concerns")
    continue
  #else:
  #  print "concerns found."
  #  print warnings
  #  continue

  # create a PDF report of the student's progress
  pdfreport = "math-dpr-%s.pdf"%(studentID)
  dpr.pdf_report(student, courses, degree, pdfreport)

  # set up message
  me = 'snorris@smu.edu'
  you = str(student.email)

  # create the body of the email
  values = dict()
  values['ID']    = student.ID
  values['fname'] = student.fname
  values['lname'] = student.lname
  values['email'] = student.email
  values['term']  = termtext
  values['warninglist'] = warnings
  values['link']  = suglink
  body = email_template.substitute(values)

  #print body
  #continue

  # set up message
  msg = MIMEMultipart()
  msg['From'] = me
  msg['To'] = you
  msg['Date'] = formatdate(localtime=True)
  msg['Subject'] = "Mathematics advising: pre-semester check-in (%s)" % (student.ID)
  msg.attach(MIMEText(body))

  # add attachments
  for f in [pdfreport]:
    with open(f, "rb") as fil:
      msg.attach(MIMEApplication(
        fil.read(),
        Content_Disposition='attachment; filename="%s"' % basename(f),
        Name=basename(f)
      ))

  # send message
  try:
    smtp = SMTP_SSL('smtp.smu.edu:465')
    smtp.login('01370901', 'EfT36Fee13')
    smtp.sendmail(me, [you], msg.as_string())
    print("Successfully sent email to %s" % (student.email))
  except SMTPException:
    print("Error: unable to send email to %s" % (student.email))







