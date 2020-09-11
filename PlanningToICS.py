'''
| | | |/ _/ | || |  V  | 
| |_| | \_| | \/ | \_/ | 
|___|_|\__/_|\__/|_| |_| 

|**********************************************************************;
* Project           : UTBMPlanningToICS Tool
*
* Program name      : UTBMPlanningToICS
*
* Author            : licium (Valentin Mercy)
*
* Date created      : 20200109
*
* Purpose           : Creates an ICS file from UTBM's planning system output. UTBM = University of Technology of Belfort-Montbeliard.
*
* Description       : This script allows UTBM students to translate their unformatted planning (generated at the beginning of each semester and found on the university web portal) into an ICS file that can be imported on modern planning tools like Google Agenda, Apple iCalendar, etc...).
*
|**********************************************************************;
'''

from ics import Calendar, Event
import re
from datetime import datetime, timedelta
import codecs
from os import path, listdir
import csv

frStrings = {
    'welcome': "Bienvenue sur l'utilitaire UTBMPlanningToICS !\nCelui-ci te permet de convertir ton emploi du temps consultable à chaque début de semestre sur l'espace etudiant, en un agenda numérique au format standard ICS. En important ce dernier sur Google Agenda ou iCalendar (par exemple), tu pourras consulter tes horaires et salles de cours beaucoup plus facilement (sur ton PC, ton smartphone, etc...). Finie la corvée de la saisie de l'emploi du temps à chaque début de semestre !\nCommence par saisir le nom du fichier txt (avec l'extension .txt) dans lequel tu as copié-collé ton emploi du temps personnel (lire le README.md maintenant si ce n'est pas déjà fait). Ce fichier doit se trouver dans le répertoire racine du projet !",
    'askfile': "Nom du fichier ? : ",
    'tooshort':   "Erreur : le nom de fichier saisi est trop court",
    'wrongextension': "Erreur : le nom de fichier saisi ne porte pas l'extension .txt",
    'notfound': "Erreur : le fichier \"{}\" est introuvable",
    'readsuccess': "Fichier lu avec succes",
    'errline': "Erreur de format ligne {}",
    'requestreview': "Merci de vérifier le fichier et de recommencer",
    'wrongheader': "Erreur de format de l'entete du fichier",
    'introaskgroup': "Merci de saisir tes différents groupes pour les cours non-hebdomadaires (information à trouver dans le tableau des affectations recu en début de semestre, juste après les inscriptions pédagogiques)",
    'askgroup': "Saisis ton groupe (A/B) pour le cours suivant : {}",
    'errorAB': "Groupe invalide, saisis A ou B : ",
    'noSemesterFile': "Erreur : aucun calendrier semestriel n'a été trouvé dans le répertoire courant. Il est toutefois possible d'en créer un en suivant le modèle donnée dans le README. Merci de recommencer une fois le fichier créé.",
    'severalSemCals': "Plusieurs calendriers semestriels ont été trouvés : {}. Merci de sélectionner celui à considérer en saisissant le code correspondant (A20 par exemple) : ",
    'wrongCode': "La saisie ne correspond pas à un code de semestre. Recommence : ",
    'errorPeriods' : "Erreur dans le calendrier du semestre : au moins une période est invalide (dates incohérentes ou début>fin) ou porte un type erroné (différent de A/B)",
    'overlappingPeriods' : "Erreur dans le calendrier du semestre : les deux périodes suivantes se chevauchent : {} et {}",
    'success' : "Opération terminée ({} événements créés en tout) ! Tu peux maintenant récupérer le fichier output.ics créé dans le répertoire courant, et l'importer sur Google Agenda (ou équivalent).",
    'errorWritingICS' : "Une erreur s'est produite lors de la finalisation du fichier ICS ({})",
}

enStrings = {
    'welcome': "Welcome to the UTBMPlanningToICS utility! \nThis utility allows you to convert your schedule, which can be consulted at the start of each semester on your personnal space, into a digital agenda in the standard ICS format. By importing it on Google Calendar or iCalendar (for example), you will be able to consult your scheduled classes and classrooms much more easily (on your PC, your smartphone, etc ...). No more time loss of manually entering the schedule at the start of each semester!\nPlease start by typing the full filename (with .txt extension) in which you pasted your personnal planning (see the README.md before continuing). This file must be placed in the same root folder as PlanningToICS.py !",
    'askfile': "Filename ? : ",
    'tooshort':   "Error : given filename is too short",
    'wrongextension': "Error : given filename does not have the extension .txt",
    'notfound': "Error : no file named \"{}\" inside current directory",
    'readsuccess': "File read with success",
    'errline': " - Formatting error on line {}",
    'requestreview': "Please review input file and retry",
    'wrongheader': "Error in file header (first line is not correctly formatted)",
    'introaskgroup': "Please enter your different groups for non-weekly classes (these informations can be found in the groups table that you get at the beginning of each semester after your UVs registrations)",
    'askgroup': "Enter your week group (A/B) for the following course : {}",
    'errorAB': "Invalid group, please enter A or B : ",
    'noSemesterFile': "Error : no semester calendar was found. Please consider creating it by following the structure given in README file, and try again.",
    'severalSemCals': "Several semester calendars were found : {}. Please select the one to consider by entering the corresponding code (A20 for example) : ",
    'wrongCode': "Given string does not match a semester code. Please try again : ",
    'errorPeriods' : "Error in semester calendar : at least one period is erroneous (start>end) or has an invalid type (different from A/B)",
    'overlappingPeriods' : "Error in semester calendar : following periods are overlapping : {} and {}.",
    'success' : "Operation successfully completed ({} events have been created) ! You can now find the output.ics file into the working directory, and upload it on Google Agenda (or an equivalent software).",
    'errorWritingICS' : "An error occured while rendering ICS file : ({})",
}

daysOfWeekFR = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi']
daysOfWeekEN = ['monday', 'tuesday', 'wednesday',
                'thursday', 'friday', 'saturday']

daysOfWeek = []

regex_dict = {
    'firstline': '^UV\s*Groupe\s*Jour\s*Début\s*Fin\s*Fréquence\s*Mode d\'enseignement\s*Salle\(s\)\s*$',
    'middleline': '^\s*[A-Z0-9]{4}\s+([A-Z]\s+){0,1}(CM|TD|TP)\s[0-9]{1,2}\s+(lundi|mardi|mercredi|jeudi|vendredi|samedi)\s+([0-9]{1,2}:[0-9]{1,2}\s+){2}[1-2]\s\s+(Distanciel|Présentiel)\s+([A-Z]\s[0-9a-z]{3,4})?\s*$',
    'semesterFile': '^SEM_(A|P)[0-9]{2}.csv$',
    'ICSDatetime' : "^(DTSTART|DTEND):[0-9]{8}T[0-9]{6}Z$"
}

regex = {}  # dict containing compiled regexs
NbEventsCreated = 0
OutputFileName = "output.ics"

for key in regex_dict:
    regex[key] = re.compile(regex_dict[key])

def checkFileExistence(filename):
    return path.exists(filename)

def validateFile(filename):
    if len(filename) < 5:
        print(VerbList['tooshort'])
        return False
    if filename[-4:] != ".txt":
        print(VerbList['wrongextension'])
        return False
    if not checkFileExistence(filename):
        print(VerbList['notfound'].format(filename))
        return False
    return True

def askGroups(classes):
    Groups = []
    for Class in classes:
        if Class[5] > 1:
            print(VerbList['introaskgroup'])
            break
    for Class in classes:
        if Class[5] > 1:
            group = input(" - "+VerbList['askgroup'].format(Class[0]+" ("+Class[1]+")"+" | " +
                                                            daysOfWeek[Class[2]].capitalize()+" "+Class[3]+" -> "+Class[4])+" ("+Class[6]+") : ")
            while group != 'A' and group != 'B':
                group = input(VerbList['errorAB'])
            Groups.append([classes.index(Class), group])
    return Groups

def padTimeWithZeros(timeString):
    DPPos = timeString.index(':')
    b = timeString[0:DPPos]
    if int(b) < 10 and timeString[0] != '0':
        timeString = '0'+timeString
    return timeString

def ReadTxt(filename):
    with codecs.open(filename, 'r', encoding='utf-8') as textfile:
        raw_lines = []
        for line in textfile:
            raw_lines.append(line.replace('\t', ' ').replace('\n', ''))
        textfile.close()
    matchs = 0
    if regex['firstline'].match(raw_lines[0]):
        matchs = 1
    else:
        print(VerbList['wrongheader'])
    for line in raw_lines[1:]:
        if regex['middleline'].match(line):
            matchs += 1
        else:
            print(VerbList['errline'].format(raw_lines.index(line)))
    if matchs != len(raw_lines):
        print(VerbList['requestreview'])
        print("Nombre de matchs : ", matchs)
        return False
    print(VerbList['readsuccess'])

    Classes = [] #each element must be a subarray in the form [UV_code, type of class, day of week index, start_time, end_time, frequency, room]. room can be "Distanciel" if class is given remotely.

    for line in raw_lines[1:]:
        newClass = line.replace('\t', '').split(' ')
        newClass = [value for value in newClass if value != '']
        if not newClass[1] in ['CM', 'TD', 'TP']:
            newClass.pop(1)
        newClass.pop(2)
        newClass[2] = daysOfWeekFR.index(newClass[2])
        newClass[5] = int(newClass[5])
        if newClass[6] == "Distanciel":
            if len(newClass)==7: #no room provided
                newClass[6]="Distanciel"
            else:
                newClass[6]="Distanciel ("+''.join(newClass[7:])+")"
        else:
            newClass[6] = newClass[7]+newClass[8]
        newClass = newClass[:7]
        Classes.append(newClass)
    return Classes

def findSemesterFile():
    Candidates = [f for f in listdir('.') if path.isfile(f)]
    finalCands = []
    for cand in Candidates:
        if regex['semesterFile'].match(cand):
            finalCands.append(cand)
    if not finalCands:
        print(VerbList['noSemesterFile'])
        return False
    if len(finalCands) == 1:
        return finalCands[0]
    finalCands2 = []
    for cand in finalCands:
        finalCands2.append(cand[cand.index('_')+1:cand.index('.')])
    select = input(VerbList['severalSemCals'].format(finalCands))
    while not select in finalCands:
        select = input(VerbList['wrongCode'])
    return "SEM_"+select+".csv"


def CheckSemester(filename):  # returns calendar min and max if
    periods = []
    with open(filename, 'r') as SemCal:
        reader = csv.DictReader(SemCal, delimiter=';')
        for row in reader:
            try:
                startDTT = datetime.strptime(row['START'], '%d/%m/%y')
                endDT = datetime.strptime(row['END'], '%d/%m/%y')
            except ValueError:
                return False
            if startDTT > endDT or row['TYPE'] not in ['A', 'B']:
                return False
            periods.append([startDTT, endDT, row['TYPE']])
    return periods

def overlappingTwoPeriods(start_a, end_a, start_b, end_b):
    return start_a<=start_b and start_b<=end_a or start_b<=start_a and start_a<=end_b

def overlappingPeriods(per):
    for period in per:
        for period2 in per[per.index(period)+1:]:
            if overlappingTwoPeriods(period[0],period[1],period2[0],period2[1]):
                return [period,period2]
    return False

def getGroupOfClass(groups, class_index):
    for group in groups:
        if group[0]==class_index:
            return group[1]
    return False

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

def CreateCalendar(groups, Classes, periods):
    global NbEventsCreated
    cal = Calendar()
    dateFormat = "%Y-%m-%d %H:%M:%S"
    for period in periods:
        FirstWeekDay = period[0].weekday()
        LastWeekDay = period[1].weekday()
        for i in range(FirstWeekDay,LastWeekDay+1):
            for Class in Classes:
                if Class[2]==i:
                    if Class[5]==1 or getGroupOfClass(groups,Classes.index(Class))==period[2]: #if frequency is 1 (class occuring each week) or if group matches period
                        e = Event()
                        startDT = period[0]+timedelta(Class[2]-period[0].weekday())
                        startDT = startDT.replace(hour=int(Class[3][:Class[3].index(':')]))
                        startDT = startDT.replace(
                            minute=int(Class[3][Class[3].index(':')+1:]))
                        endDT = startDT.replace(hour=int(Class[4][:Class[4].index(':')]))
                        endDT = endDT.replace(minute=int(Class[4][Class[4].index(':')+1:]))
                        e.begin = startDT.strftime(dateFormat)
                        e.end = endDT.strftime(dateFormat)
                        e.location = Class[6]
                        e.name = Class[0]+" ("+Class[1]+")"
                        cal.events.add(e)
                        NbEventsCreated+=1          
    return cal

def LocalizeICSTimes(filename): #deletes all Z characters in UTC timestamps inside ICS file, replacing all UTC-based times by local ones
    try:
        with open(filename,'r') as ICSFile:
            data = ICSFile.readlines()
    except EnvironmentError:
        return False
    newData = []
    for line in data:
        if(regex['ICSDatetime'].match(line)):
            newData.append(line.replace('00Z','00'))
        else:
            newData.append(line)
    try:
        with open(filename,'w') as ICSFile:
            ICSFile.writelines(newData)
    except EnvironmentError:
        return False
    return True

def CheckICS(filename):
    startOfEvents = 0
    endOfEvents = 0
    try:
        with open(filename,'r') as ICSFile:
            data = ICSFile.readlines()
            for line in data:
                if "BEGIN:VEVENT" in line:
                    startOfEvents+=1
                elif "END:VEVENT" in line:
                    endOfEvents+=1
    except EnvironmentError:
        print(VerbList['errorWritingICS'].format("cannot check ICS file integrity" if SelectedLang=='EN' else "impossible de vérifier l'intégrité du fichier ICS"))
        exit(0)
    if startOfEvents==endOfEvents:
        return startOfEvents-NbEventsCreated
    print(VerbList['errorWritingICS'].format("cannot check ICS file integrity" if SelectedLang=='EN' else "impossible de vérifier l'intégrité du fichier ICS"))
    exit(0)

if __name__ == "__main__":
    print("**** UTBM PlanningToICS Script ****\nAuthor: Licium\n")
    print("Version 1.0")
    SelectedLang = input("Choose your language - Selectionne ta langue :\n-FR\n-EN\n : ")
    SelectedLang = SelectedLang.lower()
    while(SelectedLang != "fr" and SelectedLang != "en"):
        SelectedLang = input(
            "Oops ! Please type \"EN\" or \"FR\" and press ENTER - Merci de saisir \"EN\" ou \"FR\" et d'appuyer sur ENTREE : ")
        SelectedLang = SelectedLang.lower()
    if SelectedLang == "fr":
        VerbList = frStrings
        daysOfWeek = daysOfWeekFR
    elif SelectedLang == "en":
        VerbList = enStrings
        daysOfWeek = daysOfWeekEN

    print(VerbList['welcome'])
    filename = input(VerbList['askfile'])
    while not validateFile(filename):
        filename = input(VerbList['askfile'])

    Classes = ReadTxt(filename)

    if not Classes:
        exit(0)

    SemFile = findSemesterFile()
    if not SemFile:
        exit(0)
    periods = CheckSemester(SemFile)
    if not periods:
        print(VerbList['errorPeriods'])
        exit(0)
    overlap = overlappingPeriods(periods)
    if overlap:
        print(VerbList['overlappingPeriods'].format(overlap[0][0].strftime("%d/%m/%Y")+" -> "+overlap[0][1].strftime("%d/%m/%Y"),overlap[1][0].strftime("%d/%m/%Y")+" -> "+overlap[1][1].strftime("%d/%m/%Y")))
        exit(0)

    Groups = askGroups(Classes)

    FinalCalendar = CreateCalendar(Groups, Classes, periods)

    try:
        with open(OutputFileName, 'w') as ICSFile:
            ICSFile.writelines(FinalCalendar)
    except EnvironmentError:
        print(VerbList['errorWritingICS'].format("writing permission denied" if SelectedLang=='EN' else "permission d'écriture refusée"))
        exit(0)
    EventsDelta = CheckICS(OutputFileName)
    if EventsDelta:
        if SelectedLang == 'en':
            print(VerbList['errorWritingICS'].format(str(abs(EventsDelta))+(" missing" if EventsDelta<0 else "extra")+" event"+("s" if abs(EventsDelta)!=1 else "")))
        elif SelectedLang == 'fr':
            print(VerbList['errorWritingICS'].format(str(abs(EventsDelta))+" événements "+("s" if abs(EventsDelta)!=1 else "")+("manquants" if EventsDelta<0 else "en trop")))
        exit(0)
    if not LocalizeICSTimes(OutputFileName):
        print(VerbList['errorWritingICS'].format("reading permission denied" if SelectedLang=='EN' else "permission de lecture refusée"))
        exit(0)

    print(VerbList['success'].format(NbEventsCreated))
