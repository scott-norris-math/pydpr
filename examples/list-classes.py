import sys
import pydpr.pydpr as dpr

# basic setup info
studentfile = './records/current-mathmajors.xlsx'
coursesfile = './records/current-coursehistories.xlsx'

# identify the student
fragment = sys.argv[1]
studentID = dpr.find_student(studentfile, fragment)


sortkey = 'term'
try:
  sortkey = sys.argv[2]
except:
  pass


if sortkey == 'term':  sortfunc = lambda course: course.term
if sortkey == 'code':  sortfunc = lambda course: course.code


tca = 0
tcp = 0
tgp = 0

courselist = dpr.load_courses_from_query(coursesfile, studentID)
courselist.sort(key=sortfunc)
for cc in courselist:
  if cc.credits == 0: 
    continue

  print("{0:4} {1:4} --> {2:16} --> {3:4} {4:4}".format(cc.dept, cc.number, dpr.termcode_to_text(cc.term), cc.credits, cc.grade))

  credits = cc.credits
  gpoints = dpr.get_gradepoints(cc.grade)
  if (gpoints != None):
    tca += int(credits)
    tgp += float(gpoints)*float(credits)
    tcp += (int(credits) if gpoints > 0 else 0)
  



print("--------------------------------------------")
print("                                   %4d %2.2f" % (tcp, float(tgp)/float(tca) )  )




print('\n')


