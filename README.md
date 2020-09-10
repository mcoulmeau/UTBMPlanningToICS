# UTBMPlanningToICS script #

## Author ##
Valentin Mercy - Licium

## Script description ##
UTBMPlanningToICS aims to simplify classes planning comprehension for UTBM students (UTBM = University of Technology of Belfort-Montbeliard). More precisely, this python script allows all UTBM students to turn the unformatted list of courses (which can be found on [their personnal space](https://monespace.utbm.fr/)) into a proper ICS file they can directly import on their favourite scheduling utility, such as Google Agenda for example.

## Supported languages ##
* English
* French

## How to use it ##
* First, open a bash terminal, clone this repository and make it become your working directory :
```
git clone https://github.com/Valentin68/UTBMPlanningToICS.git
cd UTBMPlanningToICS/
```
* Go to your [UTBM personnal space](https://monespace.utbm.fr/), navigate to "Mon dossier étudiant" > "Emploi du temps" and copy (Ctrl-C) your list of classes **with the header**. Please ensure that your selection starts just before the word "UV" and ends just after the location of the very last class.
* Paste it into a new .txt file. That file must finally contain something like this :
```
UV 		Groupe 	Jour 	Début 	Fin 	Fréquence 	Salle(s)
LO21 		TD 1 	lundi 	8:00 	10:00 	1 	P 130
LC00 		TD 1 	lundi 	14:00 	16:00 	1 	P 122
IFD1 		CM 1 	lundi 	16:15 	18:15 	1 	T 305
PS22 		TD 2 	mardi 	8:00 	10:00 	1 	P 243
MDA1 	A 	TD 1 	mardi 	14:00 	16:00 	1 	P 323
MTC7 		TD 2 	mardi 	16:15 	18:15 	1 	P 325
MDA1 	A 	CM 1 	mercredi 	8:30 	10:00 	1 	P 108b
LO21 		CM 1 	mercredi 	14:00 	16:00 	1 	T 306
LO21 		TP 2 	mercredi 	16:15 	19:15 	2 	P 334
MTC7 		TD 2 	jeudi 	8:00 	10:00 	1 	P 122
PS22 		CM 1 	jeudi 	10:15 	12:15 	1 	P 108b
PS22 		TP 2 	vendredi 	8:00 	10:00 	2 	P 226
IFD1 		CM 1 	vendredi 	10:15 	12:15 	1 	T 305
MTC7 		CM 1 	vendredi 	14:00 	16:00 	1 	P 243
LC00 		TP 4 	vendredi 	16:15 	17:15 	1 	P 145
```
* Save this file into the working directory, that should also contain the main script ```PlanningToICS.py``` and the list of A/B weeks for the next semester : ```SEM_A20.csv``` for example.
* Launch the main script :
```
python3 PlanningToICS.py
```
* Follow the instructions
* You should now have a new file named ```output.ics``` in your working directory. You can directly import it in your Google Agenda for example, and enjoy the result !

## How to contribute ##
Feel free to contribute to this project ! Here are some possible improvments :
* Create a GUI
* Turn it into a standalone utility, maybe a portable .exe for Windows users
* Use ICS RRULES for repeating events to link them together
* Detect overlapping classes, then warn and ask users which ones they want to keep
* Each semester, as the UTBM administration gives us the semester calendar, feel free to turn it into a SEM_XXX.csv file that can be read by this script. Please respect the following structure (only working periods must be listed) :
```
START;END;TYPE
14/09/20;21/09/20;A
21/09/20;28/09/20;B
28/09/20;05/10/20;A
05/10/20;12/10/20;B
12/10/20;19/10/20;A
19/10/20;26/10/20;B
02/11/20;09/11/20;A
09/11/20;16/11/20;B
16/11/20;17/11/20;A
18/11/20;18/11/20;B
19/11/20;22/11/20;A
23/11/20;29/11/20;B
29/11/20;06/12/20;A
07/12/20;14/12/20;B
14/12/20;20/12/20;A
04/01/21;06/01/21;B
07/01/21;07/01/21;A
08/01/21;08/01/21;B
```
As this file is the same for all UTBM students, feel free to push it to this repository so that others can benefit from it.