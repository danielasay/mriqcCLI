# Thoughts for creating mriqc pipeline:

# 1) Ask the user which study they want to qc
# 2) Ask if they want it run on all subjects, only new, or a specific list
# 3) Confirm the study and the number of subjects that will be processed
# 4) Show progress bar
# 5) Built funtionality for running qc on all subjects from all studies

import os
from tkinter import *
import inquirer as inq
import time
import pandas as pd
import numpy as np
import csv
import subprocess


class mriqcCLI():
	def __init__(self):	
		pass


	def selectStudy(self, studyPaths):
		while True:
			try:
				studies = [
					inq.List('studies',
									message = "Which study would you like to qc?",
									choices = ['opioid', 'explosive sync', 'bacpac', 'bacpac best', 'mapp2', 'micapp', 'cpira2'],
								),
				]

				studiesAnswer = inq.prompt(studies)
				studyAnswer = studiesAnswer['studies']


				studyConfirmation = {
					inq.Confirm('studyConfirmation',
									message="You've selected the " + studyAnswer + " study. Is that correct?",
								),
				}

				confirmationAnswer = inq.prompt(studyConfirmation)

				if confirmationAnswer['studyConfirmation'] == True:
					print("Study Selection Confirmed.")
					time.sleep(.5)
				else:
					raise ValueError("You did not confirm your selection. Please try again.")
			except ValueError:
					print("You did not confirm your selection. Please try again.")
					time.sleep(1.5)
					continue

			if studyAnswer == "explosive sync":
				studyAnswer = "explosiveSync"
			elif studyAnswer == "BACPAC BEST":
				studyAnswer = "bacpacBest"	

			if mriqcCLI.validateBIDSDir(self, studyAnswer) == True:
				break
			else:
				print("The study you selected does not have a valid BIDS directory.\nSelect a different study or add a valid BIDS directory for " + studyAnswer + ".")
				time.sleep(1.5)
				continue
		BIDSDir = studyPaths[studyAnswer]

		return studyAnswer, BIDSDir


	def validateBIDSDir(self, study):
		if studyPaths[study] == "":
			return False
		else:
			return True

	def getSubs(self, BIDSDir):
		os.chdir(BIDSDir)
		subList = []
		for sub in os.listdir():
			if sub.startswith("sub-"):
				subList.append(sub)
		print("There are a total of " + str(len(subList)) + " subjects. Here is a list of them all:\n")
		print("")
		time.sleep(1.5)
		subList.sort()
		df = pd.DataFrame(subList, columns=['subject'])
		print(df)
		subjectConfirmation = {
			inq.Confirm('subjectConfirmation',
							message="Would you like to qc all " + str(len(subList)) + " subjects?",
						),
		}

		subjectAnswer = inq.prompt(subjectConfirmation)

		if subjectAnswer['subjectConfirmation'] == True:
			print("Subject Selection Confirmed.")
			return subList
			time.sleep(1)
		else:
			subset = mriqcCLI.subjectSubset(self, subList, BIDSDir)
			return subset

	def subjectSubset(self, subList, BIDSDir):
		print("Please select the subjects you would like to qc:\n")
		print("(this may take a minute if you're on a remote machine)\n")
		while True:
			try:
				# bring up GUI for user to select subjects
				mriqcCLI.subjectGUI(self, subList)

				# grab the subject sublist selected by the user
				os.chdir(BIDSDir)
				subs = []
				with open("subjectSubset.csv", "r") as subjects:
					read_file = csv.reader(subjects)
					for j in read_file:
						subs.append(j)
					subs = np.array(subs)      
					flatSubs = subs.flatten()
				subprocess.run(['rm', 'subjectSubset.csv'])

				# confirm with user that they selected the subs they wanted.
				df = pd.DataFrame(flatSubs, columns=['subject'])
				print("These are the subjects you've selected:")
				print(df)
				time.sleep(1)
				subsetConfirmation = {
					inq.Confirm('subsetConfirmation',
									message="Please confirm your selection. ",
								),
				}

				subsetAnswer = inq.prompt(subsetConfirmation)

				if subsetAnswer['subsetConfirmation'] == True:
					print("Subject Selection Confirmed.")
					time.sleep(.5)
				else:
					raise ValueError("You did not confirm your subject selection. Please try again.")
			except ValueError:
					print("You did not confirm your subject selection. Please try again.")
					time.sleep(1.5)
					continue


			return flatSubs
			

	def subjectGUI(self, subjectList):
		subjects = []
		window = Tk()
		w = 500
		h = 450

    	# get screen width and height
		ws = window.winfo_screenwidth() # width of the screen
		hs = window.winfo_screenheight() # height of the screen
    
    	# calculate x and y coordinates for the Tk root window
		x = (ws/2) - (w/2)
		y = (hs/2) - (h/2) - 150
    
    	# set the dimensions of the screen 
    	# and where it is placed
		window.geometry('%dx%d+%d+%d' % (w, h, x, y))
		window.title('Multiple selection')
  
    	# for scrolling vertically
		yscrollbar = Scrollbar(window)
		yscrollbar.pack(side = RIGHT, fill = Y)
      
		label = Label(window,
					text = "Select the subjects below :  ",
					font = ("Times New Roman", 18), 
					padx = 10, pady =10)
		label.pack()
		list = Listbox(window, selectmode = "multiple", 
						yscrollcommand = yscrollbar.set)
      
    	# Widget expands horizontally and 
    	# vertically by assigning both to
    	# fill option
		list.pack(padx = 10, pady = 10,
					expand = YES, fill = "both")
      
		for each_item in range(len(subjectList)):
			list.insert(END, subjectList[each_item])
			list.itemconfig(each_item, bg = "white")

		def saveSelected():
			subprocess.run(['touch', 'subjectSubset.csv'])
			subName = list.curselection()
			for i in subName:
				op = list.get(i)
				with open('subjectSubset.csv', mode='a+', newline='') as csv_file:
					writer = csv.writer(csv_file)
					sub = [op]
					writer.writerow(sub)
			print("Selection Saved!")

 	
		def quit():
			window.destroy()

      
    	# Attach listbox to vertical scrollbar
		yscrollbar.config(command = list.yview)
		Button(window, text="Save Selection", command=saveSelected).pack()
		Button(window, text="Close Window", command=quit).pack()
		window.mainloop()


	def runMriqc(self, subjects, BIDSDir):
		pass



studyPaths = {"opioid": "/PROJECTS/REHARRIS/opioid/opioid_BIDS", "explosiveSync": "", "bacpac": "", "bacpacBest": "", "mapp2": "/PROJECTS/MAPP/MAPP2/data/MAPP2_BIDS", "cpira2": ""}

qc = mriqcCLI()

selectedStudy, BIDSDir = qc.selectStudy(studyPaths)

subjects = qc.getSubs(BIDSDir)

print(subjects)


