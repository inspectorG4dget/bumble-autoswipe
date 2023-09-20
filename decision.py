import logging

import numpy as np
import skfuzzy as fuzz
import skfuzzy.control as ctrl


def getRules(prefs):
    """
    Generate all fuzzy rules based on othe user's preferences
    :param prefs: {trait: {category: input value for fuzzy system, ...}, ...}
        This has the same structure as the config file
    :return: {trait: [rule, rule, ...], ...}
        all fuzzy rules key'd by traits in the preference
    """
    universe = np.linspace(-1, 1, 50)
    swipe = ctrl.Consequent(universe, 'swipedir')
    swipe['left'] = fuzz.trapmf(universe, (-1, -1, -0.5, 0))
    swipe['right'] = fuzz.trapmf(universe, (0.5, 1, 1, 1))

    RULES = {}

    universe = np.arange(0, 78, 1)
    key = 'heightv2'
    rule = ctrl.Antecedent(universe, key)
    rule['tooShort'] = fuzz.trapmf(universe, (0, 0, prefs[key]['min'], prefs[key]['max']))
    rule['works'] = fuzz.trimf(universe, (prefs[key]['min'], prefs[key]['max'], prefs[key]['bufferMax']))
    rule['tooTall'] = fuzz.trapmf(universe, (prefs[key]['max'], prefs[key]['bufferMax'], 78, 78))

    RULES[key] = [ctrl.Rule(antecedent = rule['works'],
                            consequent = swipe['right']
                            ),
                  ctrl.Rule(antecedent = rule['tooTall'],
                            consequent = swipe['left']
                            ),
                  ctrl.Rule(antecedent = rule['tooShort'],
                            consequent = swipe['left']
                            ),
                  ]

    for k in prefs:
        universe = np.linspace(0, 1, 100)
        rule = ctrl.Antecedent(universe, k)
        rule['no'] = fuzz.trimf(universe, (0,0,1))
        rule['yes'] = fuzz.trimf(universe, (0,1,1))

        RULES[k] = [ctrl.Rule(antecedent = rule['no'],
                              consequent = swipe['left'],
                              ),
                    ctrl.Rule(antecedent = rule['yes'],
                              consequent = swipe['right'],
                              ),
                    ]

    return RULES

def getSwipeDir(attributes, RULES):
    """
    Create a fuzzy system and get the output, based on the input data available.
    Filter `RULES` by the available data. The filtered rules go into the fuzzy system
    :param attributes: {trait: value, ...}
        captured from Bumb;es interface
    :param RULES: {trait: [rule, rule, ...], ...}
        The set of all rules created from the preferences in config.yaml
    :return: float. The output of the fuzzy system.
        Values under 0 are swipe left
        Values >= 0 are swipe right
    """
    rules = []
    for a in attributes:
        if a not in RULES:
            logging.warning(f"Attribute '{a}' not considered for inputs")
            continue

        rules.extend(RULES[a])

    system = ctrl.ControlSystem(rules=rules)
    sim = ctrl.ControlSystemSimulation(system)
    for a,v in attributes.items():
        if a not in RULES: continue
        sim.input[a] = v

    if not rules: return 1

    sim.compute()
    return sim.output['swipedir']