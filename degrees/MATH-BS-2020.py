'''
TODO:  

Need to update specialization checks.

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


spectext = dict({'PURE':'Pure', 'APPL':'Applied', 'COMP':'Computational', '':'NONE DECLARED!!!'})

ISCP = set( ['MATH 3315', 'CSE 3365', 'MATH 3316', 'CS 3365'] )

PURE = set( ['MATH 4339', 'MATH 4351', 'MATH 4355', 'MATH 4381', 'MATH 6337'])
APPL = set( ['MATH 4325', 'MATH 4334', 'MATH 4335', 'MATH 4337', 'MATH 6324', 'MATH 6332', 'MATH 6311', 'MATH 6336'])
COMP = set( ['MATH 4315', 'MATH 4316', 'MATH 4317', 'MATH 4370', 'MATH 4377', 'MATH 6315', 'MATH 6316'])
ADV  = PURE|APPL|COMP


CS  = set( ['ASIM 1310', 'CRCP 1310', 'CSE 1341', 'CSE 1342', 'CSE 2341', 'CSE 3353', 'CEE 3310', 'ME 3310', 'CS 1340', 'CS 1341', 'CS 1342', 'CS 2341', 'CS 3353'] )
STAT = set( ['STAT 3300', 'STAT 3304', 'STAT 4340', 'CSE 4340', 'CS 4340', 'EMIS 3340', 'STAT 5340', 'EE 3360', 'STAT 4341', 'EMIS 7370', 'ECO 5350'] )

PHYS = set( ['PHYS 1303', 'PHYS 1304', 'PHYS 1105', 'PHYS 1106', 'PHYS 1403', 'PHYS 1404',] )
CHEM = set( ['CHEM 1303', 'CHEM 1304', 'CHEM 1113', 'CHEM 1114'] )
BIOL = set( ['BIOL 1301', 'BIOL 1302', 'BIOL 1101', 'BIOL 1102', 'BIOL 1401', 'BIOL 1402'] )
GEOL = set( ['GEOL 1301', 'GEOL 1305', 'GEOL 1307', 'GEOL 1313', 'GEOL 1315', 'GEOL 3340'] ) 
SCI  = PHYS|CHEM|BIOL|GEOL






def create_degree(degcode, speccode=None):


  # create a generic degree instance
  degree = dpr.Degree()


  # add major-specific warnings
  degree.add_major_warning_check(credits_per_semester)
  degree.add_major_warning_check(incomplete_foundation)
  if speccode == 'PURE':
    degree.add_major_warning_check(pure_missing_3311)
  if speccode == 'APPL':
    degree.add_major_warning_check(appl_missing_3313)
  if speccode == 'COMP':
    degree.add_major_warning_check(comp_missing_3315)
  if speccode == None:
    # need to do something here!!!!
    pass


  # Fundamentals for Major
  fund = dpr.Group("Math Foundation")
  fund.add_requirement("Calculus I",      ['MATH 1337', 'MATH 1309'], 1)
  fund.add_requirement("Calculus II",     ['MATH 1338', 'MATH 1340'], 1)
  fund.add_requirement("Calculus III",    ['MATH 3302'], 1)
  fund.add_requirement("Linear Algebra",  ['MATH 3304'], 1)
  fund.add_requirement("Int. to Proof",   ['MATH 3311'], 1)
  fund.add_requirement("Int. to ODEs",   ['MATH 3313'], 1)
  fund.add_requirement("Int. to SC", ISCP, 1)
  fund.add_requirement("Real Analysis",   ['MATH 4338'], 1)
  degree.add_group(fund)

  # Supplemental Courses
  supp = dpr.Group("Supplemental Courses")
  supp.add_requirement("Sci/Eng Statistics", STAT, 1, greedy=True)
  supp.add_requirement("Intro. Programming", CS, minhours=3, greedy=True)
  supp.add_requirement("Science", SCI, minhours=6, greedy=True)
  degree.add_group(supp)


  # Specialization
  spec = dpr.Group("Specialization Electives")
  if speccode == 'PURE':
    spec.add_requirement("Pure Math", PURE, minhours=9)
  if speccode == 'APPL':
    spec.add_requirement("Appl. Math", APPL, minhours=9)
  if speccode == 'COMP':
    spec.add_requirement("Comp. Math", COMP, minhours=9)
  degree.add_group(spec)


  # Electives
  elec = dpr.Group("Additional Electives")
  elec.add_requirement("Extra Math 3000+", ADV, minhours=9, greedy=True)
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
    return dpr.DPRWarning(4, "Foundation incomplete with <= 1 semesters remaining.")
  if uterms <= 2 and not fcomp:
    return dpr.DPRWarning(3, "Foundation incomplete with <= 2 semesters remaining.")
  if uterms <= 3 and not fcomp:
    return dpr.DPRWarning(2, "Foundation incomplete with <= 3 semesters remaining.")
  if uterms <= 4 and not fcomp:
    return dpr.DPRWarning(1, "Aim to complete foundation by the middle of junior year.")

  return None



def pure_missing_3311(student, coursehistory, degree):

  # get necessary information
  ccodes = [c.code for c in coursehistory]
  uterms = dpr.unplanned_terms(student, coursehistory)
  unready = ('MATH 3311' not in ccodes)

  # return appropriate warning
  if uterms <= 1 and unready:
    return dpr.DPRWarning(4, "missing MATH 3311: Pure specializaion impossible.")
  if uterms <= 2 and unready:
    return dpr.DPRWarning(3, "missing MATH 3311: Pure specializaion very unlikely.")
  if uterms <= 3 and unready:
    return dpr.DPRWarning(2, "please change your schedule to be enrolled in MATH 3311.")
  if uterms <= 4 and unready:
    return dpr.DPRWarning(1, "make sure to take MATH 3311 as early as possible.")

  return None


def appl_missing_3313(student, coursehistory, degree):

  # get necessary information
  ccodes = [c.code for c in coursehistory]
  uterms = dpr.unplanned_terms(student, coursehistory)
  unready = ('MATH 3313' not in ccodes)

  # return appropriate warning
  if uterms <= 1 and unready:
    return dpr.DPRWarning(4, "missing MATH 3313: Applied specializaion impossible.")
  if uterms <= 2 and unready:
    return dpr.DPRWarning(3, "missing MATH 3313: Applied specializaion very unlikely.")
  if uterms <= 3 and unready:
    return dpr.DPRWarning(2, "please change your schedule to be enrolled in MATH 3313.")
  if uterms <= 4 and unready:
    return dpr.DPRWarning(1, "make sure to take MATH 3313 as early as possible.")

  return None


def comp_missing_3315(student, coursehistory, degree):

  # get necessary information
  ccodes = [c.code for c in coursehistory]
  uterms = dpr.unplanned_terms(student, coursehistory)
  unready = ('MATH 3315' not in ccodes and 'MATH 3316' not in ccodes and 'CSE 3365' not in ccodes and 'CS 3365' not in ccodes)

  # return appropriate warning
  if uterms <= 1 and unready:
    return dpr.DPRWarning(4, "missing MATH 3315: Computational specializaion no longer possible.")
  if uterms <= 2 and unready:
    return dpr.DPRWarning(3, "missing MATH 3315: Computational specializaion becoming unlikely.")
  if uterms <= 3 and unready:
    return dpr.DPRWarning(2, "please change your schedule to be enrolled in MATH 3315.")
  if uterms <= 4 and unready:
    return dpr.DPRWarning(1, "make sure to take MATH 3315 as early as possible.")

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


