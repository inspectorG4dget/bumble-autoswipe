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
    """
    The main function that runs everything
    :return:
    """
    prefs, dealmakers, dealbreakers = data.loadConfig(os.path.join('DataFiles', 'bumble.log'))
    throttleRatio = prefs['throttle_ratio']
    rules = decision.getRules(prefs)
    br = webdriver.Firefox()

    br.get("https://bumble.com/app")

    input("Login and press ENTER to continue: ")

    # number of left and right swipes
    numLeft = 0
    numRight = 0
    while True:

        if len(br.find_elements(By.CLASS_NAME, "cta-box__title")) > 0:
            print('Out of swipes for today')  ##
            break

        attrs, rawData = data.extractData(br, prefs)

        totalSwipes = numLeft + numRight
        try:
            throttleRatio = numRight/totalSwipes
        except ZeroDivisionError:
            pass  # we've already gotten the ratio


        attrs['throttle_ratio'] = rawData['throttle_ratio'] = throttleRatio
        print(f"{throttleRatio = }")  ##

        answer = decision.getSwipeDir(attrs, rules, dealbreakers, dealmakers)

        logging.info(f"{json.dumps(rawData)} | {answer}")

        if answer >= 0.5:
            r = random.random()
            if r <= 1 - (throttleRatio - prefs['throttle_ratio']):
                answer = Keys.ARROW_RIGHT
                numRight += 1
            else:
                answer = Keys.ARROW_LEFT
                numLeft += 1
        else:
            answer = Keys.ARROW_LEFT
            numLeft += 1

        actions = ActionChains(br)
        time.sleep(random.uniform(0,2))
        actions.send_keys(answer)
        actions.perform()

        time.sleep(2)  # let the next profile load

        if len(br.find_elements(By.CLASS_NAME, "encounters-match__header")) > 0:  # there was a match
            b = br.find_elements(By.CLASS_NAME, "encounters-match__cta-action")[1]
            b.click()

    br.quit()


if __name__ == "__main__":
    print('starting')

    main()

    print('done')