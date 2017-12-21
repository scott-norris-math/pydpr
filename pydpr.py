'''
TODO:  

Need to implement a general, object-based functionality whereby departments 
create their own warning criteria, in the department's Major definition file.
It should be expected that all MDCs have a callable warning_list() function,
the results of which are then added to the global warning list in the DPR
report (which departments can *not* edit).

'''


import copy
import time
import os.path
import numpy as np
import matplotlib.pyplot as plt
from subprocess import call
from openpyxl import load_workbook
from colorama import init, Fore, Back, Style



init()


# lookup tables for common codes
termcodes = ['Jan', 'Spring', 'May', 'Summer', 'August', 'Fall', 'Fall']
degreetext = dict({'BA':'Bachelor of ARTS (no science)', 'BS':'Bachelor of Science', 'MN':'Minor'})

# Define a dictionary for grade to GPA conversion
GPAlookup = dict()
GPAlookup[' '] = 4.0
GPAlookup['NOW'] = 4.0
GPAlookup['CR'] = 4.0
GPAlookup['A']  = 4.0
GPAlookup['A-'] = 3.7
GPAlookup['B+'] = 3.3
GPAlookup['B']  = 3.0
GPAlookup['B-'] = 2.7
GPAlookup['C+'] = 2.3
GPAlookup['C']  = 2.0
GPAlookup['C-'] = 1.7

GPAlookup['D+'] = 1.3
GPAlookup['D']  = 1.0
GPAlookup['D-'] = 0.7
GPAlookup['F']  = 0.0
GPAlookup['W'] = 0.0
GPAlookup['I'] = 0.0
GPAlookup['P'] = 0.0

GPAlookup['ED+'] = 1.3
GPAlookup['ED'] = 1.0
GPAlookup['ED-'] = 0.7
GPAlookup['EF'] = 0.0

GPAlookup['TD'] = 1.0
GPAlookup['TF'] = 0.0

GPAgrades = set(['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F'])


class Error(Exception):
# base class for exceptions in this module
  pass

class MissingStudentError(Error):
# raised when a student is not found in the student list

  def __init__(self, studentID, queryfile):
    self.studentID = studentID
    self.queryfile = queryfile

class MissingCoursesError(Error):
# raised when a student is not found in the coursehistory list

  def __init__(self, studentID, queryfile):
    self.studentID = studentID
    self.queryfile = queryfile

class MissingFileError(Error):
# raised when a student is not found in the coursehistory list

  def __init__(self, queryfile):
    #self.studentID = studentID
    self.queryfile = queryfile




# =====================================
#     Input / Output
# =====================================



"""
This function reads $queryfile [which is assumed to be an XLSX file] looking for a given $studentID in column 0.  If the student ID is found, then demographic information is read from the row.  At the moment, the columns associated with each piece of information are hard-coded.  This could be set up in a configuration file if desired.
"""

def load_student_from_query(queryfile, studentID):

  # read the list of students
  wb = load_workbook(queryfile)
  ws = wb[wb.get_sheet_names()[0]]

  # find the indicated student
  #for a in ws:
  #  print a[0].value

  record = [a for a in ws if str(a[0].value) == str(studentID)]
  if len(record) == 0:
    print("Student ID %s not found in student file %s." % (studentID, queryfile))
    raise MissingStudentError(studentID, queryfile)


  # extract a summary of the student's information
  s = Student()
  row = record[0]
  s.ID  = str(row[0].value)
  s.lname = row[2].value
  s.fname = row[3].value
  s.email = row[4].value
  s.degree = row[22].value
  s.degreecode = s.degree.split('-')[1]

  s.speccode = row[24].value
  if s.speccode != None:
    s.speccode = s.speccode.split('-')[1]

  # admit and expected graduation terms
  s.aterm = str(row[16].value)
  s.gterm = str(row[17].value)

  s.gyear  = 2000+int(s.gterm[1:3])
  s.gsess  = int(s.gterm[3])
  #s.gstatus = row[7].value

  return s



# this function reads a course history from a single text file, 
# that results from copying the my.SMU course history table,
# and pasting it into a text file.


"""
This function reads $queryfile [which is assumed to be an XLSX file] looking for all rows containing a given $studentID in column 0.  Each row is assumed to represent a course taken by that student, and course details are read from the row, resulting in a list of Course() data structures.  At the moment, the columns associated with each piece of course information are hard-coded.  This could be set up in a configuration file if desired.
"""

def load_courses_from_query(queryfile, studentID):

  wb   = load_workbook(queryfile)
  ws   = wb[wb.get_sheet_names()[0]]

  #for a in ws:
  #  print a[0].value, studentID, a[0].value == studentID
  rows = [a for a in ws if str(a[0].value) == str(studentID)]

  if len(rows) == 0:
    print("Student ID %s not found in course query file %s." % (studentID, queryfile))
    raise MissingCoursesError(studentID, queryfile)

  courselist = []
  for row in rows:
    course = Course()
    course.term    = row[4].value
    course.dept    = row[5].value
    course.number  = row[6].value
    course.code    = course.dept + ' ' + str(course.number)
    course.name    = row[8].value
    course.grade   = row[9].value
    course.credits = row[10].value
    course.credit_awarded = row[11].value
    #course.status  = row[].value

    if course.credits == 0:
      continue

    if course.grade == None:
      course.grade = 'NOW'

    courselist.append(course)

  return courselist



# this function reads a course history from a single text file, 
# which must be the result of copying the my.SMU course history 
# table, for a specific student, and pasting it into a text file.

def load_courses_from_webtext(courselistfile):

  if not os.path.isfile(courselistfile):
    print("Manual file %s not found.  Exiting." % (courselistfile))
    raise MissingFileError(courselistfile)

  f = open(courselistfile, 'r')

  endc = -1
  courselist = []
  lookahead = f.readline()
  while lookahead != '':

    course = Course()
    course.code    = lookahead[:endc]
    course.name    = f.readline()[:endc]
    course.term    = f.readline()[:endc]
    course.grade   = f.readline()[:endc]
    course.credits = f.readline()[:endc]
    course.status  = f.readline()[:endc]
    lookahead      = f.readline()

    words = course.code.split(' ')
    course.dept = words[0]
    course.number = words[1]
    course.termsort = convert_term_name(course.term)

    courselist.append(course)

  f.close()
  return courselist




# =====================================
#     Utilities
# =====================================


def termcode_to_text(termcode):

  if termcode == None:  return None
  termcode = str(termcode)

  try:
    century = int(termcode[0])
    year2d  = int(termcode[1:3])
    term    = int(termcode[3])
    yeartxt = str(1900 + century*100 + year2d)
    termtxt = termcodes[term-1]
    return yeartxt + ' ' + termtxt
  except Exception:
    return termcode




def convert_term_name(termname):

  words = termname.split(' ')
  season = words[0]
  year   = words[1]
  syear  = int(year[2:])

  if season == 'Fall':
    newname = "%2d%2d-fall" % (syear, syear+1) 
  else:
    newname = "%2d%2d-spring" % (syear-1, syear)
  return newname


def current_term():

  date = time.localtime()
  year = date.tm_year
  month = date.tm_mon

  term = 1000 + (year - 2000)*10
  if month <= 6:  term += 2
  if month > 6:  term += 7
  return term





# =====================================
#     Essential Objects
# =====================================



'''
class Student()
----------------
A Student is an object for storing student information.  This includes
- student ID
- last name
- first name
- email address
- graduation date
- degree and specialization
'''

class Student:

  def __init__(self, ID="", lname="", fname="", email="", gcode="", degree="", subtype="", gyear="", aterm="", gterm="", degreecode="", speccode=""):

    self.ID = ID
    self.lname = lname
    self.fname = fname
    self.email = email
    self.gcode = gcode
    self.gyear = gyear
    self.aterm = aterm
    self.gterm = gterm
    #self.degree = degree
    #self.subtype = subtype
    #self.degreecode = degreecode
    #self.speccode = speccode




'''
class Course()
----------------
A Course is an object for storing courses that have been taken or are being taken.  Field include
- course code
- course title
- term
- grade
- credits
- credit status
'''

# A Course is just a record of a course that is being taken or has been taken.
# It is a simple object with several fields decribing the course code, name, term,
# grade, credits, and status.

class Course:

  def __init__(self, code=None, name=None, term=None, grade=None, credits=0, status=None):

    self.dept  = None
    self.number = None
    self.code = code
    self.name = name
    self.term = term
    self.grade = grade
    self.credits = credits
    self.status = status


'''
Requirement()
---------------
The most basic building block for describing degrees, a Requirement is simply a list of courses, with a parameter specifying the minimum number of such courses that must be taken.  Examples include

- a single, absolutely-required course       Requirement("Calc I", ["MATH 1337"], 1)
- a certain number of courses from a list    Requirement("Two Science", ["", "", "", ...], 2)
'''

class Requirement(object):

  def __init__(self, name, courselist, mincourses=0, minhours=0):

    self.name       = name
    self.courselist = set(courselist)

    self.minhours   = minhours
    self.mincourses = mincourses

    self.satcourses = []
    self.satisfied  = False
    return 


  def check(self, coursehistory, verlist=None):

    # identify courses also satisfying verifications
    vercourses = set()
    if verlist != None:
      for ver in verlist:
        for course in ver.courselist:
          if course in self.courselist:
            vercourses.add(course)


    # first find satisfying courses that are *also* in the verification lists
    templist = []
    for course in vercourses:
      satisfying_course = [cc for cc in coursehistory if (cc.code == course and cc.credits > 0 and GPAlookup[cc.grade] > 1.5)]
      if satisfying_course != []:
        templist.append(satisfying_course[0])
    templist.sort(key=lambda course: course.term)
    self.satcourses.extend(templist)

    # now find satisfying courses that are *not* in the verification list
    templist = []
    for course in self.courselist - vercourses:
      satisfying_course = [cc for cc in coursehistory if (cc.code == course and cc.credits > 0 and GPAlookup[cc.grade] > 1.5)]
      if satisfying_course != []:
        templist.append(satisfying_course[0])
    templist.sort(key=lambda course: course.term)
    self.satcourses.extend(templist)

    # truncate the list to the size of the requirement
    if self.mincourses > 0:
      if len(self.satcourses) > self.mincourses:
        self.satcourses = self.satcourses[:self.mincourses]
      self.satisfied = (len(self.satcourses) >= self.mincourses)
    if self.minhours > 0:
      templist = []
      cumhours = 0
      for course in self.satcourses:
        templist.append(course)
        cumhours += course.credits
        if cumhours > self.minhours:
          break
      self.satcourses = templist
      self.satisfied = (cumhours >= self.minhours)

    return 




'''
Group()
-------------
A Group is the main organizing class for degrees, in that a Degree is simply a list of Groups.  In turn, a Group is a list of Requirements, supplemented by an (optional) list of Verifications.  The only difference between a Requirement and a Verification is that a Verification is not exclusive -- i.e. a single class can work toward satisfying multiple Verifications, whereas it can only satisfy a single Requirement within a Degree.
'''


# ----------------------------------------------------
# A Group a list of requirements, plus verifications.
# ----------------------------------------------------

class Group(object):

  def __init__(self, name=None, reqlist=None, verlist=None):

    self.name       = name
    self.reqlist    = [] if reqlist == None else reqlist
    self.verlist    = [] if verlist == None else verlist
    self.satisfied  = False
    self.satcourses = []
    return 


  def add_requirement(self, name, courselist, mincourses=0, minhours=0):
    req = Requirement(name, courselist, mincourses, minhours)
    self.reqlist.append(req)
    return


  def add_verification(self, name, courselist, mincourses=0, minhours=0):
    req = Requirement(name, courselist, mincourses, minhours)
    self.verlist.append(req)
    return


  def check(self, coursehistory):

    for req in self.reqlist:
      req.check(coursehistory, self.verlist)
      for course in req.satcourses:
        self.satcourses.append(course)

    for ver in self.verlist:
      ver.check(coursehistory)
      #for course in ver.satcourses:        # Here is where a verifcation is 
      #  self.satcourses.append(course)     # different than a requirement

    reqs_satisfied = (False not in [req.satisfied for req in self.reqlist])
    vers_satisfied = (False not in [ver.satisfied for ver in self.verlist])
    self.satisfied = (reqs_satisfied and vers_satisfied)
    return


# ------------------------------
# A Degree is a list of Groups.
# ------------------------------

class Degree:

  def __init__(self, name=None, grplist=None):

    self.name = name
    self.grplist = [] if grplist == None else grplist
    self.complete = False
    self.required_credits = 0

    # optional opportunity to customize degree checking and warning reporting
    self.pre_check_routines = []
    self.dept_warning_checks = []


  def add_group(self, group):
    self.grplist.append(group)
    return

  def check(self, coursehistory):

    # run any pre-check routines
    for pcr in self.pre_check_routines:
      pcr(self, coursehistory)

    # make a copy of the courselist and analyze it
    courses = copy.deepcopy(coursehistory)
    for grp in self.grplist:
      grp.check(courses)
      for rr in grp.satcourses:
        courses = [cc for cc in courses if cc.code != rr.code]  # removes already-used courses
    self.complete = (False not in [grp.satisfied for grp in self.grplist])

    ## run any red-flag checks
    #for rfr in self.red_flag_checks:
    #  rfr(self, coursehistory)

    return




# -------------------------------
#    TODO:  DPR Warning
# -------------------------------

'''
The idea here is to abstract the idea of a DPR warning, so that red-flag conditions can be specified separately from the basic definitions of Degree / Group / Requirement / Course.  Crucially, it would be nice to have some "standard" or "general" red flags, but also allow departments to implement their own red-flag conditions in the major definition file.  

Not implemented yet -- currently red flags are caught in the class called ProgressReport() in this file.
'''

class DPRWarning():

  def __init__(self, checker, template, lookup):

    self.checker  = checker		# a callback function of the form check(student, coursehistory, degree)
    self.template = template	# a templated string reporting the warning if checker returns true
    self.lookup   = lookup		# 
    '''
    What if checker() returns [template, lookupdict]?
    What if checker() simply returns the warning string?
    '''


  def check(self, student, coursehistory, degree):
    pass

  def render(self, color=False):
    if color:
      warnstring = Fore.RED+"Warning:"+Style.RESET_ALL+"  "
    else:
      warnstring = "Warning:  "
    warnstring +=  string.Template(self.template).substitute(self.lookup)
    return warnstring





# -------------------------------
#    Reporting Capabilities
# -------------------------------

'''
Halfway solution to a clean implementation of degree red flags.  All red flags are hard-coded into this object.
'''

class ProgressReport:

  def __init__(self, student, coursehistory, degree):

    self.last_GPA = None
    self.last_credits = None
    self.last_year_fails = None
    self.degree_GPA = None
    self.degree_rem_credits = None
    self.degree_rem_semesters = None
    self.degree_credits_per_semester = None

    this_term = int(current_term())
    last_term = this_term - 5
    last_year = this_term - 10

    # get last semester's courses
    courses_ls = [cc for cc in coursehistory if int(cc.term) == last_term and cc.grade in GPAgrades]

    # calculate last semester's GPA
    gpoints = np.array([GPAlookup[cc.grade] for cc in courses_ls]) 
    credits = np.array([cc.credits for cc in courses_ls])
    self.last_credits = sum(credits)
    self.last_GPA = np.dot(gpoints, credits) / sum(credits)

    # count failed courses last semester
    failset = set(['F', 'D-', 'D', 'D+'])
    courses_ly = [cc for cc in coursehistory if int(cc.term) >= last_year and cc.grade in GPAgrades]
    self.last_year_fails = len([cc for cc in courses_ly if cc.grade in failset])

    # get all degree courses
    degcourses = []
    for grp in degree.grplist:
      for cc in grp.satcourses:
        degcourses.append(cc)

    # calculate degree GPA
    degcourseset = set([cc.code for cc in degcourses])
    alldegcourses = [cc for cc in coursehistory if cc.code in degcourseset and cc.grade in GPAgrades]
    gpoints = np.array([GPAlookup[cc.grade] for cc in alldegcourses]) 
    credits = np.array([cc.credits for cc in alldegcourses])
    self.degree_GPA = np.dot(gpoints, credits) / sum(credits)
  
    # assess remaining credits and semesters
    self.degree_rem_semesters = (int(student.gterm) - current_term())*2/10
    self.degree_rem_credits = degree.required_credits - sum([ cc.credits for cc in degcourses ])
    if self.degree_rem_semesters < 1: 
      self.degree_credits_per_semester = np.inf if self.degree_rem_credits > 0 else 0
    else:
      self.degree_credits_per_semester = float(self.degree_rem_credits) / float(self.degree_rem_semesters)


    # here add a set of progress report




# ================================================
#     reporting and visualization
# ================================================




'''
terminal_report()
-----------------
This prints a report of the student's progress to the terminal, using Colorama for colored text.
'''

def terminal_report(student, courselist, degree):


    # get a ProgressReport
    pr = ProgressReport(student, courselist, degree)

    # Assessment of Degree progress
    credits_per_sem = pr.degree_credits_per_semester
    credit_rating = ""
    if   credits_per_sem == 0.0:  credit_rating = Fore.CYAN    + 'COMPLETE!!'  + Style.RESET_ALL
    elif credits_per_sem <= 3.0:  credit_rating = Fore.GREEN   + 'excellent!'  + Style.RESET_ALL
    elif credits_per_sem <= 4.5:  credit_rating = Fore.YELLOW  + 'acceptable.' + Style.RESET_ALL
    elif credits_per_sem <= 6.0:  credit_rating = Fore.YELLOW  + 'caution ...' + Style.RESET_ALL
    elif credits_per_sem <= 7.5:  credit_rating = Fore.RED     + 'concern!'    + Style.RESET_ALL
    else:                         credit_rating = Fore.MAGENTA + 'CRITICAL!!'  + Style.RESET_ALL
    credit_report = "needs %d credits over %d semesters: %s" % (pr.degree_rem_credits, pr.degree_rem_semesters, credit_rating)

    # student and degree information
    report  = "\n\n"
    report += student.lname + ", " + student.fname + "\n"
    report += "-"*25 + "\n"
    report += "SMU ID:      " + str(student.ID) + "\n"
    report += "Email:       " + str(student.email) + "\n"
    report += "Admitted:    " + termcode_to_text(student.aterm) + "\n"
    report += "Graduates:   " + termcode_to_text(student.gterm) + "\n"
    report += "Degree:      " + str(degree.name) + "\n"
    report += "Status:      " + str(credit_report) + "\n"
    report += "\n"

    # loop through the groups
    for grp in degree.grplist:

      grpstatus = Fore.GREEN+'satisfied'+Style.RESET_ALL if grp.satisfied else Fore.RED+'not satisfied'+Style.RESET_ALL
      report += "{0:24}: {1:16}".format(grp.name, grpstatus) + '\n'
      report += '-'*64 + '\n'

      # now loop through the requirements
      for req in grp.reqlist:
        nullcourse = Course()
        nullcourse.term = '(none)'
        nullcourse.code = '(none)'
        nullcourse.grade = '-'

        if (req.minhours > 0):
          sathours = sum([cc.credits for cc in req.satcourses])
          remhours = max(0, req.minhours - sathours)
          for kk,cc in enumerate(req.satcourses):
            counter = '' if (len(req.satcourses)==1 and remhours==0) else ' ' + str(kk)
            report += "{0:24} {1:16} {2:16} {3:4}".format(req.name+counter, cc.code, termcode_to_text(cc.term), cc.grade) + '\n'
          blanklns = int(np.ceil(remhours / 3.0))
          cc = nullcourse if len(req.satcourses) < kk else req.satcourses[kk-1]
          for kk in range(blanklns):
            report += "{0:24} {1:16} {2:16} {3:4}".format(req.name+counter, cc.code, termcode_to_text(cc.term), cc.grade) + '\n'
        if (req.mincourses > 0):
          for kk in range(1,req.mincourses+1):
            counter = '' if req.mincourses == 1 else ' '+str(kk)
            cc = nullcourse if len(req.satcourses) < kk else req.satcourses[kk-1]
            report += "{0:24} {1:16} {2:16} {3:4}".format(req.name+counter, cc.code, termcode_to_text(cc.term), cc.grade) + '\n'

      # now loop through verifications
      for ver in grp.verlist:
        reqstatus = Fore.GREEN+'satisfied'+Style.RESET_ALL if ver.satisfied else Fore.RED+'not satisfied'+Style.RESET_ALL
        report += '{0:24}: {1}'.format(ver.name, reqstatus) + '\n'
      report += '\n'

    # Warnings
    if pr.last_credits < 12:
      report += Fore.RED+"Warning:"+Style.RESET_ALL+" last sem. credits = %d \n" % (pr.last_credits)
    if pr.last_GPA < 2.5:
      report += Fore.RED+"Warning:"+Style.RESET_ALL+" last semester GPA = %2.2f \n" % (pr.last_GPA)
    if pr.last_year_fails > 0:
      report += Fore.RED+"Warning:"+Style.RESET_ALL+" fails in last year = %d \n" % (pr.last_year_fails)
    if pr.degree_GPA < 2.5:
      report += Fore.RED+"Warning:"+Style.RESET_ALL+" cumulative degree GPA = %2.2f \n" % (pr.degree_GPA)
    if pr.degree_credits_per_semester > 6:
      report += Fore.RED+"Warning:"+Style.RESET_ALL+" needed degree credits / semester = %2.2f \n" % (pr.degree_credits_per_semester)

    return report



'''
terminal_report()
-----------------
This saves a textual report of the student's progress to the file $ID.pdf.
'''

def pdf_report(student, courselist, degree, pdfname):

    # get a ProgressReport
    pr = ProgressReport(student, courselist, degree)

    # Assessment of Degree progress
    credits_per_sem = pr.degree_credits_per_semester
    credit_rating = ""
    if   credits_per_sem == 0.0:  credit_rating = 'COMPLETE!!'
    elif credits_per_sem <= 3.0:  credit_rating = 'excellent!'
    elif credits_per_sem <= 4.5:  credit_rating = 'acceptable.'
    elif credits_per_sem <= 6.0:  credit_rating = 'caution ...'
    elif credits_per_sem <= 7.5:  credit_rating = 'concern!'
    else:                         credit_rating = 'CRITICAL!!'
    credit_report = "needs %d credits over %d semesters: %s" % (pr.degree_rem_credits, pr.degree_rem_semesters, credit_rating)

    # student and degree information
    report  = ""
    report += student.lname + ", " + student.fname + "\n"
    report += "-"*25 + "\n"
    report += "SMU ID:      " + str(student.ID) + "\n"
    report += "Email:       " + str(student.email) + "\n"
    report += "Admitted:    " + termcode_to_text(student.aterm) + "\n"
    report += "Graduates:   " + termcode_to_text(student.gterm) + "\n"
    report += "Degree:      " + str(degree.name) + "\n"
    report += "Status:      " + str(credit_report) + "\n"
    report += "\n\n"

    # loop through the groups
    for grp in degree.grplist:

      grpstatus = 'SATISFIED' if grp.satisfied else 'NOT SATISFIED'
      report += "{0:24}: {1:16}".format(grp.name, grpstatus) + '\n'
      report += '-'*64 + '\n'

      # now loop through the requirements
      for req in grp.reqlist:

        nullcourse = Course()
        nullcourse.term = '________________'
        nullcourse.code = '________________'
        nullcourse.grade = '____'
        nc = nullcourse

        if (req.minhours > 0):
          sathours = sum([cc.credits for cc in req.satcourses])
          remhours = max(0, req.minhours - sathours)
          for kk,cc in enumerate(req.satcourses):
            counter = '' if (len(req.satcourses)==1 and remhours==0) else ' ' + str(kk)
            report += '\n'
            report += "{0:24} {1:16} {2:16} {3:4}".format(req.name+counter, cc.code, termcode_to_text(cc.term), cc.grade) + '\n'
          blanklns = int(np.ceil(remhours / 3.0))
          cc = nullcourse if len(req.satcourses) < kk else req.satcourses[kk-1]
          for kk in range(blanklns):
            report += '\n'
            report += "{0:24} {1:16} {2:16} {3:4}".format(req.name+counter, nc.code, termcode_to_text(nc.term), nc.grade) + '\n'

        if (req.mincourses > 0):
          for kk in range(1,req.mincourses+1):
            counter = '' if req.mincourses == 1 else ' '+str(kk)
            cc = nullcourse if len(req.satcourses) < kk else req.satcourses[kk-1]
            report += '\n'
            report += "{0:24} {1:16} {2:16} {3:4}".format(req.name+counter, cc.code, termcode_to_text(cc.term), cc.grade) + '\n'

      # now loop through verifications
      for ver in grp.verlist:
        reqstatus = 'SATISFIED' if ver.satisfied else 'NOT SATISFIED'
        report += '{0:24} {1}'.format(ver.name, reqstatus) + '\n'
      report += '\n\n'

    # Warnings
    if pr.last_credits < 12:
      report += "WARNING: last sem. credits = %d \n" % (pr.last_credits)
    if pr.last_GPA < 2.5:
      report += "WARNING: last semester GPA = %2.2f \n" % (pr.last_GPA)
    if pr.last_year_fails > 0:
      report += "WARNING: fails in last year = %d \n" % (pr.last_year_fails)
    if pr.degree_GPA < 2.5:
      report += "WARNING: cumulative degree GPA = %2.2f \n" % (pr.degree_GPA)
    if pr.degree_credits_per_semester > 6:
      report += "WARNING: needed degree credits / semester = %2.2f \n" % (pr.degree_credits_per_semester)

    # write to textfile
    sp = 'temp-report-%s' % (student.ID)
    outfile = open('%s.txt' % (sp), 'w')
    outfile.write(report)
    outfile.close()

    # convert to pdf and clean up
    call('enscript -p %s.ps --margins=72:72:72:72 --no-header %s.txt'%(sp, sp), shell=True)
    call('ps2pdf %s.ps %s'%(sp, pdfname), shell=True)
    call('rm %s.txt %s.ps'%(sp, sp), shell=True)

    return 



'''
Uses Matplotlib to bring up a plot of the student's GPA progression.
'''

def plot_gpa_progression(courselist):
  terms  = [c.term for c in courselist]
  uterms = np.unique(terms)
  sterms = np.sort(uterms)
  aterms = (np.array( [float(t) for t in sterms] ) - 1000) / 10.0 + .05

  credits = np.empty(len(sterms))
  gpoints = np.empty(len(sterms))
  GPA  = np.empty(len(sterms))
  for kk,term in enumerate(sterms):
    courses     = [c for c in courselist if (c.term == term and c.grade in GPAgrades)]
    credits[kk] = sum([c.credits for c in courses])
    gpoints[kk] = sum([c.credits*GPAlookup[c.grade] for c in courses])
    GPA[kk]     = gpoints[kk] / credits[kk] if credits[kk] > 0 else 0

  totalGPA = sum(gpoints) / sum(credits)


  #trend lind for aterms, GPA, weighted by credits
  from lmfit import minimize, Parameters
  def model(params, x):
    value = params['a']
    slope = params['b']
    return value + slope * x

  def residual(params, x, data, weights):
    delta = data - model(params, x)
    return delta*weights

  params = Parameters()
  params.add('a', value=3.5)
  params.add('b', value=0.0)
  output = minimize(residual, params, args=(aterms, GPA, credits))


  fig, ax = plt.subplots(figsize=(6,4))

  # background
  ax.axhspan(0.0, 2.0, alpha=0.5, color='red')
  ax.axhspan(2.0, 2.7, alpha=0.5, color='orange')
  ax.axhspan(2.7, 3.3, alpha=0.5, color='yellow')
  ax.axhspan(3.3, 3.7, alpha=0.5, color='greenyellow')
  ax.axhspan(3.7, 4.3, alpha=0.5, color='green')

  # GPA circles and average value
  ax.scatter(aterms, GPA, s=25*credits, color='white', marker='o', alpha=0.66, zorder=5)
  ax.plot(aterms, model(output.params, aterms), 'k--', linewidth=4, zorder=6)

  # setting axes
  xmin = np.floor(min(aterms))
  xmax = np.ceil(max(aterms))
  plt.xlim(xmin, xmax)
  plt.xticks(np.arange(xmin, xmax+1))
  plt.ylim(1,4.1)
  plt.title('Overall GPA is %1.3f' % (totalGPA))
  plt.xlabel('Term')
  plt.tight_layout()
  plt.show()
