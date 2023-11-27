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
args = parser.parse_args()

# Directory to save files
save_directory = '/home/user/watch/rtorrent'
os.makedirs(save_directory, exist_ok=True)

# Temporary directory within the save directory
temp_directory = os.path.join(save_directory, 'temp')
os.makedirs(temp_directory, exist_ok=True)

# Session cookie
cookie = {'session': 'yourseedhere'}

# Target URL
url = 'https://orpheus.network/top10.php?type=torrents&limit=10&details=day' if not args.list else 'https://orpheus.network/top10.php'

# Headers to mimic browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# Send GET request
response = requests.get(url, cookies=cookie, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    # Parse HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all links with anchor text 'DL'
    dl_links = [link['href'] for link in soup.find_all('a', string='DL')]

    # If -l flag is used, limit to first 10 links
    if args.list:
        dl_links = dl_links[:10]

    # Download and save each file
    for link in dl_links:
        file_url = 'https://orpheus.network/' + link
        file_response = requests.get(file_url, cookies=cookie, headers=headers, allow_redirects=True, stream=True)

        # Check if the file download request was successful
        if file_response.status_code == 200:
            # Determine file name from Content-Disposition header or URL
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

            # Move file if it does not exist in the save directory
            if not os.path.exists(final_file_path):
                shutil.move(temp_file_path, final_file_path)
                print(f"File moved to save directory: {final_file_path}")
            else:
                print(f"File already exists, skipped: {final_file_path}")
        else:
            print(f"Failed to download file from {file_url}")

    # Delete the temp directory after processing all files
    shutil.rmtree(temp_directory)
    print(f"Temporary directory deleted: {temp_directory}")

else:
    print("Failed to retrieve data. Status code:", response.status_code)
