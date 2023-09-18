import logging
import os

import yaml
from selenium.webdriver.common.by import By


class MirrorDict(dict):
    def __getitem__(self, item):
        return item

logging.basicConfig(filename='DataFiles/bumble.log')
attrMap = {'heightv2': MirrorDict()}

with open(os.path.join("DataFiles", 'config.yaml')) as infile:
    d = yaml.load(infile.read(), Loader=yaml.Loader)
    attrMap.update(d)


def extractData(br):
    divs = br.find_elements(By.CLASS_NAME, "p-3")
    divs = [div for div in divs if div.get_attribute('class') == 'p-3 text-ellipsis font-weight-medium'][:-1]

    attrDivs = br.find_elements(By.CLASS_NAME, "pill__image")

    attrs = {}
    for attr, div in zip(attrDivs, divs):
        br.execute_script("arguments[0].scrollIntoView();", div)
        src = os.path.basename(attr.get_attribute('src'))
        src = src.rsplit('.', 1)[0].rsplit("_", 1)[-1]
        val = div.text.lower()

        if src in attrMap:
            try:
                attrs[src] = attrMap[src][val]
            except KeyError:
                logging.error(f'Value "{val}" not handled for attribute "{src}"')

        else:
            logging.critical(f'Attribute "{src}" not handled. Found value "{val}"')

    if 'heightv2' in attrs:
        height = attrs['heightv2']
        height = [int(h) if h else 0 for h in height.split("'")][:2]
        height = 12*height[0] + height[1]

        attrs['heightv2'] = height

    return attrs

if __name__ == "__main__":
    print('starting')
    print(sorted(attrMap.keys()))
    print('done')