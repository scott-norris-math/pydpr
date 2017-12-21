import sys
from colorama import init, Fore, Back, Style
init()

# for reading XLSX files
from openpyxl import load_workbook

# files with student and course histories
gradsfile   = './records/graduating-mathmajors.xlsx'
studentfile = './records/current-mathmajors.xlsx'
coursesfile = './records/current-coursehistories.xlsx'

fragment = sys.argv[1]
counter = 1
matches = []

wb = load_workbook(studentfile)
ws = wb[wb.get_sheet_names()[0]]
for jj,row in enumerate(ws):
  ID    = str(row[0].value)
  lname = str(row[2].value)
  fname = str(row[3].value)
  email = str(row[4].value)

  found = False
  fields = [lname, fname, email]
  for kk,ff in enumerate(fields):
    pos = ff.lower().find(fragment)
    if pos > -1:
      fields[kk] = ff[0:pos]+Fore.GREEN+ff[pos:pos+len(fragment)]+Style.RESET_ALL+ff[pos+len(fragment):]
      found = True

  if found:
    print('(%1d) [%s] "%s, %s" <%s>' % (counter, ID, fields[0], fields[1], fields[2]))
    matches.append(row)
    counter += 1



val = int(input("\nSelect a student: "))
if val > 0 and val <= len(matches):  
  ID = matches[val-1][0].value


else:
  print ("invalid entry.  exiting.")

