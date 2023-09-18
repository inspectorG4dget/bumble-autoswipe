import time

import os

from selenium.webdriver.common.by import By

import data

from selenium import webdriver

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

import decision


def main():
    br = webdriver.Firefox()

    br.get("https://bumble.com/app")

    input("Login and press ENTER to continue: ")

    while True:

        if br.find_elements(By.CLASS_NAME, "cta-box__title")[0].text == "You’ve hit the end of the line — for today!":
            print('Out of swipes for today')  ##
            break

        attrs = data.extractData(br)
        answer = decision.getSwipeDir(attrs)

        print(answer)

        if answer >= 0:
            answer = Keys.ARROW_RIGHT
        else:
            answer = Keys.ARROW_LEFT

        actions = ActionChains(br)
        actions.send_keys(answer)
        actions.perform()

        time.sleep(2)  # let the next profile load

    br.quit()


if __name__ == "__main__":
    print('starting')

    main()

    print('done')