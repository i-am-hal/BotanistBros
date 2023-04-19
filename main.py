"""
File:   main.py
Date:   April 18
Author: Alastar Slater
Info:   The entrypoint for the Plant Nanny program.
Inputs, be it from keyboard buttons or regular ones,
are reistered here. Will save user settings to a file,
and oversee the intermittent watering of the plant 
when the time is needed.

Save file data:
NOW:time last recorded
NEXT-CHECK:time for next moisture check
SETTING-DELAY:index for what delay option is selected
SETTING-WATER:index for what water option is selected
"""

import curses
from UI import *
from inputs import *
from os import path
from curses import wrapper
from datetime import datetime, timedelta

#Constants for settings file
SETTINGS        = "plantnanny.save.txt"
TIME_NOW        = "NOW"
NEXT_SOIL_CHECK = "NEXT-CHECK"
SETTING_DELAY   = "SETTING-DELAY"
SETTING_WATER   = "SETTING-WATER"
#Parse string needed to parse times from save file
TIME_PARSE_STR  = "%Y-%m-%d %H:%M:%S.%f"

#Reads the save file, parses info, returns save data as dict
def read_save() -> dict:
	#Get all of the lines from the save file
	lines = [line.strip() for line in open(SETTINGS, 'r').readlines()]
	#Create key-value pairs based on all the lines of info
	pairs = [l.split(':') for l in lines]
	#Take the key-value pairs and shove them into dictionary that is save data
	data = {name:value for (name,value) in pairs}

	#Parses last recorded time into a datetime object
	data[TIME_NOW] = datetime.strptime(data[TIME_NOW], TIME_PARSE_STR)
	#Parses the estimated time for the soil to be checked
	data[NEXT_SOIL_CHECK] = datetime.strptime(data[NEXT_SOIL_CHECK], TIME_PARSE_STR)
	#Convert the indices for water, delay settings into integers
	data[SETTING_DELAY] = int(data[SETTING_DELAY])
	data[SETTING_WATER] = int(data[SETTING_WATER])
	
	return data

#Loads saved data, but only if there is save data
def load_saved_data() -> (bool, dict):
	if path.isfile(SETTINGS):
		return True, read_save()
	
	return False, {SETTING_DELAY: 0, SETTING_WATER: 0}

def main(curseScrn):
	#Makes getch non-blocking, allowing to glance at character inputs
	curseScrn.nodelay(True)

	#Instantiates the lcd screen that we will be using this whole time
	screen = LCD(0x27, 1, curseScrn, numlines=4)

	#Attempt to load any save data from the program
	save_data_exists, save_data = load_saved_data()

	#If the local save data exists, use it
	if save_data_exists:
		#Makes ui reflect that these should be the selected options from onset
		UI_tabs["Delay"][SELECTION] = save_data[SETTING_DELAY]	
		UI_tabs["Water"][SELECTION] = save_data[SETTING_WATER]	

	prep_opt_length()

	#The index (which tab) is selected
	tab_select = 0
	
	display_ui(screen, tab_select)

	cmd = ""	

	last_pulse = datetime.now() 
	five_mins  = timedelta(minutes=5)
	next_pulse = last_pulse + five_mins

	while True:
		now = datetime.now()

		#Every five minutes:
		# 1) Update UI: time till watering
		# 2) Write current time to file
		if now >= next_pulse:
			last_pulse = now			
			next_pulse = now + five_mins

		#Go to next tab
		if cmd in "1s":
			tab_select = wrapTab(tab_select+1)
			#print(f"Next tab {tab_select}")
			update_ui(screen, tab_select)
		
		#Cycle through options in this tab
		elif cmd in "2o":
			tab = list(UI_tabs)[tab_select]
			tab_options  = UI_tabs[tab][OPTIONS]
			tab_curr_sel = UI_tabs[tab][SELECTION]
			
			if tab_curr_sel >= len(tab_options)-1:
				UI_tabs[tab][SELECTION] = 0
			else:
				UI_tabs[tab][SELECTION] += 1

			#Update no matter what
			update_ui(screen, tab_select)

		#display_ui(screen, tab_select)
		screen.refresh()
		cmd = screen.getch()


if __name__ == "__main__":
	wrapper(main)
