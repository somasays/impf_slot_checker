from datetime import datetime

import requests
import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from configparser import ConfigParser

open_drivers = {}

def get_impf_zentrums():
    return requests.get("https://api.impfstoff.link/?v=0.3&robot=1").json()['stats']

id_url_mapping = {
    "arena": "https://www.doctolib.de/institut/berlin/ciz-berlin-berlin?pid=practice-158431",
    "tempelhof": "https://www.doctolib.de/institut/berlin/ciz-berlin-berlin?pid=practice-158433",
    "tegel": "https://www.doctolib.de/institut/berlin/ciz-berlin-berlin?pid=practice-158436",
    "erika": "https://www.doctolib.de/institut/berlin/ciz-berlin-berlin?pid=practice-158437",
    "messe": "https://www.doctolib.de/institut/berlin/ciz-berlin-berlin?pid=practice-158434",
    "velodrom": "https://www.doctolib.de/institut/berlin/ciz-berlin-berlin?pid=practice-158435"
}


def is_slot_open(centre_stat):

    if centre_stat['open']:
        stats = centre_stat['stats']
        for key, value in stats.items():
            stat_date = datetime.strptime(key, '%Y-%m-%d')
            if stat_date >= datetime.fromisoformat('2021-06-07'):
                return id_url_mapping[centre_stat['id']]


def open_slots():
    centre_with_slots_open = []
    for impf_zentrum in get_impf_zentrums():
        open_slot = is_slot_open(impf_zentrum)
        if open_slot:
            centre_with_slots_open.append(open_slot)
    return centre_with_slots_open


def doctolib_login(driver):
    url = "https://www.doctolib.de/sessions/new"

    config = ConfigParser()
    config.read('creds',)
    user_name = config['DEFAULT']['username']
    p = config['DEFAULT']['password']

    driver.get(url)
    accept(driver)

    username = driver.find_element_by_name("username")
    password = driver.find_elements_by_css_selector("#password")[1]

    username.send_keys(user_name)
    password.send_keys(p)

    login_button = driver.find_elements_by_css_selector(".Tappable-inactive.dl-button-DEPRECATED_yellow.dl-toggleable-form-button.dl-button.dl-button-block.dl-button-size-normal")
    login_button[0].click()


def accept(driver):
    try:
        accept_button = driver.find_element_by_id("didomi-notice-agree-button")
        if accept_button:
            accept_button.click()
    except Exception as e:
        print(f"Exception occurred while trying to click accept {e}")


def get_open_window_for_slot_or_else(open_slot):
    print(f"Driver was able to get the window handle from memory {open_drivers.get(open_slot)}")
    existing_driver = open_drivers.get(open_slot)
    if not existing_driver:
        return False, create_and_get_driver()
    try:
        rect = existing_driver.get_window_rect()
        print(f"open window for {open_slot} is {rect}")
    except:
        open_drivers.pop(open_slot)
        print(f"Window for {open_slot} is closed will open a new window")
        return False, create_and_get_driver()
    return True, existing_driver


def create_and_get_driver():
    driver = webdriver.Chrome(ChromeDriverManager().install(), )
    open_drivers[open_slot] = driver
    return driver


if __name__ == '__main__':
    while True:
        time.sleep(1)
        for open_slot in open_slots():
            is_open, driver = get_open_window_for_slot_or_else(open_slot)
            if not is_open:
                doctolib_login(driver)
                time.sleep(2)
                driver.get(open_slot)


