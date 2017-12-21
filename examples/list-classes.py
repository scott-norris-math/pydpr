import sys
import pydpr.pydpr as dpr

studentfile = './records/current-mathmajors.xlsx'
coursesfile = './records/current-coursehistories.xlsx'

studentID = sys.argv[1]

dfilter   = False
if len(sys.argv) > 2:
  dfilter = True
  dept = sys.argv[2]

courselist = dpr.load_courses_from_query(coursesfile, studentID)
courselist.sort(key=lambda course: course.term)
for cc in courselist:
  if cc.credits == 0: 
    continue
  if dfilter == True and cc.dept != dept:
    continue

  print("{0:4} {1:4} --> {2:16} --> {3:16}".format(cc.dept, cc.number, dpr.termcode_to_text(cc.term), cc.grade))

print('\n')


