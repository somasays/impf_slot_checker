from datetime import datetime

import requests
import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from configparser import ConfigParser

CUT_OFF_DATE = datetime.fromisoformat('2021-06-07')
open_drivers = {}
id_url_mapping = {
    "arena": "https://www.doctolib.de/institut/berlin/ciz-berlin-berlin?pid=practice-158431",
    "tempelhof": "https://www.doctolib.de/institut/berlin/ciz-berlin-berlin?pid=practice-158433",
    "tegel": "https://www.doctolib.de/institut/berlin/ciz-berlin-berlin?pid=practice-158436",
    "erika": "https://www.doctolib.de/institut/berlin/ciz-berlin-berlin?pid=practice-158437",
    "messe": "https://www.doctolib.de/institut/berlin/ciz-berlin-berlin?pid=practice-158434",
    "velodrom": "https://www.doctolib.de/institut/berlin/ciz-berlin-berlin?pid=practice-158435"
}


def get_impf_zentrums():
    try:
        return requests.get("https://api.impfstoff.link/?v=0.3&robot=1").json()['stats']
    except Exception as e:
        print(f"Exception occured while trying to access the api, error = {e}")


def atleast_one_slot_open(centre_stat):
    if centre_stat['open']:
        stats = centre_stat['stats']
        for key, value in stats.items():
            stat_date = datetime.strptime(key, '%Y-%m-%d')
            if stat_date >= CUT_OFF_DATE:
                return id_url_mapping[centre_stat['id']]


def open_slots():
    centre_with_slots_open = []
    for impf_zentrum in get_impf_zentrums():
        open_slot = atleast_one_slot_open(impf_zentrum)
        if open_slot:
            centre_with_slots_open.append(open_slot)
    return centre_with_slots_open


def doctolib_login(driver):
    url = "https://www.doctolib.de/sessions/new"
    driver.get(url)
    accept(driver)

    config = ConfigParser()
    config.read('creds', )

    user_name = config['DEFAULT']['username']
    username = driver.find_element_by_name("username")
    username.send_keys(user_name)

    p = config['DEFAULT']['password']
    password = driver.find_elements_by_css_selector("#password")[1]
    password.send_keys(p)

    login_button = driver.\
        find_elements_by_css_selector(".Tappable-inactive.dl-button-DEPRECATED_yellow.dl-toggleable-form-button.dl-button.dl-button-block.dl-button-size-normal")
    login_button[0].click()


def accept(driver):
    try:
        accept_button = driver.find_element_by_id("didomi-notice-agree-button")
        accept_button.click()
    except Exception as e:
        print(f"Exception occurred while trying to click accept {e}")


def create_and_get_driver():
    driver = webdriver.Chrome(ChromeDriverManager().install(), )
    open_drivers[open_slot] = driver
    return driver


def get_open_window_for_slot_or_else(slot):

    existing_driver = open_drivers.get(slot)
    if not existing_driver:
        return False, create_and_get_driver()

    print(f"Driver was able to get the window handle from memory {open_drivers.get(slot)}")
    try:
        rect = existing_driver.get_window_rect()
        print(f"open window for {slot} is {rect}")
    except Exception as e:
        open_drivers.pop(slot)
        print(f"Window for {slot} is closed will open a new window")
        return False, create_and_get_driver()

    return True, existing_driver


if __name__ == '__main__':

    while True:
        time.sleep(1)

        for open_slot in open_slots():
            is_open, driver = get_open_window_for_slot_or_else(open_slot)

            if not is_open:
                doctolib_login(driver)
                time.sleep(2) #to allow login to complete, better would be to use webdriver wait, but hey, it works :)
                driver.get(open_slot)


