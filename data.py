import logging
import os

import yaml
from selenium.webdriver.common.by import By


class MirrorDict(dict):
    def __getitem__(self, item):
        return item


def loadConfig(infilepath):
    """

    :param infilepath:
    :return:
    """
    logging.basicConfig(filename=infilepath, level=logging.INFO)

    with open(os.path.join("DataFiles", 'config.yaml')) as infile:
        prefs = yaml.load(infile.read(), Loader=yaml.Loader)

    return prefs


def extractData(br, prefs):
    """

    :param br:
    :param prefs:
    :return:
    """
    divs = br.find_elements(By.CLASS_NAME, "p-3")
    divs = [div for div in divs if div.get_attribute('class') == 'p-3 text-ellipsis font-weight-medium'][:-1]

    attrDivs = br.find_elements(By.CLASS_NAME, "pill__image")

    rawData = {}
    attrs = {}
    for attr, div in zip(attrDivs, divs):
        br.execute_script("arguments[0].scrollIntoView();", div)
        src = os.path.basename(attr.get_attribute('src'))
        src = src.rsplit('.', 1)[0].rsplit("_", 1)[-1]
        val = div.text.lower()
        rawData[src] = val

        if src == 'heightv2':
            val = [int(h) if h else 0 for h in val.split("'")][:2]
            val = 12*val[0] + val[1]
            attrs[src] = val
            continue

        if src in prefs:
            try:
                attrs[src] = prefs[src][val]
            except KeyError:
                logging.error(f'Value "{val}" not handled for attribute "{src}"')

        else:
            logging.critical(f'Attribute "{src}" not handled. Found value "{val}"')

    return attrs, rawData
