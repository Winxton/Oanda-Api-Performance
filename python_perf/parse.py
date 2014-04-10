import csv

"""
with open('streamresults/resultfile.csv', 'w') as resultfile:
    reportwriter = csv.writer(resultfile, delimiter = ',', quotechar = '|', quoting = csv.QUOTE_MINIMAL)
"""

stuff = {}

with open('streamresults/bothticks2.csv', 'r') as csvfile:
    reader = csv.reader(csvfile)
    
    for line_list in reader:
        #print line_list[0]
        stuff[line_list[0]] = [line_list[0], line_list[1], line_list[2], line_list[3]]
        #print line_list[0], stuff[line_list[0]]

    #print stuff.has_key('1396637904.212')

open('streamresults/resultfile2.csv', 'w').close()
with open('streamresults/resultfile2.csv', 'a') as resultfile:
    reportwriter = csv.writer(resultfile, delimiter = ',', quotechar = '|', quoting = csv.QUOTE_MINIMAL)

    with open('streamresults/bothticks2.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        
        for line_list in reader:
            #print line_list[5], type(line_list[5])

            if stuff.has_key(line_list[5]):

                #print stuff[line_list[5]]
                stuff[line_list[5]].extend( [line_list[6],line_list[7],line_list[8]] )
            
                reportwriter.writerow(stuff[line_list[5]])

            #if line_list[0] != line_list[5]:

