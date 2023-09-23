import logging
import math

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
    universe = np.linspace(0, 1, 50)
    swipe = ctrl.Consequent(universe, 'swipedir')
    swipe['left'] = fuzz.trapmf(universe, (0, 0, 0.25, 0.75))
    swipe['right'] = fuzz.trapmf(universe, (0.25, 0.75, 1, 1))

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
    prefs.pop(key, None)

    universe = np.arange(0,1,0.01)
    key = 'throttle_ratio'
    rule = ctrl.Antecedent(universe, key)
    rule['low'] = fuzz.trimf(universe, (0, 0, prefs[key]))
    rule['high'] = fuzz.trimf(universe, (prefs[key], 1, 1.5))
    rule['perfect'] = fuzz.trimf(universe, (prefs[key]/2, prefs[key], min(1, prefs[key]*1.15)))

    RULES[key] = [ctrl.Rule(antecedent = rule['high'],
                            consequent = swipe['left'],
                            ),
                  ctrl.Rule(antecedent = rule['perfect'],
                            consequent = swipe['right'],
                            ),
                  ]
    prefs.pop(key, None)

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

def getSwipeDir(attributes, RULES, dealbreakers, dealmakers):
    """
    Create a fuzzy system and get the output, based on the input data available.
    Filter `RULES` by the available data. The filtered rules go into the fuzzy system

    Dealbreakers and dealmakers (immediate swipe-right) are handled. In the event that there's both (at least one
        dealbreaker and at least one dealmaker), then skip the immediate swipe and go on to the actual fuzzy system

    :param attributes: {trait: value, ...}
        The preference value of each trait captured from Bumble's interface
        Other parameters may be added into this, such as the `throttle_ratio`
    :param RULES: {trait: [rule, rule, ...], ...}
        The set of all rules created from the preferences in config.yaml
    :param dealbreakers: {trait: maxValue, ...}
        If there's a trait in `attributes` that's also in `dealbreakers`,
            if the attribute/trait value is lower than the `maxValue`, then return -1 - this is a dealbreaker
    :param dealmakers: {trait: minValue, ...}
        If there's a trait in `attributes` that's also in `dealmakers`,
            if the attribute/trait value is at least the dealmaker/trait value, then return 1 - this is an immediate yes
    :return: float. The output of the fuzzy system.
        Values under 0 are swipe left
        Values >= 0 are swipe right
    """

    prompts = attributes.pop('prompts', None)  # to be handled later
    bio = attributes.pop('bio', None)  # to be handled later

    yes, no = 0, 0  # dealmakers and dealbreakers
    for a,v in attributes.items():
        yes += v >= dealmakers.get(a, math.inf)
        no += v < dealbreakers.get(a, -math.inf)

    if yes and not no: return 1
    if no and not yes: return 0

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