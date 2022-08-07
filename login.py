import json
from typing import Dict, List

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from loguru import logger

def domainToURL(domain: str) -> str:
    """ 
    Converts a domain to the valid URL 

    Parameters
    ----------
        domain (str): Partial domain

    Returns
    -------
        url (str): Valid URL
    """
    if domain.startswith("."):
        domain = "www" + domain
    return "http://" + domain

def login(driver: WebDriver, cookies_file: str, account: str) -> bool:
    """
    Loggin in account using cookies.

    Parameters
    ---------- 
        driver (WebDriver): Selenium WebDriver to access from
        cookies_file (str): Path to the file with cookies of account

    Returns
    -------
        logged_in (bool): True - succesfully logged in, False - didn't log in

    Restore auth cookies from a file. Does not guarantee that the user is logged in afterwards.
    Visits the domains specified in the cookies to set them, the previous page is not restored.
    """

    logger.info(f"Logging in {account}'s account")

    domain_cookies: Dict[str, List[object]] = {}

    with open(cookies_file) as file:
        cookies: List = json.load(file)
        # Sort cookies by domain, because we need to visit to domain to add cookies
        for cookie in cookies:
            try:
                domain_cookies[cookie["domain"]].append(cookie)
            except KeyError:
                domain_cookies[cookie["domain"]] = [cookie]

    for domain, cookies in domain_cookies.items():
        driver.get(domainToURL(domain + "/robots.txt"))
        for cookie in cookies:
            cookie.pop("sameSite", None) 
            cookie.pop("storeId", None)  
            try:
                driver.add_cookie(cookie)
            except:
                logger.error(f"Couldnt's set cookie {cookie['name']} for {domain}")

    driver.get("https://www.youtube.com")
    assert "YouTube" in driver.title # Checks if YouTube opened

    try:
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "avatar-btn")))
        logger.success(f'Succesfully logged in {account} account.')
        return True
    except TimeoutError:
        logger.error(f"Couldn't log in {account} account. Please, update cookies of this account and try again.")
        return False    