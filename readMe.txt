This is a program designed to facilitate the entry of fuel filling station data into a mySQL DB at $Port/stations, and also then allow the user to select the newly added station and add fuel prices at $port/fuel.

This likely will not be useful for other people for the most part, but I'm open to conversations and suggestions.

Deploying PapTwitter:

Must have: 
Python 3.10.2 installed
MySql database installed

Run: python -m pip install -r  ./requirements.txt
to ensure you have all requirements for this project

Also you will need to edit your mySQL log on details and your Twitter Developer keys to be your own

fuelForm.html file is not important to save, as it gets generated within the startFlask.py

Create a config.py file to contain all your SQL log in details and API keys, do not push to repo
