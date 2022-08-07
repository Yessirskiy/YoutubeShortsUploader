import logging
import re
from datetime import datetime
from time import sleep
import os

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException

from loguru import logger
import config
import emoji

JS_ADD_TEXT_TO_INPUT = '''
const text = `{content}`;
const dataTransfer = new DataTransfer();
dataTransfer.setData('text', text);
const event = new ClipboardEvent('paste', {{
  clipboardData: dataTransfer,
  bubbles: true
}});
arguments[0].dispatchEvent(event)
'''

def uploadFile(
        driver: WebDriver,
        video_path: str,
        title: str,
        account: str,
        description: str = None,
        game: str = None,
        kids: bool = False,
        thumbnail_path: str = None) -> bool:
    
    driver.get('https://studio.youtube.com/')
    # Clicking on Upload Button
    try:
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "ytcp-button#create-icon"))).click()
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//tp-yt-paper-item[@test-id="upload-beta"]'))
        ).click()
    except Exception as e:
        logger.error("There was an error while trying to click on 'Upload' button. Please, make sure you have all the guides completed.")
        driver.close()
        return False

    # Uploading Video File
    try:
        video_input = driver.find_element("xpath", '//input[@type="file"]')
        video_input.send_keys(os.path.abspath(video_path))
    except Exception as e:
        logger.error("There was an error while uploading file. Please, make sure path to the file with video is correct.")
        driver.close()
        return False

    logger.success("File succesfully loaded on website. Now setting up video's details.")

    basic_setup = _set_basic_settings(driver, title, description, thumbnail_path)
    advance_setup = _set_advanced_settings(driver, game, kids)


    # Go to visibility settings
    for i in range(3):
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "next-button"))).click()

    processed = _wait_for_processing(driver)

    try:
        if basic_setup and advance_setup and processed:
            driver.find_element(By.XPATH, '/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-uploads-review/div[2]/div[1]/ytcp-video-visibility-select/div[1]/tp-yt-paper-radio-group/tp-yt-paper-radio-button[3]').click()
            sleep(3) 
        else:
            return False
    except Exception as e:
        logger.error("Error while setting up access to the video.")
        driver.close()
        return False

    # Upload
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "done-button"))).click()
    sleep(5) # Wait for final screen to disappear
    logger.success(f"Video '{title}' succesfully uploaded on {account}'s account.")
    return True

def _wait_for_processing(driver: WebDriver) -> bool:
    try:
        # Wait for processing to complete
        progress_label: WebElement = driver.find_element(By.CSS_SELECTOR, "span.progress-label")
        #pattern = re.compile(r"(finished processing)|(processing hd.*)|(check.*)")
        pattern = re.compile(fr"({config.PROCESSING_FINISHED_REGEXP})")
        current_progress = progress_label.get_attribute("textContent")
        last_progress = None
        while not pattern.match(current_progress.lower()): # Checking if file is fully submitted
            if last_progress != current_progress:
                logging.info(f'Current progress: {current_progress}')
            last_progress = current_progress
            sleep(5)
            current_progress = progress_label.get_attribute("textContent")
            if current_progress == '':
                logger.error("Video cannot be uploaded on this acc. Maybe, you have reached a limit.")
                driver.close()
                return False

        return True
    except Exception as e:
        logger.error('Error while awaiting for processing the video.')
        driver.close()
        return False

def _set_basic_settings(driver: WebDriver, title: str|None, description: str|None, thumbnail_path: str|None) -> bool:
    try:
        title_input: WebElement = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    '/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-ve/ytcp-video-metadata-editor/div/ytcp-video-metadata-editor-basics/div[1]/ytcp-social-suggestions-textbox/ytcp-form-input-container/div[1]/div[2]/div/ytcp-social-suggestion-input/div',

                )
            )
        ) # Waiting until file is loaded

        title_input: WebElement = driver.find_element(
            By.XPATH,
            '/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-ve/ytcp-video-metadata-editor/div/ytcp-video-metadata-editor-basics/div[1]/ytcp-social-suggestions-textbox/ytcp-form-input-container/div[1]/div[2]/div/ytcp-social-suggestion-input/div'
        )
        description_input: WebElement = driver.find_element(
        By.XPATH, '/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-ve/ytcp-video-metadata-editor/div/ytcp-video-metadata-editor-basics/div[2]/ytcp-social-suggestions-textbox/ytcp-form-input-container/div[1]/div[2]/div/ytcp-social-suggestion-input/div'
        )
        thumbnail_input: WebElement = driver.find_element(
            By.CSS_SELECTOR,
            "input#file-loader"
        )

        if title:
            title_input.clear()
            if emoji.emoji_count(title) > 0: # If emoji in title
                driver.execute_script("arguments[0].innerHTML = '{}'".format(title), title_input)
            else:
                title_input.send_keys(title)

        if description:
            if emoji.emoji_count(description) > 0: # If emoji in description
                driver.execute_script("arguments[0].innerHTML = '{}'".format(description), description_input)
            else:
                description_input.send_keys(description)

        if thumbnail_path:
            thumbnail_input.send_keys(thumbnail_path)
        return True
    except Exception as e:
        logger.error('Error occured while setting up Title, Description or Thumbnail of the video.')
        driver.close()
        return False

def _set_advanced_settings(driver: WebDriver, game_title: str, made_for_kids: bool) -> bool:
    try:
        # Open advanced options
        driver.find_element(By.CSS_SELECTOR, "#toggle-button").click()
        if game_title:
            game_title_input: WebElement = driver.find_element(
                By.CSS_SELECTOR,
                ".ytcp-form-gaming > "
                "ytcp-dropdown-trigger:nth-child(1) > "
                ":nth-child(2) > div:nth-child(3) > input:nth-child(3)"
            )
            game_title_input.send_keys(game_title)

            # Select first item in game drop down
            WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable(
                    (
                        By.CSS_SELECTOR,
                        "#text-item-2",  # The first item is an empty item
                    )
                )
            ).click()

        WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
            (By.NAME, "VIDEO_MADE_FOR_KIDS_MFK" if made_for_kids else "VIDEO_MADE_FOR_KIDS_NOT_MFK")
        )).click()
        return True
    except Exception as e:
        logger.error("Error while setting GameTitle or Kids Restrictions.")
        driver.close()
        return False

# Functions down below are not used in a project

def _set_endcard(driver: WebDriver):
    # Add endscreen
    driver.find_element(By.CSS_SELECTOR, "#endscreens-button").click()
    sleep(5)

    for i in range(1, 11):
        try:
            # Select endcard type from last video or first suggestion if no prev. video
            driver.find_element(By.CSS_SELECTOR, "div.card:nth-child(1)").click()
            break
        except (NoSuchElementException, ElementNotInteractableException):
            logging.warning(f"Couldn't find endcard button. Retry in 5s! ({i}/10)")
            sleep(5)

    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "save-button"))).click()

def _set_time(driver: WebDriver, upload_time: datetime):
    # Start time scheduling
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.NAME, "SCHEDULE"))).click()

    # Open date_picker
    driver.find_element(By.CSS_SELECTOR, "#datepicker-trigger > ytcp-dropdown-trigger:nth-child(1)").click()

    date_input: WebElement = driver.find_element(By.CSS_SELECTOR, "input.tp-yt-paper-input")
    date_input.clear()
    # Transform date into required format: Mar 19, 2021
    date_input.send_keys(upload_time.strftime("%b %d, %Y"))
    date_input.send_keys(Keys.RETURN)

    # Open time_picker
    driver.find_element(
        By.CSS_SELECTOR, 
        "#time-of-day-trigger > ytcp-dropdown-trigger:nth-child(1) > div:nth-child(2)"
    ).click()

    time_list = driver.find_element(By.CSS_SELECTOR, "tp-yt-paper-item.tp-yt-paper-item")
    # Transform time into required format: 8:15 PM
    time_str = upload_time.strftime("%I:%M %p").strip("0")
    time = [time for time in time_list[2:] if time.text == time_str][0]
    time.click()