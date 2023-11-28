#!/usr/bin/env python3.7
import requests
from bs4 import BeautifulSoup
import os
import re
import shutil
import argparse

# Parse command line arguments
parser = argparse.ArgumentParser(description='Download files from Orpheus network.')
parser.add_argument('-l', '--list', action='store_true', help='Use alternative URL and get the first 10 DL links')
parser.add_argument('-f', '--freeleech', action='store_true', help='Check for available Freeleech tokens')
args = parser.parse_args()

# Directory to save files
save_directory = '/home/user/watch/rtorrent'
os.makedirs(save_directory, exist_ok=True)

# Temporary directory within the save directory
temp_directory = os.path.join(save_directory, 'temp')
os.makedirs(temp_directory, exist_ok=True)

# Session cookie
cookie = {'session': 'cookiepastedhere'}

# Headers to mimic browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# Function to get user ID
def get_user_id():
    url = 'https://orpheus.network/index.php'
    response = requests.get(url, cookies=cookie, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        user_link = soup.find('a', class_='username')
        if user_link and 'id=' in user_link['href']:
            return re.search('id=(\d+)', user_link['href']).group(1)
    return None

# Function to get downloaded torrent IDs
def get_downloaded_torrent_ids(user_id):
    downloaded_ids = set()
    for page in range(1, 6):
        torrentid_url = f'https://orpheus.network/torrents.php?type=downloaded&userid={user_id}&page={page}'
        response = requests.get(torrentid_url, cookies=cookie, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            group_infos = soup.find_all('div', class_='group_info')

            for group in group_infos:
                links = group.find_all('a', href=True)
                for link in links:
                    if 'torrentid=' in link['href']:
                        torrentid = re.search('torrentid=(\d+)', link['href']).group(1)
                        downloaded_ids.add(torrentid)
        else:
            break

    return downloaded_ids

# Function to check Freeleech tokens
def check_freeleech_tokens():
    url = 'https://orpheus.network/index.php'
    response = requests.get(url, cookies=cookie, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        fl_token_tag = soup.find('li', id='fl_tokens')

        if fl_token_tag:
            stat_span = fl_token_tag.find('span', class_='stat')
            if stat_span and stat_span.find('a'):
                token_value = stat_span.find('a').get_text()
                try:
                    token_value = int(token_value)
                    return token_value
                except ValueError:
                    pass

        return 0
    else:
        return -1

# Check Freeleech tokens if -f flag is used
use_token = False
if args.freeleech:
    token_count = check_freeleech_tokens()
    if token_count == -1:
        print("Failed to retrieve webpage for Freeleech tokens")
        exit()
    elif token_count >= 1:
        print(f"Remaining Tokens: {token_count}")
        use_token = True
    else:
        print("No Freeleech Tokens Available")
        exit()

# Retrieve user ID
user_id = get_user_id()
if user_id is None:
    print("Failed to retrieve user ID. Check session cookie or network.")
    exit()

# Get downloaded torrent IDs
downloaded_torrent_ids = get_downloaded_torrent_ids(user_id)

# Target URL
url = 'https://orpheus.network/top10.php?type=torrents&limit=10&details=day' if not args.list else 'https://orpheus.network/top10.php'

# Send GET request
response = requests.get(url, cookies=cookie, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    dl_links = [link['href'] for link in soup.find_all('a', string='DL')]

    if args.list:
        dl_links = dl_links[:10]

    for link in dl_links:
        torrent_id = re.search('id=(\d+)', link).group(1)
        if torrent_id in downloaded_torrent_ids:
            print(f"Torrent ID {torrent_id} already downloaded, skipping...")
            continue

        file_url = 'https://orpheus.network/' + link
        if use_token:
            file_url += '&usetoken=1'

        file_response = requests.get(file_url, cookies=cookie, headers=headers, allow_redirects=True, stream=True)

        if file_response.status_code == 200:
            content_disposition = file_response.headers.get('content-disposition')
            if content_disposition:
                filename = re.findall("filename=\"?([^\";]+)\"?", content_disposition)[0]
            else:
                filename = link.split('/')[-1]

            temp_file_path = os.path.join(temp_directory, filename)
            final_file_path = os.path.join(save_directory, filename)

            with open(temp_file_path, 'wb') as file:
                for chunk in file_response.iter_content(chunk_size=128):
                    file.write(chunk)

            if not os.path.exists(final_file_path):
                shutil.move(temp_file_path, final_file_path)
                print(f"File moved to save directory: {final_file_path}")
            else:
                print(f"File already exists, skipped: {final_file_path}")
        else:
            print(f"Failed to download file from {file_url}")

    shutil.rmtree(temp_directory)
    print(f"Temporary directory deleted: {temp_directory}")

else:
    print("Failed to retrieve data. Status code:", response.status_code)
