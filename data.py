import logging
import os

import yaml
from selenium.webdriver.common.by import By


class MirrorDict(dict):
    """
    A dictionary whose values are the keys themselves.
    It's really more of a collections.defaultdict because you don't have to insert a key,value pair first, to query it
    """
    def __getitem__(self, item):
        return item


def  loadConfig(infilepath):
    """
    Load the config file
    :param infilepath: str. The filepath of the config file.
    :return: {trait: {category: value, ...}, ...}. The loaded config
    """
    logging.basicConfig(filename=infilepath, level=logging.INFO)

    with open(os.path.join("DataFiles", 'config.yaml')) as infile:
        prefs = yaml.load(infile.read(), Loader=yaml.Loader)

    return prefs


def extractData(br, prefs):
    """
    Given the selenium browser object and the preferences dict, pull the data out of the webpage.
    :param br: The selenium webdriver
    :param prefs: {trait: {category: value, ...}, ...} The preferences dict loaded by `loadConfig`
    :return: {trait: value, ...}, {trait: category}. This is a 2-tuple
        The second element is a dictionary with the raw trait values seen on the Bumble interface.
            This is used later, for logging.
        The first element is a dictionary with the configured values. This will ultimately be input into the fuzzy system
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
