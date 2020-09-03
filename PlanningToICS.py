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
* Description       : This script allows UTBM students to translate their unformatted planning (generated at the beginning of each semester and found on the university web portal) into an ICS file that can be imported on modern planning tools like Google Agenda, iCalendar, etc...).
*
|**********************************************************************;
'''

from ics import Calendar, Event
import re
import pandas as pd
from datetime import datetime, timedelta
from os import path

frStrings = {
'welcome' : "Bienvenue sur l'utilitaire UTBMPlanningToICS !\nCelui-ci te permet de convertir ton emploi du temps consultable à chaque début de semestre sur uPortal, en un agenda numérique au format standard ICS. En important ce dernier sur Google Agenda ou iCalendar (par exemple), tu pourras consulter tes horaires et salles de cours beaucoup plus facilement (sur ton PC, ton smartphone, etc...). Fini la corvée de la saisie de l'emploi du temps à chaque début de semestre !\nCommence par saisir le nom du fichier txt (avec l'extension .txt) dans lequel tu as copié-collé ton emploi du temps uPortal (lire le README.md maintenant si ce n'est pas déjà fait). Ce fichier doit se trouver dans le répertoire racine du projet !", 
'askfile' : "Nom du fichier ? : ",
'tooshort' :   "Erreur : le nom de fichier saisi est trop court",
'wrongextension' : "Erreur : le nom de fichier saisi ne porte pas l'extension .txt",
'notfound' : "Erreur : le fichier \"{}\" est introuvable",
'readsuccess' : "Fichier lu avec succes",
'errline' : "Erreur de format ligne {}",
'requestreview' : "Merci de vérifier le fichier et de recommencer",
'wrongheader' : "Erreur de format de l'entete du fichier",
'introaskgroup' : "Merci de saisir tes différents groupes pour les cours non-hebdomadaires (information à trouver dans le tableau des affectations recu en début de semestre, juste après les inscriptions pédagogiques)",
'askgroup'  : "Saisis ton groupe (A/B) pour le cours suivant : {}",
'errorAB' : "Groupe invalide, saisis A ou B : "
}

enStrings = {
'welcome' : "Welcome to the UTBMPlanningToICS utility! \nThis utility allows you to convert your schedule, which can be consulted at the start of each semester on uPortal, into a digital agenda in the standard ICS format. By importing it on Google Calendar or iCalendar (for example), you will be able to consult your scheduled classes and classrooms much more easily (on your PC, your smartphone, etc ...). No more drudgery of entering the schedule at the start of each semester!\nPlease start by typing the full filename (with .txt extension) in which you pasted your uPortal planning (see the README.md before continuing). This file must be placed in the same root folder as PlanningToICS.py !",
'askfile' : "Filename ? : ",
'tooshort' :   "Error : given filename is too short",
'wrongextension' : "Error : given filename does not have the extension .txt",
'notfound' : "Error : no file named \"{}\" inside current directory",
'readsuccess' : "File read with success",
'errline' : " - Formatting error on line {}",
'requestreview' : "Please review input file and retry",
'wrongheader' : "Error in file header (first line is not correctly formatted)",
'introaskgroup' : "Please enter your different groups for non-weekly classes (these informations can be found in the groups table that you get at the beginning of each semester after your UVs registrations)",
'askgroup' : "Enter your week group (A/B) for the following course : {}",
'errorAB' : "Invalid group, please enter A or B : "
}

daysOfWeekFR = ['lundi','mardi','mercredi','jeudi','vendredi','samedi']
daysOfWeekEN = ['monday','tuesday','wednesday','thursday','friday','saturday']

daysOfWeek = []

'''
e.name = "Test PythonToICS"
e.begin = start_date.strftime("%Y-%m-%d %H:%M:%S")
e.duration = Duration
e.description = "Ceci est la description de cet evenement test"

c.events.add(e)
'''

def checkFileExistence(filename):
    return path.exists(filename)

def validateFile(filename):
    if len(filename)<5:
        print(VerbList['tooshort'])
        return False
    if filename[-4:]!=".txt":
        print(VerbList['wrongextension'])
        return False
    if not checkFileExistence(filename):
        print(VerbList['notfound'].format(filename))
        return False
    return True

def askGroups(classes):
    Groups = []
    print(VerbList['introaskgroup'])
    for Class in classes:
        if Class[5]>1:
            group = input(" - "+VerbList['askgroup'].format(Class[0]+" ("+Class[1]+")"+" | "+daysOfWeek[Class[2]].capitalize()+" "+Class[3]+" -> "+Class[4])+" ("+Class[6]+") : ")
            while group!='A' and group!='B':
                group = input(VerbList['errorAB'])
            Groups.append([classes.index(Class),group])
    return Groups

def padTimeWithZeros(timeString):
    DPPos = timeString.index(':')
    b = timeString[0:DPPos]
    if int(b)<10 and timeString[0]!='0':
        timeString='0'+timeString
    return timeString

def ReadTxt(filename):
    regex_dict = {
    'firstline' : '^UV\s*Groupe\s*Jour\s*Début\s*Fin\s*Fréquence\s*Salle\(s\)\s*$',
    'middleline' : '^\s*[A-Z0-9]{4}\s+([A-Z]\s+){0,1}(CM|TD|TP)\s[0-9]{1,2}\s+(lundi|mardi|mercredi|jeudi|vendredi|samedi)\s+([0-9]{1,2}:[0-9]{1,2}\s+){2}[1-2]\s+[A-Z]\s[0-9a-z]{3,4}\s*$'
    }
    regex = {} #dict containing compiled regexs
    for key in regex_dict:
        regex[key] = re.compile(regex_dict[key])
    with open(filename,'r') as textfile:
        raw_lines = []
        for line in textfile:
            raw_lines.append(line.replace('\t',' ').replace('\n',''))
        textfile.close()
    matchs = 0
    if regex['firstline'].match(raw_lines[0]):
        matchs=1
    else:
        print(VerbList['wrongheader'])
    for line in raw_lines[1:]:
        if regex['middleline'].match(line):
            matchs+=1
        else:
            print(VerbList['errline'].format(raw_lines.index(line)))
    if matchs != len(raw_lines):
        print(VerbList['requestreview'])
        print("Nombre de matchs : ",matchs)
        return False
    print(VerbList['readsuccess'])
    
    Classes = []
    for line in raw_lines[1:]:
        newClass = line.replace('\t','').split(' ')
        newClass = [value for value in newClass if value!='']
        if not newClass[1] in ['CM','TD','TP']:
            newClass.pop(1)
        newClass.pop(2)
        newClass[6] = newClass[6]+newClass[7]
        newClass.pop(7)
        newClass[2]=daysOfWeekFR.index(newClass[2])
        newClass[5]=int(newClass[5])
        Classes.append(newClass)
    return Classes

if __name__ == "__main__":
    print("**** UTBM PlanningToICS Script ****\nAuthor:\n")
    print("| | | |/ _/ | || |  V  | \n| |_| | \_| | \/ | \_/ | \n|___|_|\__/_|\__/|_| |_| \n\
    ")
    print("Version 1.0")
    SelectedLang = input("Choose your language - Selectionne ta langue :\n-FR\n-EN\n : ")
    SelectedLang = SelectedLang.lower()
    while(SelectedLang != "fr" and SelectedLang != "en"):
        SelectedLang = input("Oops ! Please type \"EN\" or \"FR\" and press ENTER - Merci de saisir \"EN\" ou \"FR\" et d'appuyer sur ENTREE : ")
        SelectedLang = SelectedLang.lower()
    if SelectedLang=="fr":
        VerbList = frStrings
        daysOfWeek = daysOfWeekFR
    elif SelectedLang=="en":
        VerbList = enStrings
        daysOfWeek = daysOfWeekEN

    print(VerbList['welcome'])
    filename = input(VerbList['askfile'])
    while not validateFile(filename):
        filename = input(VerbList['askfile'])
        
    Classes = ReadTxt(filename)

    if not Classes:
        exit(0)

    #Groups = askGroups(Classes)
    
    c = Calendar()

    GlobalStartDate = datetime(2020,9,14,8,0,0)

    dateFormat = "%Y-%m-%d %H:%M:%S"

    for Class in Classes:
        e = Event()
        startDate = GlobalStartDate+timedelta(Class[2])
        startDate = startDate.replace(hour = int(Class[3][:Class[3].index(':')]))
        startDate = startDate.replace(minute = int(Class[3][Class[3].index(':')+1:]))
        endDate = startDate.replace(hour = int(Class[4][:Class[4].index(':')]))
        endDate = endDate.replace(minute = int(Class[4][Class[4].index(':')+1:]))
        e.begin = startDate.strftime(dateFormat)
        e.end = endDate.strftime(dateFormat)
        e.location = Class[6]
        e.name = Class[0]+" ("+Class[1]+")"
        c.events.add(e)
    
    with open("test.ics", 'w') as ICSFIle:
        ICSFIle.writelines(c)
    print("DONE")


'''
c = Calendar()
e = Event()
'''


    
'''
start_date = datetime.now()+timedelta(hours=1)
Duration = timedelta(hours=1,minutes=30)

e.name = "Test PythonToICS"
e.begin = start_date.strftime("%Y-%m-%d %H:%M:%S")

e.duration = Duration
e.location = "P245"
e.description = "Ceci est la description de cet evenement test"

c.events.add(e)
'''
""" 
with open("test.ics", 'w') as ICSFIle:
    ICSFIle.writelines(c)
print("DONE")
 """