# YoutubeShortsUploader

## About Project
The idea of this project is simple and achievable. 
So, I need bot which will post Youtube Shorts from different accounts.
Videos are pre-made and stored in one folder.

## Realisation
Firstly, I'm trying to figure out how to log into Google Account and post video from it.
Then, just will make a simple console-based application which will ask for a duration of delays, accs and etc. 

Project will be based on Google API service, which as I know provide functionality to post videos on youtube using it.

## Setup
First of all, creating virtual environment using virtualenv module:
`virtualenv venv`
Then, activate using: `venv\Scripts\activate`
Let's update virtualenv using: `python.exe -m pip install --upgrade pip`

### Account
Follow this [guide](https://developers.google.com/youtube/v3/guides/uploading_a_video):
    1. Create project and add there YouTube API V3 
    2. Create credentials
    3. Use [login file](login.py) to create secrets of this account. Generated file will be required for uploading videos.