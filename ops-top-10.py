import requests
from bs4 import BeautifulSoup
import os
import re

# Watch folder
save_directory = '/your/watch/dir'
os.makedirs(save_directory, exist_ok=True)

# Session cookie
cookie = {'session': 'pasteyourcookiehere'}

# Target URL
url = 'https://orpheus.network/top10.php?type=torrents&limit=10&details=day'

# Send GET request
response = requests.get(url, cookies=cookie)

# Check if the request was successful
if response.status_code == 200:
    # Parse HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all links with anchor text 'DL'
    dl_links = [link['href'] for link in soup.find_all('a', string='DL')]

    # Download and save each file
    for link in dl_links:
        file_url = 'https://orpheus.network/' + link
        file_response = requests.get(file_url, cookies=cookie, stream=True)

        # Check if the file download request was successful
        if file_response.status_code == 200:
            # Determine file name from Content-Disposition header or URL
            content_disposition = file_response.headers.get('content-disposition')
            if content_disposition:
                filename = re.findall("filename=(.+)", content_disposition)[0].strip('"')
            else:
                filename = link.split('/')[-1]

            file_path = os.path.join(save_directory, filename)

            # Check if file already exists
            if not os.path.exists(file_path):
                with open(file_path, 'wb') as file:
                    for chunk in file_response.iter_content(chunk_size=128):
                        file.write(chunk)
                print(f"File saved: {file_path}")
            else:
                print(f"File already exists: {file_path}")
        else:
            print(f"Failed to download file from {file_url}")

else:
    print("Failed to retrieve data. Status code:", response.status_code)
