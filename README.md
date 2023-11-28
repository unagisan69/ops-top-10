# Orpheus Top 10 Snatcher
Snatch the current Top 10 from OPS to your watch folder. Checks to ensure the .torrent file doesn't already exist in watch folder and also that you haven't previously downloaded the torrent. 
## Usage
./ops-top-10.py

use the argument -l to use https://orpheus.network/top10.php rather than https://orpheus.network/top10.php?type=torrents&limit=10&details=day

## Installation
chmod +x ops-top-10.py

Enter your session cookie and watch folder location.

Find your session cookie using your browser's DOM inspector, under the Application tab, click the Cookies dropdown, then https://orpheus.network, then copy the Value. 
