'''
TODO:  

Update warnings.


Eventually we want a global routine provided by pydpr, 
that allows the user to select which degree we want to create.
This routine should accept 'degreecode' and 'speccode' and then
return the appropriate degree.

If this is done using objects, then each degree object should 
include routines such as


pre_check()
check()


'''

import sys
import numpy as np
import pydpr.pydpr as dpr


spectext = dict({'':'None'})

ISCP = set( ['MATH 3315', 'CSE 3365', 'MATH 3316', 'CS 3365'] )

PURE = set( ['MATH 4339', 'MATH 4351', 'MATH 4355', 'MATH 4381', 'MATH 6337'])
APPL = set( ['MATH 4325', 'MATH 4334', 'MATH 4335', 'MATH 4337', 'MATH 6324', 'MATH 6332', 'MATH 6311', 'MATH 6336'])
COMP = set( ['MATH 4315', 'MATH 4316', 'MATH 4317', 'MATH 4370', 'MATH 4377', 'MATH 6315', 'MATH 6316'])
ADV  = PURE|APPL|COMP


CS  = set( ['ASIM 1310', 'CRCP 1310', 'CSE 1341', 'CSE 1342', 'CSE 2341', 'CSE 3353', 'CEE 3310', 'ME 3310', 'CS 1340', 'CS 1341', 'CS 1342', 'CS 2341', 'CS 3353'] )
STAT = set( ['STAT 2331', 'STAT 3300', 'STAT 3304', 'STAT 4340', 'CSE 4340', 'CS 4340', 'EMIS 3340', 'STAT 5340', 'EE 3360', 'STAT 4341', 'EMIS 7370', 'ECO 5350'] )

ME = set(['ME 5302', 'ME 5320', 'ME 5322', 'ME 5336', 'ME 5361', 'ME 5386', 'ME 7302', 'ME 7322',  'ME 7361'])
EE = set(['EE 5330', 'EE 5332', 'EE 5336', 'EE 5360', 'EE 5362', 'EE 5372', 'EE 7330', 'EE 7336', 'EE 7360'])
CE = set(['ME 5336', 'MATH 6336', 'CEE 5331', 'CEE 5332', 'CEE 5334', 'CEE 7331', 'CEE 7332', 'CEE 5361', 'CEE 5364', 'CEE 7361', 'CEE 7364', 'ME 7322'])
OR = set(['EMIS 3360', 'EMIS 5361', 'EMIS 5362', 'EMIS 5369', 'STAT 5344', 'EMIS 5364', 'EMIS 7362'])
CS = set(['CSE 4381', 'CS 4381'])
EDU = set([])
ECO = set([])

OUT = ME|EE|CE|OR|CS|EDU|ECO


def create_degree(degcode, speccode=None):

  # create a generic degree instance
  degree = dpr.Degree()

  # add major-specific warnings
  degree.add_major_warning_check(credits_per_semester)
  degree.add_major_warning_check(incomplete_foundation)

  # Fundamentals for major
  fund = dpr.Group("Math Foundation")
  fund.add_requirement("Calculus I",     ['MATH 1337', 'MATH 1309'], 1)
  fund.add_requirement("Calculus II",    ['MATH 1338', 'MATH 1340'], 1)
  fund.add_requirement("Calculus III",   ['MATH 3302'], 1)
  fund.add_requirement("Linear Algebra", ['MATH 3304'], 1)
  fund.add_requirement("Intro to ODEs",  ['MATH 3313'], 1)
  degree.add_group(fund)

  # Supplemental Courses
  supp = dpr.Group("Supplemental Courses")
  supp.add_requirement("Sci/Eng Statistics", STAT, mincourses=1, greedy=True)
  supp.add_requirement("Intro. Programming", CS,   mincourses=1, greedy=True)

  elec = dpr.Group("Additional Elective(s)")
  elec.add_requirement("Extra Math 3000+", ADV|OUT, mincourses=6, greedy=True)
  elec.add_verification( "ver: Four 4000+ (ANY)", ADV|OUT, 4)
  elec.add_verification( "ver: Two 4000+ (MATH)", ADV, 2)
  degree.add_group(elec)


  #return
  return degree






# ---------------------------------------------------------
#    Degree-specific pre- and post-check routines
# ---------------------------------------------------------

def incomplete_foundation(student, coursehistory, degree):

  # get necessary information
  uterms = dpr.unplanned_terms(student, coursehistory)
  fcomp = degree.grplist[0].satisfied

  # return appropriate warning
  if uterms <= 1 and not fcomp:
    return dpr.DPRWarning(4, "Foundation incomplete with <= 2 semesters remaining.")
  if uterms <= 2 and not fcomp:
    return dpr.DPRWarning(3, "Foundation incomplete with <= 3 semesters remaining.")
  if uterms <= 3 and not fcomp:
    return dpr.DPRWarning(2, "Foundation incomplete with <= 4 semesters remaining.")
  if uterms <= 4 and not fcomp:
    return dpr.DPRWarning(1, "Aim to complete foundation by the end of sophomore year.")
  return None




def credits_per_semester(student, coursehistory, degree, threshhold=6.0):

    # assess remaining credits and semesters
    rem_semesters = (int(student.gterm) - dpr.current_term())*2/10
    rem_credits = degree.hours_rem
    if rem_semesters < 1: 
      cps = np.inf if rem_credits > 0 else 0
    else:
      cps = float(rem_credits) / float(rem_semesters)

    # return the appropriate response
    warning = None
    if cps == np.inf:
      return dpr.DPRWarning(4, "graduation not possible by intended date")
    if cps > 11.9:
      return dpr.DPRWarning(3, "courses per semester >= 4")
    if cps > 8.9:
      return dpr.DPRWarning(2, "courses per semester >= 3")
    if cps > 5.9:
      return dpr.DPRWarning(1, "courses per semester >= 2")

    return None


