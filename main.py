#!/bin/python3
# Laitanayoola@gmail.com
# https://github.com/Lytes/

import requests
import math
import re
import youtube_dl
import os
import sys 

anime_per_page = 30 #Animepahe's episode links per API request. Might change in the future

payload = "\r\n"  # Required for Animepahe APIs to reply.
episode_links_array = {} # Dictionary to select episode link selected by user

def folder_create(name): # Creates a folder for each anime
	downloads_folder = os.path.join(os.getcwd(), "Downloads")
	anime_folder = os.path.join(downloads_folder, name)
	
	try:
		if os.path.isdir(downloads_folder) != True:
			print("[+][+] Creating general folder")
			os.mkdir(downloads_folder) # Creates general Downloads folder for AnimeAll script 
		if os.path.isdir(anime_folder) != True:
			print("[+][+] Creating download folder for {}".format(name))
			os.mkdir(anime_folder)
	except Exception:
		print("[=][=] Folder creation failed\n[=][=] Make sure you have permission to create folders in current directory")
		sys.exit()
	return(anime_folder)
		
def search_anime(anime_name): # Searches for the anime and returns link of what user picks.
	search_link = "https://animepahe.com/api?m=search&l=8&q={}".format(anime_name.lower()) 
	headers = {'Host': 'animepahe.com', 'Referer': 'https://animepahe.com/', 'Content-Length': '2'}
	r = requests.get(search_link, headers=headers, data=payload)

	if r.json()['total'] == 0: # If no animes were found with name, cancel the program
		print("[+][+] No animes were found with name similar.\n[+][+] Make sure to search in both English and Japanese.")
		sys.exit()		
	
	print("[+][+] Found {} search match(es)".format(r.json()['total']))		
	for i, val in enumerate(r.json()['data']): # Returns info of all search results and an ID Number to make picking easier
		print("\nID Number: ", i+1, "\nTitle:", val['title'], "\nType:", val['type'], "\nEpisodes:", val['episodes'], "\nStatus:", val['status'], "\nYear:", val['year'], "\n\n")
	
	while True: # An infinite while loop that makes sure the user provides a valid nummber before continuing
		download_number=input("[+][+] Which one should I download? Each search result has an ID number.\n[0][0] Kindly input your desired ID Number: ")	
		try: # Incase user decides to input string or Heavens-help a list/dict.
			num = int(download_number)-1
			if int(download_number) > r.json()['total']:
				print("\n[+][+] There are {} results and thereby {} options, Your pick '{}' is out of range.\n[+][+]Kindly select a valid ID number: ".format(r.json()['total'], r.json()['total'], num))
			elif num < 0:
				print("\n[+][+] Really? You seriously want to try and pick a negative number?")
			else:
				break # Break the infinite loop when user's input meets all requirements.
		except Exception:
			print("[+][+] Please make sure your pick is a valid integer")
	
	get_episode_links(r.json()['data'][num]['session'], r.json()['data'][num]['title'], r.json()['data'][num]['episodes'], r.json()['data'][num]['id']) # Calls another function and gives it anime session, anime title, number of episodes and the anime id
	
	
	
def get_episode_links(session, title, episodes_number, anime_id):
	link_anime = "https://animepahe.com/anime/{}".format(session) # Gets the link to the anime page of User's pick
	print("\n[+][+] Picking {}".format(title))
		
	while True: # Another infinite while loop that makes sure the user provides a valid range before continuing
		download_range = input("\n[+][+] There are {} episodes, select range to download e.g '1-{}'.\n[+][+] If you intend to download only one episode, use the episode as range e.g '1-1' or '22-22'\n\n[0][0] Enter Range: ".format(episodes_number, episodes_number)).replace(" ", "") # Incase anyone in their infinite wisdom decides to add whitespace
		regex = re.findall(r'^[0-9]+-[0-9]+$', download_range)			 						
		if len(regex) != 1:
			print("[+][+] Kindly input a valid range. Example => '1-22'")						
		else:
				break # Break the infinite loop when user's input meets all requirements.		
	
	sorted_range = regex[0].split("-")
	sorted_range.sort(key=int) # Sorts user inputted range incase some genius thinks something like '192-1' would make sense for a range. 		
	lower_limit, upper_limit = int(sorted_range[0]), int(sorted_range[1]) # Episodes range to download. Lower limit and upper limit.		
	lower_limit_page_number = math.ceil(lower_limit/anime_per_page) 
	upper_limit_page_number = math.ceil(upper_limit/anime_per_page) # Animepahe's API only gives 30 episodes per page so need to know which specific pages to request for
	
	
	if upper_limit == lower_limit: #User only wants one episode
		search_link = "https://animepahe.com/api?m=release&id={}&l=30&sort=episode_asc&page={}".format(anime_id, upper_limit_page_number) 
		headers = {'Host': 'animepahe.com', 'Referer': '{}'.format(link_anime), 'Content-Length': '2'}
		req = requests.get(search_link, headers=headers, data=payload)
		for i in req.json()['data']:
			if i['episode'] == upper_limit:
				episode_links_array[i['episode']] = "https://animepahe.com/play/{}/{}".format(session, i['session']) 
			
	elif upper_limit_page_number == lower_limit_page_number: # If requested episodes are on the same page.	
		search_link = "https://animepahe.com/api?m=release&id={}&l=30&sort=episode_asc&page={}".format(anime_id, upper_limit_page_number) 
		headers = {'Host': 'animepahe.com', 'Referer': '{}'.format(link_anime), 'Content-Length': '2'}
		req = requests.get(search_link, headers=headers, data=payload)
		for i in req.json()['data']:
			if i['episode'] in range(lower_limit, upper_limit+1):
				episode_links_array[i['episode']] = "https://animepahe.com/play/{}/{}".format(session, i['session'])

	else: # Requires multiple pages 
		for i in range(lower_limit_page_number, upper_limit_page_number+1):
			search_link = "https://animepahe.com/api?m=release&id={}&l=30&sort=episode_asc&page={}".format(anime_id, i)
			headers = {'Host': 'animepahe.com', 'Referer': '{}'.format(link_anime), 'Content-Length': '2'}
			req = requests.get(search_link, headers=headers, data=payload)
			try: # In case a user selects a range bigger than the number of episodes released at the moment
				for i in req.json()['data']:
					if i['episode'] in range(lower_limit, upper_limit+1):
						episode_links_array[i['episode']] = "https://animepahe.com/play/{}/{}".format(session, i['session'])
			except Exception:
				pass
	download_path = folder_create(title)
	download_each_episode(episode_links_array, link_anime, download_path)
				
def download_each_episode(array, referer, download_path):
	for number, link in array.items(): #Iterate through the episode links
		headers = {'Host': 'animepahe.com', 'Referer': '{}'.format(referer), 'Content-Length': '2'}
		r = requests.get(link, headers=headers, data=payload)		
		regexed_link = re.findall(r'https://kwik.cx/e/.*[^"\n;]', r.text)[0] # Gets specific link from the heap of html/js response
		
		headers2 = {'Host': 'kwik.cx', 'Referer': '{}'.format(link)}
		req = requests.get(regexed_link, headers=headers2)
		regexed_string = re.findall(r'https://i\.kwik\.cx.*\.jpg', req.text) # Gets specific link from the heap of html/js response
		needed_string = regexed_string[0].split("/")[-1].split(".")[0] # Gets the important string - The link gotten above is useless 
		
		download_link = "https://cdn-na-d1.nextstream.org/stream/0000/{}/uwu.m3u8".format(needed_string) # Creates the important link using the string
		
		try:			
			print("[+][+] Downloading Episode {} as {}.mp4".format(number, number))
			youtube_dl.std_headers['Referer'] = regexed_link # Youtube_dl when embedded in python doesn't seem to have an options to add referer header so I'm adding it manually
			episode_download_path = os.path.join(download_path, '{}.mp4'.format(number))
			ydl_opts = {'quiet': 'yes', 'outtmpl': episode_download_path}
			#ydl_opts = {}
			with youtube_dl.YoutubeDL(ydl_opts) as ydl:
				ydl.download([download_link])
		except Exception:
			print("[=][=] Error downloading episode {}.mp4".format(number))
			pass	
				
if __name__ == "__main__":
	print("INSERT BANNER")
	anime_name = input("[0][0] Enter anime name: ")
	search_anime(anime_name)			
