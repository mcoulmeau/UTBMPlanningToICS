import re

regex_dict = {
    'firstline': '^UV\s*Groupe\s*Jour\s*Début\s*Fin\s*Fréquence\s*Salle\(s\)\s*$',
    'middleline': '^\s*[A-Z0-9]{4}\s+([A-Z]\s+){0,1}(CM|TD|TP)\s[0-9]{1,2}\s+(lundi|mardi|mercredi|jeudi|vendredi|samedi)\s+([0-9]{1,2}:[0-9]{1,2}\s+){2}[1-2]\s+[A-Z]\s[0-9a-z]{3,4}\s*$',
    'semesterFile': '^SEM_(A|P)[0-9]{2}.csv$',
    'ICSDatetime' : "^(DTSTART|DTEND):[0-9]{8}T[0-9]{6}Z$"
}

regex = {}  # dict containing compiled regexs
NbEventsCreated = 0
OutputFileName = "output.ics"

for key in regex_dict:
    regex[key] = re.compile(regex_dict[key])

def LocalizeICSTimes(filename): #deletes all Z characters in UTC timestamps inside ICS file, replacing all UTC-based times by local ones
    try:
        with open(filename,'r') as ICSFile:
            data = ICSFile.readlines()
        ICSFile.close()
    except EnvironmentError:
        return False
    print(data)
    newData = []
    for line in data:
        if(regex['ICSDatetime'].match(line)):
            newData.append(line.replace('00Z','00'))
        else:
            newData.append(line)
    print(newData)
    try:
        with open(filename,'w') as ICSFile:
            ICSFile.writelines(newData)
        ICSFile.close()
    except EnvironmentError:
        return False
    return True

LocalizeICSTimes(OutputFileName)