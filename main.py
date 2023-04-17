from UI import *
import curses
from curses import wrapper

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
