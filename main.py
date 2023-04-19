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
from devices import *
from serial import Serial
from os import path, remove
from curses import wrapper
from datetime import datetime, timedelta

#Globals for location and port for the serial
SER_LOC, SER_PORT = "/dev/ttyACM0", 9600

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
	pairs = [l.split(': ') for l in lines]
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

#Takes the save data dictionary, and writes it to the save file
def write_save_data(data:dict):
	#Only delete the last save file if it exists
	if path.isfile(SETTINGS):
		remove(SETTINGS)

	with open(SETTINGS, 'w') as settings: #Open the settings file for writing
		for save_key in data:         #Write each piece of data in file
			settings.write(f"{save_key}: {data[save_key]}\n")

#Given serial port, and required water level, checks and gets to that water level
def moisture_loop(serialPort, waterLevel):
	moisture = readMoisture(serialPort)
	
	#Open file, write this debug information
	with open('water-log.txt', 'w') as f:
		f.write(f"Moisture {moisture:03d}% at {datetime.now()}\n")
	
	#While the moisture level isn't desired level
	while moisture < waterLevel.percent:
		#Water the plant! NEEDS IMPLEMENTING LOL
		moisture = readMoisture(serialPort)
		break #STOP BECAUSE WE CANNOT WATER THE PLANT YET HAHAHAHA

def main(curseScrn):
	#Makes getch non-blocking, allowing to glance at character inputs
	curseScrn.nodelay(True)
	
	#Create the serial port to read moisture readings
	serial = Serial(SER_LOC, SER_PORT)

	#Instantiates the lcd screen that we will be using this whole time
	screen = LCD(0x27, 1, curseScrn, numlines=4)

	#Attempt to load any save data from the program
	save_data_exists, save_data = load_saved_data()

	#Default of False (not set), will cause us first-force-watering
	next_soil_check = False 

	#If the local save data exists, use it
	if save_data_exists:
		#Makes ui reflect that these should be the selected options from onset
		UI_tabs["Delay"][SELECTION] = save_data[SETTING_DELAY]	
		UI_tabs["Water"][SELECTION] = save_data[SETTING_WATER]	
		#Save the time for the next soil check
		next_soil_check = save_data[NEXT_SOIL_CHECK]

	#Changes UI tabs so that each tab has correct number of options (opt-len)
	prep_opt_length()

	#The index (which tab) is selected
	tab_select = 0
	
	display_ui(screen, tab_select)

	cmd = ""	
	
	#First pulse will force a soil-check to ensure it's moist
	force_soil_check = True

	last_pulse = datetime.now() 
	five_mins  = timedelta(minutes=5) #timedelta(minutes=1) 
	next_pulse = last_pulse + five_mins

	#soil_check_time = last_pulse

	while True:
		now = datetime.now()

		#Every five minutes:
		# 1) Update UI: time till watering
		# 2) Write current time to file
		# 3) See if it is time to check soil
		#    3a) Check + water soil
		#    3b) Save upcoming check time
		if now >= next_pulse:
			#Fetch the water and delay selections made by the user
			water_tab_sel = UI_tabs["Water"][SELECTION]
			delay_tab_sel = UI_tabs["Delay"][SELECTION]

			#Retrieve the moisture percentage, and delay time selected by user
			moisture_lvl  = UI_tabs["Water"][OPTIONS][water_tab_sel]
			delay_time    = UI_tabs["Delay"][OPTIONS][delay_tab_sel].deltatime

			#if there is no saved time for soil check, check soil NOW
			if not next_soil_check:
				moisture_loop(serial, moisture_lvl)
				next_soil_check = datetime.now() + delay_time
			
			#If it is time for the soil check, do it, update timer
			elif now >= next_soil_check:
				moisture_loop(serial, moisture_lvl)
				next_soil_check = datetime.now() + delay_time

			else: #Otherwise, just wait another 5 mins to check
				last_pulse = now			
				next_pulse = now + five_mins

			break #STOP STOP STOP STOP STOP 

			#Store current time, next soil check, and settings to save file
			save_data[TIME_NOW]        = str(now)
			save_data[NEXT_SOIL_CHECK] = str(next_soil_check)
			save_data[SETTING_DELAY]   = str(delay_tab_sel)
			save_data[SETTING_WATER]   = str(water_tab_sel)
		
			#Saves the users selections, current time, next soil check
			write_save_data(save_data)

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
