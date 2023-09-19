import json
import logging
import os
import random
import time

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import data
import decision


def main():
    br = webdriver.Firefox()

    br.get("https://bumble.com/app")

    input("Login and press ENTER to continue: ")

    while True:

        if len(br.find_elements(By.CLASS_NAME, "cta-box__title")) > 0:
            print('Out of swipes for today')  ##
            break

        attrs, rawData = data.extractData(br)
        answer = decision.getSwipeDir(attrs)

        logging.info(f"{json.dumps(rawData)} | {answer}")

        print(answer)

        if answer >= 0:
            answer = Keys.ARROW_RIGHT
        else:
            answer = Keys.ARROW_LEFT

        actions = ActionChains(br)
        time.sleep(random.uniform(0,2))
        actions.send_keys(answer)
        actions.perform()

        time.sleep(2)  # let the next profile load

    br.quit()


if __name__ == "__main__":
    print('starting')

    main()

    print('done')