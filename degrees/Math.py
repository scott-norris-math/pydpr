'''
TODO:  

Need specific departmental warnings in the following cases:

Spring of Sophomore year (5 sem remaining), and not taking 3308.
Fall of Junior year (4 sem remaining), and not taking CSE 1341.
Spring of Junior year (3 sem remaining), and not taking 3337.
Spring of Junior year (3 sem remaining), and not taking 3315.

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
import pydpr.pydpr as dpr


spectext = dict({'PM':'Pure', 'ANU':'Applied/Numerical', 'CSE':'Computer Science', 'OR':'Operations Research', 'ENG-EE':'Elec. Eng.', 'ENG-ME':'Mech. Eng.', '':'NONE DECLARED!!!'})

CAL1 = set( ['MATH 1337', 'MATH 1309'] )
CAL2 = set( ['MATH 1338', 'MATH 1340'] )
CORE = set( ['MATH 3302', 'MATH 2339', 'MATH 3304', 'MATH 3353', 'MATH 3313', 'MATH 2343'] )

IPRF = set( ['MATH 3308', 'MATH 3311'] )
ISCP = set( ['MATH 3315', 'CSE 3365', 'MATH 3316'] )

PURE = set( ['MATH 3337', 'MATH 4338', 'MATH 4351', 'MATH 4355', 'MATH 4381', 'MATH 5331', 'MATH 5353', 'MATH 6337'])
APPL = set( ['MATH 3334', 'MATH 3337', 'MATH 4337', 'MATH 4325', 'MATH 4335', 'MATH 5331', 'MATH 5334', 'MATH 5353', 'MATH 6324'])
COMP = set( ['MATH 4315', 'MATH 4370', 'MATH 5315', 'MATH 5316', 'MATH 6315', 'MATH 6316', 'CSE 7365'])
ADV  = PURE|APPL|COMP
APNU = APPL|COMP


CSE  = set( ['ASIM 1310', 'CRCP 1310', 'CSE 1341', 'CSE 1342', 'CEE 3310'] )
STAT = set( ['STAT 4340', 'CSE 4340', 'EMIS 3340', 'STAT 5340', 'EE 3360', 'STAT 4341', 'EMIS 7370', 'ECO 5350'] )

PHYS = set( ['PHYS 1303', 'PHYS 1304', 'PHYS 1105', 'PHYS 1106', 'PHYS 1403', 'PHYS 1404',] )
CHEM = set( ['CHEM 1303', 'CHEM 1304', 'CHEM 1113', 'CHEM 1114'] )
BIOL = set( ['BIOL 1301', 'BIOL 1302', 'BIOL 1101', 'BIOL 1102', 'BIOL 1401', 'BIOL 1402'] )
GEOL = set( ['GEOL 1301', 'GEOL 1305', 'GEOL 1307', 'GEOL 1313', 'GEOL 1315', 'GEOL 3340'] ) 
SCI  = PHYS|CHEM|BIOL|GEOL

ENG1 = set(['MATH 3337', 'MATH 4337', 'MATH 4325', 'MATH 4315', 'MATH 4370', 'MATH 5315', 'MATH 5316', 'MATH 5331', 'MATH 5334', 'MATH 6315', 'MATH 6316', 'CSE 7365'])

MEG2 = set(['ME 4322', 'ME 4360', 'ME 5302', 'ME 5320', 'ME 5322', 'ME 5336', 'ME 5361', 'ME 5386', 'ME 7302', 'ME 7322',  'ME 7361'])
EEG2 = set(['EE 5330', 'EE 5332', 'EE 5336', 'EE 5360', 'EE 5362', 'EE 5372', 'EE 7330', 'EE 7336', 'EE 7360', 'EE 3322', 'EE 3330', 'EE 3372'])
CEG2 = set(['ME 4322', 'ME 5336', 'MATH 6336', 'CEE 5331', 'CEE 5332', 'CEE 5334', 'CEE 7331', 'CEE 7332', 'CEE 5361', 'CEE 5364', 'CEE 7361', 'CEE 7364', 'ME 4322', 'ME 5322', 'ME 7322'])
ORG2 = set(['EMIS 3360', 'EMIS 5361', 'EMIS 5362', 'EMIS 5369', 'STAT 5344', 'EMIS 5364', 'EMIS 7362'])
CSG2 = set()



def create_degree(degcode, speccode):

  degree = dpr.Degree()

  # If it is a minor, adjust and return
  if (0):
  #if degcode == 'MN':
    degree.name = "Minor in Mathematics"
    degree.required_credits = 18

    minfund = dpr.Group("Calculus Sequence")
    minfund.add_requirement("Calculus I", CAL1, 1)
    minfund.add_requirement("Calculus II", CAL2, 1)
    minfund.add_requirement("Calculus III", ['MATH 2339'], 1)
    degree.add_group(minfund)

    minelec = dpr.Group("Three Advanced Electives")
    minelec.add_requirement("Elective", MID|ADV, 3)
    degree.add_group(minelec)
    return degree


  # Fundamentals for major
  fund = dpr.Group("Math Foundation")
  fund.add_requirement("Calculus I",     ['MATH 1337', 'MATH 1309'], 1)
  fund.add_requirement("Calculus II",    ['MATH 1338', 'MATH 1340'], 1)
  fund.add_requirement("Calculus III",   ['MATH 3302', 'MATH 2339'], 1)
  fund.add_requirement("Linear Algebra", ['MATH 3304', 'MATH 3353'], 1)
  fund.add_requirement("Intro to ODEs",  ['MATH 3313', 'MATH 2343'], 1)
  degree.add_group(fund)

  # Supplemental Courses
  supp = dpr.Group("Supplemental Courses")
  supp.add_requirement("Sci/Eng Statistics", STAT, 1, greedy=True)
  supp.add_requirement("Intro. Programming", CSE, minhours=3, greedy=True)

  if degcode == 'BA':
    degree.name = 'B.A. Mathematics:  Spec. %s ' % ('UNKNOWN -- SEE ME ASAP.' if (speccode == None or speccode == 'UNS' or speccode == 'ENG') else speccode)
    degree.required_credits = 36

  if degcode == 'BS':
    degree.name = 'B.S. Mathematics:  Spec. %s ' % ('UNKNOWN -- SEE ME ASAP.' if (speccode == None or speccode == 'UNS' or speccode == 'ENG') else speccode)
    degree.required_credits = 42
    supp.add_requirement("Science", SCI, minhours=6, greedy=True) 

  degree.add_group(supp)




  spec = dpr.Group("Specialization Electives")
  ENG4P = set([])

  if speccode == 'PM':
    spec.add_requirement("Intro. Proof", IPRF, 1)
    spec.add_requirement("Pure Math", PURE, minhours=9)

  if speccode == 'ANU' or speccode == None or speccode == 'UNS':
    spec.add_requirement("Intro. Sci. Comp.", ISCP, 1) 
    spec.add_requirement("App/Num. Math", APNU, 3)

  if speccode == 'ENG-ME':
    spec.add_requirement("Intro. Sci. Comp.", ISCP, 1) 
    spec.add_requirement("Two Math 4000+", ENG1, 2)
    spec.add_requirement("Two ME", MEG2, 2, greedy=True)
    
  if speccode == 'ENG-CEE':
    spec.add_requirement("Intro. Sci. Comp.", ISCP, 1) 
    spec.add_requirement("Two Math 4000+", ENG1, 2)
    spec.add_requirement("Two CEE", CEG2, 2, greedy=True)

  if speccode == 'ENG-EE':
    spec.add_requirement("Intro. Sci. Comp.", ISCP, 1) 
    spec.add_requirement("Two Math 4000+", ENG1, 2)
    spec.add_requirement("Two EE", EEG2, 2, greedy=True)

  if speccode == 'CSE':
    spec.add_requirement("Int. Sci. Comp.", ISCP, 1) 
    spec.add_requirement("Two Math 4000+",  APNU, 2) 
    spec.add_requirement("CSE 4381", ['CSE 4381'], 1)

  if speccode == 'OR':
    spec.add_requirement("Int. Sci. Comp.", ISCP, 1) 
    spec.add_requirement("Adv. Sci. Comp.", COMP, 1 )
    spec.add_requirement("Two EMIS", ORG2, 2, greedy=True)


  spec.add_verification( "ver: Two 4000+ (any)", ADV|ENG4P, 2)
  spec.add_verification( "ver: One 4000+ (MATH)", ADV, 1)
  degree.add_group(spec)


  # one advanced elective
  if speccode in set(['PM', 'ANU', 'CSE', 'OR']):
    elec = dpr.Group("Additional Elective(s)")
    elec.add_requirement("Extra Math 3000+", IPRF|ISCP|ADV, mincourses=1, greedy=True)
    degree.add_group(elec)

  #return
  return degree






def autodetect_eng_specialization(student, courselist):

  if student.speccode == 'ENG':
    depts = [a.dept for a in courselist if a.dept in ['ME', 'EE', 'CEE']]
    if len(depts) == 0: return

    maxdep = max(set(depts), key=depts.count)
    if maxdep == 'ME':  student.speccode = 'ENG-ME'
    if maxdep == 'EE':  student.speccode = 'ENG-EE'
    if maxdep == 'CEE':  student.speccode = 'ENG-CEE'








