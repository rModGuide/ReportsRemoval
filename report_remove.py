# Reports Removal Bot by u/BuckRowdy

# Import modules

import praw
import time
from datetime import datetime as dt
import traceback
import sys


# Define the subreddit you're working on.
sub_name = 'YOUR_SUBREDDIT_NAME'

# Define interval for the bot to run: 60 seconds in a minute, 60 minutes in one hour.
sleep_seconds = 60*60*1

# Define time period to search for removed links.
# Currently set at one week - 60 seconds per hour, 24 hours, 7 days.
removal_timespan = (60*60*24*7)

# Reddit login.  Insert your login credentials below. 
def reddit_login():
	reddit = praw.Reddit(
							user_agent = 'Reports Remove Bot v.1 by u/buckrowdy',
							client_id = '',
							client_secret = '',
							username = '',
							password = ''
						)
	print(f'Logged in as: {reddit.user.me()}\n\n')
	return reddit


# Compile removed thread IDs and store them in a text file so they can be referenced for the reports function.
def report_remove_compile(subreddit):
	links_list = []
	
	# Saves links in a text file.  If file does not exist it will be created.
	with open("/home/pi/bots/ModGuide/links_list.txt", "w+") as f:
		print("Compiling list of removed threads...")
		#right_now = time.time()
		removal_epoch = (time.time() - removal_timespan)
		for log_item in reddit.subreddit(sub_name).mod.log(limit = None):
			if log_item.created_utc >= removal_epoch:            
				if log_item.action == 'removelink':
					# Exempt AutoModerator removed links; only search for non-bot mod removals.
					if log_item.mod != 'AutoModerator':                        
						logged_item = log_item.target_fullname
						if logged_item not in links_list:
							links_list.append(str(logged_item))                            
		f.write(f"{links_list}")    
		return links_list                
	print("Done compiling removed threads...")

# Check for reported comments in removed threads and then remove them. 
def report_remove(links_list):
	try:
		print("Looking for reports on removed threads....")
		if len(links_list) > 0:
				print("Okay, I'm checking for reports on removed posts...")
				for item in reddit.subreddit(sub_name).mod.reports(limit = None):
					if item.fullname.startswith("t1_"):
						if item.link_id in links_list:
							item.mod.remove()
							print(f'REMOVE ITEM: r/{item.subreddit} | {item.permalink}')
		else:
			print('None found')
		print("Done removing any reported comments in removed threads....")
	except KeyboardInterrupt:
			print('\nShutting down....')
			sys.exit(1)
	except Exception as e:
		print(f'\t### ERROR - Something went wrong.\n\t{e}')
		traceback.print_exc() 

#  Bot starts below
############################

if __name__ == "__main__":
	
	try:
			# Connect to reddit
			reddit = reddit_login()

			# Connect to the sub
			subreddit = reddit.subreddit(sub_name)

	except Exception as e:
		print('\t\n### ERROR - Could not connect to reddit.')
		sys.exit(1) 
		
	# Loop the bot
	while True:
		try:
			links_list = report_remove_compile(subreddit)
			report_remove(links_list)
		# If you interrupt the bot with ctrl+c the script will shut down a bit more elegantly.
		except KeyboardInterrupt:
			print('\nShutting down....')
			sys.exit(1)
		except Exception as e:
			print(f'\t### ERROR - Soemthing went wrong.\n\t{e}')
			traceback.print_exc() 

		# Loop the bot with a time period defined above. 
		# Change the print statement if you change the loop time period.
		print('Be back in an hour..\n')
		time.sleep(sleep_seconds)
