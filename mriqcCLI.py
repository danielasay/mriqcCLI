# Thoughts for creating mriqc pipeline:

# 1) Ask the user which study they want to qc
# 2) Ask if they want it run on all subjects, only new, or a specific list
# 3) Confirm the study and the number of subjects that will be processed
# 4) Show progress bar


import inquirer as inq
import time

class mriqcCLI():
	def __init__(self):	
		pass


	def selectStudy(self, studyPaths):
		while True:
			try:
				studies = [
					inq.List('studies',
									message = "Which study would you like to qc?",
									choices = ['opioid', 'explosive sync', 'bacpac', 'bacpac best', 'mapp2', 'micapp', 'cpira2', 'all of the above'],
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

		return studyAnswer


	def validateBIDSDir(self, study):
		if studyPaths[study] == "":
			return False
		else:
			return True

studyPaths = {"opioid": "/PROJECTS/REHARRIS/opioid/opioid_BIDS", "explosiveSync": "", "bacpac": "", "bacpacBest": "", "mapp2": "/PROJECTS/MAPP/MAPP2/data/MAPP2_BIDS", "cpira2": ""}

qc = mriqcCLI()

selectedStudy = qc.selectStudy(studyPaths)

print(selectedStudy)

#print(studyPaths[selectedStudy])



