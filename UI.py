"""
File:   UI.py
Author: Alastar Slater
Date:   April 15, 2023
Info:   A series of routines, definitions, and classes
which enable the user interface for the Plant Nanny.
UI is displayed on a LCD screen, 4x20 characters.
"""
import curses
from curses import wrapper
from math import ceil
from serial import Serial
from enum import Enum, auto
from time import sleep
from inputs import readMoisture
from datetime import datetime, timedelta
from liquidcrystal_i2c import LiquidCrystal_I2C as I2C_LCD

#Globals for location and port for the serial
SER_LOC, SER_PORT = "/dev/ttyACM0", 9600

#This is a class for the convenience of me, Alastar. For various
# reasons the actual physical LCD screen I have is being almost
# unusable. This class allows me to use the physical screen,
# and have it update the physical screen as I would hope, while
# allowing me to see and test the UI on an actual computer screen.
class LCD:
	def __init__(self, addr, bus, curseScrn, numlines=2, linelen=20):
		self.lcd = I2C_LCD(addr, bus, numlines=numlines) 
		self.curse = curseScrn
		self.screen = [" " * linelen] * numlines
		self.linelength = linelen
		self.numlines   = numlines
	
	def getch(self) -> chr:
		char = self.curse.getch()
		
		#Do not accept any non-ascii char
		if char < 32:
			return ' '
		
		return chr(char)
	
	def eraseScreen(self):
		self.curse.erase()

	def writeLine(self, line, string):
		#raise error if too large a value
		if line >= self.numlines:
			raise ValueError(f"ERROR: {line} is not within max bound {self.numlines-1}")
		
		scrnLine  = list(self.screen[line]) #Screen line, now not weird w/ pointers
		charIndex = 0                      
		
		#Add these characters to virtual screen
		while charIndex < len(string):
			scrnLine[charIndex] = string[charIndex]
			charIndex += 1

		#Save changes to the screen 
		self.screen[line] = "".join(scrnLine)
	
	#Print out all te lines in the virtual screen
	def refresh(self):
		self.eraseScreen()	
		for (string, line) in zip(self.screen, range(self.numlines)):
			self.curse.addstr(line, 0, string)	
		self.curse.refresh()
	
	def printline(self, line, string):
		self.writeLine(line, string)
		self.lcd.printline(line, string)
		


#Time unit, can be day or week
class Time(Enum):
	DAY   = auto()
	WEEK  = auto()
	#HOUR  = auto()
	#MONTH = auto()

#An option for delay, some number of days/weeks
class DelayOption:
	def __init__(self, unit, amount):
		self.unit   = unit
		self.amount = amount
		self.deltatime = self.toTimeDelta()
	
	def __repr__(self):
		suffix = {Time.DAY:'D', Time.WEEK:'W'}
		
		return str(self.amount) + suffix.get(self.unit, " UKN")
	
	def __str__(self):
		return self.__repr__()

	def __len__(self):
		return len(self.__str__())		  
	
	#Takes this delay option, and return it as a timedelta object
	def toTimeDelta(self):
		if self.unit == Time.DAY:
			return timedelta(days=self.amount)	

		elif self.unit == Time.WEEK:
			return timedelta(weeks=self.amount)
		
		#elif self.unit == Time.MONTH:
		#	return timedelta(days=self.amount * 30)

class WaterOption:
	#Percent is just an integer 1-100
	def __init__(self, percent):
		self.percent = percent

	__repr__ = lambda self: f"{self.percent}%"
	__str__ = lambda self: self.__repr__()
	__len__ = lambda self: len(self.__repr__())

#Given some text, adds spaces to the left to center the text
def center(text, maxlength=20):
	#Throw error at runtime if text is too long
	if len(text) > maxlength:
		raise ValueError(f"Provided string \"{text}\" is longer than max of {maxlength} characters!")
	
	#Create number of spaces left of text to center it
	left_buffer = " " * ceil((maxlength - len(text))/2)
	
	return left_buffer + text

#Clears out a line so we have no leftover chars
def clearline(display, line, maxchars=20):
	display.printline(line, " " * maxchars)

#Variable used to nab the current selected option in each tab
SELECTION = "SELECTION"
#Variable used to grab the options which the user can pick between in relevant tab
OPTIONS   = "OPTIONS"
#Length of options list (how many options there are)
OPT_LEN   = "OPT_LEN"

#The two seperate 'tabs' where user can make relevant options
UI_tabs = {
	"Delay": {
		SELECTION: 0,
		OPT_LEN: 0,   #Will get set to correct number in prep func
		OPTIONS: [
			DelayOption(Time.DAY, 1), DelayOption(Time.DAY, 2), 
			DelayOption(Time.DAY, 3), DelayOption(Time.DAY, 4),
			DelayOption(Time.DAY, 5), DelayOption(Time.DAY, 6),
			DelayOption(Time.WEEK, 1), DelayOption(Time.WEEK, 2),
			DelayOption(Time.WEEK, 3), DelayOption(Time.WEEK, 4)
			]
		},

	"Water": {
		SELECTION: 0,
		OPT_LEN: 0,   #Will get set correct in prep func
		OPTIONS: [WaterOption(10), WaterOption(15), WaterOption(20), WaterOption(25)]
		} 
}

#The line below tab name that indicates selection
tabSelLines = {
	0: " " * 7 + "-" * 13,
	1: "-" * 6 + " " * 9 + 5 * "-"
}

#Select tab name rom index
selectedTab = lambda i: list(UI_tabs)[i]

#Takes tab index, wraps to first tab if going past options, else, next option
wrapTab = lambda n: 0 if n >= len(list(UI_tabs)) else n

def update_ui(screen, tab_select):
	#Using the current selection, pick relevent line below tab names
	screen.printline(1, tabSelLines[tab_select])

	tab     = selectedTab(tab_select)
	options = UI_tabs[tab][OPTIONS]
	opt_sel = UI_tabs[tab][SELECTION]
	max_opt = UI_tabs[tab][OPT_LEN]

	clearline(screen, 2) #clear out second line, remove remaining chars
	screen.printline(2, center(str(options[opt_sel])))
	#Display to user that they have N/M selected in tab
	screen.printline(3, " " * 15 + f"{opt_sel+1:02d}/{max_opt:02d}")
	#screen.updateScreen()

#
def display_ui(screen, tab_select):
	#Display the tab names at the very top
	screen.printline(0, " | ".join(UI_tabs) + " |")
	update_ui(screen, tab_select)

#Ensures that the OPT_LEN properties are the required length
def prep_opt_length():
	for tab in UI_tabs:
		UI_tabs[tab][OPT_LEN] = len(UI_tabs[tab][OPTIONS])

def main(curseScrn):
	curseScrn.nodelay(True)
	#Instantiates the lcd screen that we will be using this whole time
	#screen = liquidcrystal_i2c.LiquidCrystal_I2C(0x27, 1, numlines=4)
	screen = LCD(0x27, 1, curseScrn, numlines=4)
	#screen.eraseScreen()
	#screen.backlight() #255)

	prep_opt_length()

	#The index (which tab) is selected
	tab_select = 0
	
	display_ui(screen, tab_select)

	cmd = ""	

	#print("Enter 1 or s to change tab.\nEnter 2 or o to change option.\n\n")

	while True:
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
