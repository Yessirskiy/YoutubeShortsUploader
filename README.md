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

### Account (BAD WAY)
Follow this [guide](https://developers.google.com/youtube/v3/guides/uploading_a_video):
    1. Create project and add there YouTube API V3 
    2. Create credentials
    3. Use [login file](login.py) to create secrets of this account. Generated file will be required for uploading videos.

### Some words about Google API
Generally, YouTube API v3 was working fine with uploading videos.
BUT, as I recently found out  you have have to reach out the YouTube and send them some sort of form in which you've gotta provide some personal information and also describe, why you want to use this API. Unless you do so, all the published videos will be hidden and there's nothing you can do with that.
So YouTube API was not a solution at all, the only option left right now is to use Selenium.

## Selenium
Firstly, let's get all the required modules:
`pip install -r requirements.txt`
As I'm familiar with Chrome, this application is only support ChromeBrowser, so you will need chromedriver.
You can find your version [here](https://chromedriver.chromium.org/downloads)
Unzip package and save chromedriver.exe
Save path of the chromedriver.exe to the [config file](config.py) as `CHROMEDRIVER_PATH`

## Setup
```
SESSIONS_FOLDER = 'sessions'
VIDEOS_FOLDER = 'videos'
LOGS_FOLDER = 'logs'
CHROMEDRIVER_PATH = 'chromedriver.exe'
HIDE_BROWSER = False
PROCESSING_FINISHED_REGEXP = 'checks complete'
```
Most important setting here is the last one. If you use English verison of Chrome(system language is English) then you've got nothing to worry about.
In any other case, as soon as your file is loaded and bot started filling up all the details you will see status of proving the file at the bottom of the popped up window.
As soon as your file is proved copy first sentence(lower case) of the final status to the PROCESSING_FINISHED_REGEXP(in your langauge).

If you don't want see browser loading all the time you can set HIDE_BROWSER parameter to True.

You should store all the videos in VIDEOS_FOLDER, session of accounts in SESSIONS_FOLDER.
ALl the logs will be saved in files at LOGS_FOLDER.

## How to get session of the account
Firstly, go to this [link](https://chrome.google.com/webstore/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm) and download this extension.
Go to [YouTube](https://youtube.com) and log into your account. Aim on extension and export cookies(Right-Bottom Button).
Create .json file and paste there copied cookies. This file is the session of this account. 
If you can't log into your account you should probably copy and paste sessions one more time.

## Some Features
As you launch the bot, it will ask you for the files with title and descriptions.
Both support emojis. If you want description to be empty, leave there None.



