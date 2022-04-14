# Created by: Daniel Asay on March 28th 
# Last edit: April 11th

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
import shutil
from tqdm import tqdm
from yaspin import yaspin


class mriqcCLI():
	def __init__(self):	
		pass

	# this method will provide the user with a list of studies and ask which one they would like to qc. (limit to one selection for now)
	# if the study doesn't have a valid BIDS directory with data, they will be asked to select a different study.

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

		return BIDSDir


	# this method confirms (or not) that there's a valid BIDS dir in the studyPaths dictionary for the study selected by the user. 

	def validateBIDSDir(self, study):
		if studyPaths[study] == "":
			return False
		else:
			return True

	# the user will be shown a list of all the available subjects in the BIDS directory of their chosen study. Then they'll be asked to 
	# choose whether they'd like to qc all the subjects, or just a subset. If they just want a subset, a gui will pop up and they will be prompted
	# to select the subjects they want to run.

	def getSubs(self, BIDSDir):
		os.chdir(BIDSDir)
		subList = []
		for sub in os.listdir():
			if sub.startswith("sub-"):
				subList.append(sub)
		print("There are a total of " + str(len(subList)) + " subjects. Here is a list of them all:\n")
		print("")
		time.sleep(1.25)
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

	# this method will be triggered when the user does not want to qc each available subject. It will bring up a gui for them to choose subjects
	# and ask them to confirm the subject list they've selected.

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
			# place subject list into 'regular' (non-numpy) array
			s = []
			for i in flatSubs:
				s.append(i)
			return s
			

	# method that includes all of the specifications and sub-functions for the gui. The user will see a list of subjects for the chosen study and be able to 
	# select all the subjects they would like to qc.

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

		# button/function that will save the the list of subjects that the user selected to a csv file called subjectSubset.csv
		# this is a temporary file and will be deleted during processing.

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

 		# button/function that will close the gui.

		def quit():
			window.destroy()

      
    	# Attach listbox to vertical scrollbar
		yscrollbar.config(command = list.yview)
		Button(window, text="Save Selection", command=saveSelected).pack()
		Button(window, text="Close Window", command=quit).pack()
		window.mainloop()


	# this method is the core of the program and will run mriqc on each subject that the user specified, unless qc data already exists for the subject.
	# if qc data exists, the user will be asked if they would like to override it

	def runMriqc(self, subjects, BIDSDir):
		os.chdir(BIDSDir)
		if not os.path.isdir("mriqc"):
			os.makedirs("mriqc")
		mriqcDir = BIDSDir + "/mriqc"
		os.chdir(mriqcDir)
		for i in tqdm(range(len(subjects))):
			if mriqcCLI.checkForData(subjects[i]):
				startTime = time.time()
				with yaspin(text="Processing subject..."):
					time.sleep(1)
					mriqc = f"""
						docker run -it --rm -v {BIDSDir}:/data:ro \
						-v {BIDSDir}/mriqc:/out \
						poldracklab/mriqc:latest /data /out participant --participant_label {subjects[i][4:]} --no-sub
					"""
					proc1 = subprocess.Popen(mriqc, shell=True, stdout=subprocess.PIPE)
					proc1.wait()
					totalTime = round((time.time() - StartTime) / 60)
					print("It took " + str(totalTime) + " minutes to process " + sub)
					#mriqcCLI.cleanDir(sub, mriqcDir)
			else:
				continue


	# method will check if MRIQC output data already exists for a given subject, ask if user wants to overwrite existing data

	def checkForData(sub):
		if os.path.isdir(sub) and os.path.getsize(sub) > 0:
			print("**********\nMRIQC output already exists for " + sub + "!" + "\n**********")
			time.sleep(2)
			fileStats = os.stat(sub)
			modificationTime = time.ctime(fileStats[8])
			overwriteConfirmation = {
					inq.Confirm('overwriteConfirmation',
									message="Overwrite the mriqc data generated on " + str(modificationTime[:10] + modificationTime[19:]) + " for " + sub + "?",
								),
				}

			overwriteAnswer = inq.prompt(overwriteConfirmation)

			if overwriteAnswer['overwriteConfirmation'] == True:
				print("Overwriting data...")
				time.sleep(.5)
				return True
			else:
				print("Skipping subject...\n")
				time.sleep(1.5)
				return False
		elif os.path.isdir(sub) and os.path.getsize(sub) == 0:
			os.rmdir(sub)
			print("Running MRIQC on " + sub)
			time.sleep(2)
			return True
		else:
			print("Running MRIQC on " + sub)
			time.sleep(2)
			return True


	# this method cleans up the mriqc directory for the selected study.
	# by placing all the html files into their respective sub directories.
	# cannot use until directory permissions get figured out

	def cleanDir(sub, mriqcDir):
		os.chdir(sub)
		os.makedirs("html")
		os.chdir(mriqcDir)
		for file in os.listdir():
			if file.startswith(sub) and file.endswith("html"):
				shutil.move(file, sub + "/html")


# This is a python dictionary that contains key-value pairs of studies and their respective BIDS directories
studyPaths = {"opioid": "/PROJECTS/REHARRIS/opioid/opioid_BIDS", "explosiveSync": "", "bacpac": "", "bacpacBest": "", "mapp2": "/PROJECTS/MAPP/MAPP2/data/MAPP2_BIDS", "cpira2": ""}

# create instance of the mriqcCLI class
qc = mriqcCLI()

# get user specified study and its corresponding BIDS directory
BIDSDir = qc.selectStudy(studyPaths)

# get list of the subjects as specified by the user
subjects = qc.getSubs(BIDSDir)

qc.runMriqc(subjects, BIDSDir)

