# Thoughts for creating mriqc pipeline:

# 1) Ask the user which study they want to qc
# 2) Ask if they want it run on all subjects, only new, or a specific list
# 3) Confirm the study and the number of subjects that will be processed
# 4) Show progress bar
# 5) Built funtionality for running qc on all subjects from all studies

#import subprocess
#subprocess.run(['source', 'activate', 'dan_env'])
import os
from tkinter import *
import inquirer as inq
import sys
import time
import pandas as pd


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
					time.sleep(1)
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
			if sub.startswith("sub"):
				subList.append(sub)
		print("There are a total of " + str(len(subList)) + " subjects:")#Here is a list of them all:\n")
		print("")
		time.sleep(1)
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
			time.sleep(1)
		else:
			print("Please select the subjects you would like to qc:\n")
			print("(this may take a minute if you're on a remote machine)\n")
			#subList.sort()
			mriqcCLI.subjectGUI(self, subList)
			# get contents of txt file into array

	def subjectGUI(self, subjectList):
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
    
		def saveSelected():
			subjects = []
			subName = list.curselection()
			for i in subName:
				op = list.get(i)
				subjects.append(op)
			print("Selection Saved!")
			sys.stdout = open('subjectSubset.txt', 'w')
			print(subjects)
			sys.stdout.close()

    	
		def quit():
			window.destroy()
      
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
      
    	# Attach listbox to vertical scrollbar
		yscrollbar.config(command = list.yview)
		Button(window, text="Save Selection", command=saveSelected).pack()
		Button(window, text="Close Window", command=quit).pack()
		window.mainloop()



studyPaths = {"opioid": "/PROJECTS/REHARRIS/opioid/opioid_BIDS", "explosiveSync": "", "bacpac": "", "bacpacBest": "", "mapp2": "/PROJECTS/MAPP/MAPP2/data/MAPP2_BIDS", "cpira2": ""}

qc = mriqcCLI()

selectedStudy, BIDSDir = qc.selectStudy(studyPaths)

qc.getSubs(BIDSDir)





