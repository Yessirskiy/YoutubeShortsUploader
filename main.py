from typing import Dict, List, Tuple
import os
import random
import time
from loguru import logger

from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.chrome.service import Service

from login import login
from upload import uploadFile
import config

from rich.console import Console
from rich.tree import Tree
from rich.prompt import IntPrompt, Prompt


def setLogging(logs_folder: str):
    '''
    Setting logger for the whole bot

    Parameters
    ----------
        logs_folder (str): Name of the folder to save logs in
    '''
    if not os.path.exists(logs_folder):
        try:
            os.mkdir(logs_folder)
        except PermissionError:
            return False
    SINK = os.path.join(logs_folder, 'main_{time:DD-MM-YYYY}.log')
    LEVEL = 'INFO'
    LOGS_FORMAT = '{time: HH:mm:ss:SS DD.MM.YYYY} | {level} | {message}'
    ROTATION = '00:00'
    COMPRESSION = 'zip'
    logger.add(sink=SINK, level=LEVEL, format=LOGS_FORMAT, rotation=ROTATION, compression=COMPRESSION)

def setDirectory(session_folder: str, videos_folder: str):
    '''
    Setting app's folders
    
    Parameters
    ----------
        session_folder (str): Name of the folder with sessions
        videos_folder (str): Name of the folder with videos

    '''
    try:
        if not os.path.exists(session_folder):
            os.mkdir(session_folder)
        if not os.path.exists(videos_folder):
            os.mkdir(videos_folder)
        if not os.path.exists(config.CHROMEDRIVER_PATH):
            logger.error("Incorrect path for the chromedriver. Browser will not launch.")
    except Exception as e:
        if isinstance(e, PermissionError):
            logger.error("Bot has no permission to create any folders(required). Please, launch application as administrator.")

def setDriver(path: str) -> WebDriver:
    '''
    Creating driver of chrome browser

    Parameters
    ----------
        path (str): Path to the chromedriver.exe file

    Returns
    -------
        driver (webdriver): Created driver
    '''
    options = webdriver.ChromeOptions()
    service = Service(executable_path=os.path.abspath(path))
    options.headless = config.HIDE_BROWSER
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'}) # Setting language to english (may not work)
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_window_size(1920, 1080)

    return driver

def getSettings(console: Console) -> Tuple[int, int, str, str]:
    '''
    Getting User's settings input

    Parameters
    ----------
        console (Console): Console instance

    Returns
    -------
        result (Tuple[int, int, str, str])
            delay (int): Delay between publishing videos
            amount (int): Amount of videos to post from each account
            description (str): Description for publications
            title (str): Title for the publications
    '''
    accounts = os.listdir(config.SESSIONS_FOLDER)
    accs = Tree("[b magenta]List of accounts to post on[/b magenta]")
    for account in accounts:
        accs.add(f"[b cyan]{account}[/b cyan]")
    console.print(accs)
    delay = IntPrompt.ask("[yellow]Enter delay between publishing videos (seconds)[/yellow]", console=console)
    amount_choices = list([str(i) for i in range(21)])
    amount = IntPrompt.ask("[yellow]Enter amount of videos to publish from each account (<20)[/yellow]", console=console, choices=amount_choices, show_choices=False)
    title_file = Prompt.ask(f"[yellow]File with the title[/yellow]", choices=[file for file in os.listdir(".") if '.' in file and file.split('.')[1] == 'txt'], console=console)
    description_file = Prompt.ask(f"[yellow]File with the description[/yellow]", choices=[file for file in os.listdir(".") if '.' in file and file.split('.')[1] == 'txt' and file != title_file], console=console)
    
    with open(title_file, encoding='utf-8') as file:
        title = file.read()
    with open(description_file, encoding='utf-8') as file:
        description = file.read()
        if description.lower().strip() == 'none' or description.strip() == '':
            description = None
    return delay, amount, description, title

def isFinished(target_amount: int, launch: Dict) -> bool:
    '''
    Checks if target amount of posted videos was reached

    Parameters
    ----------
        target_amount (int): Target amount of published videos
        launch (Dict): Dict with information about current launch

    Returns
    -------
        result (bool): True - finished, False - not finished
    '''
    total = 0
    for acc in launch.values():
        total += acc['posted']
    
    return total >= target_amount

def chooseTarget(target_amount: int, launch: Dict, accounts: List[str]) -> str:
    '''
    Choosing account to post from

    Parameters
    ----------
        target_amount (int): Amount of videos to post from each account
        launch (Dict): Dictionary with information about current launch
        accounts (List[str]): List of accounts

    Returns
    -------
        account (str): Choosen account to post from
    
    '''
    choose_from = []
    for account in accounts:
        if launch[account]['posted'] < target_amount:
            choose_from.append(account)
    return random.choice(choose_from)

def mainLoop(delay: int, amount: int, description: str, title: str) -> bool:
    '''
    Main loop of the application

    Parameters
    ----------
        delay (int): Delay between posting videos
        amount (int): Amount of videos to post from each account
        description (str): Description for the publications
        title (str): Title for the publications

    Returns
    -------
        result (bool): True - succesfully finished; False - in case of errors
    '''
    accounts = os.listdir(config.SESSIONS_FOLDER)
    videos = os.listdir(config.VIDEOS_FOLDER)
    launch = {}
    for acc in accounts:
        launch[acc] = {
            'posted' : 0
        }

    if len(accounts) == 0:
        logger.error(f"No acconts to post from. Please, put cookies of accounts in '{config.SESSIONS_FOLDER}' folder.")
        return False
    if len(videos) == 0:
        logger.error(f"No videos to post. Please, put some videos in '{config.VIDEOS_FOLDER}' folder.")
        return False

    while not isFinished(amount, launch):
        driver = setDriver(config.CHROMEDRIVER_PATH)
        target_acc = chooseTarget(amount, launch, accounts)
        res = login(driver, os.path.join(config.SESSIONS_FOLDER, target_acc), target_acc.split('.')[0])
        if res:
            video = random.choice(videos)
            upload = uploadFile(
                driver=driver,
                video_path=os.path.join(config.VIDEOS_FOLDER, video),
                title=title,
                account=target_acc.split('.')[0],
                description=description
            )
            if upload:
                launch[target_acc]['posted'] += 1
                driver.close()
                time.sleep(delay)
    logger.success("Succesfully posted all the videos. Shutting down the application.")
    return True
  
def main():
    setLogging(config.LOGS_FOLDER)
    setDirectory(config.SESSIONS_FOLDER, config.VIDEOS_FOLDER)
    console = Console()
    delay, amount, description, title = getSettings(console)
    mainLoop(delay, amount, description, title)
    input("Press ENTER to exit...")

if __name__ == "__main__":
    if authUser():
        main()
    input("Press ENTER to exit...")