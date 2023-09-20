# bumble-autoswipe
Automatically swipe bumble, based on personal preferences

# Installation

1. `requirements.txt` has all the necessary python packages for this project
2. Ensure that the `DataFiles/` directory exists, as this is where log files are placed

This uses a Selenium Firefox browser to read the dom elements from Bumble to swipe left/right based on the preferences listed in `config.yaml`.

# Configuration

The entries in config.yaml are structured by section and then by category. The sections correspond to the filenames used for each of the attributes on a Bumble profile, while the category is each possible description of the section. The values correspond to the user's specific preferences on a scale of 0-1. Currently, this supports two decimal place precision.

For example:

```yaml
drinkingv2:
  never: 0
  almost never: 0.1
  rarely: 0.2
  socially: 1
  frequently: 0.1
```

This corresponds to the drinking section, i.e. how often the potential match drinks.  
The attributes are `never`, `almost never`, `rarely`, `socially`, and `frequently`. In the above example, these are ranked on a 0-1 scale. A value of `1` means that the trait is most desirable, whereas a value of `0` means the trait is least desirable.

Irrelevant sections (i.e. character traits that the user may not care about) can be simply ignored from the config file.

## Height

Height is the only non-categorical trait in the config file. So it has a couple of parameters that need to be fiddled to taste:

1. `min` is the height under which the match is too short
2. `max` is the height above which the match is too tall, but can be compromised
3. `bufferMax` is the height above which the match is too tall, and cannot be compromised

### Units

I'm writing this code in Canada and the height is reported in feet and inches. The height might be reported differently (likely in centimeters) in other parts of the world. If you run into this, please create an issue and I'll try to address it.

## Missing Categories

The current `config.yaml` contains all the sections and categories that I have discovered since I started developing this. I'm sure I've missed a few. Those are logged at runtime in `DataFiles/bumble.log`. Feel free to take a look in here and update the config file to taste.

## Immediate Swipe Decisions

Sometimes there are dealbreakers; and sometimes there's the opposite of that, i.e. an immediate swipe-right (let's call these dealmakers). These can be specifed in `config.yaml` like any other traits.

The specification for non-negotiables is slightly different from the specification for individual traits. Dealbreakers use a `maxValue` - so if a dealbreaker trait has a value lower than `maxValue`, then it's an immediate swipe-left. Similarly, dealmakers use a `minValue` - so if a dealmaker trait has a value greater than or equal to `minValue`, then it's an immediate swipe-right.

> `minValue` and `maxValue` cannot be left unspecified. If a trait doesn't apply, it must not appear in dealmakers/dealbreakers. If a there are no dealbreakers or dealmakers, the section may be omitted or left empty; but trait values must not be left empty and must not be `null`/`None`

In the even that there are both dealbreakers and dealmakers in a given profile, then the immediate swipe left/right logic is ignored and the usual fuzzy system is used (as if dealmakers and dealbreakers were never configured).

### Example: dealbreaker

Suppose `config.yaml` looks like this:

```yaml
dealbreakers:
  smokingv2: 0.1
```

This means that if a profile has a `smokingv2` value of anything less than 0.1 (eg: 0.09, but not 0.1 itself), then it's an immediate swipe left.

A value of 0.1 (or higher) will not result in an immediate swipe left, and the usual fuzzy system takes over.

### Example: dealmaker

Suppose `config.yaml` looks like this:

```yaml
dealmakers:
  drinkingv2: 0.7
```

This means that if a profile has a `drinkingv2` value of anything greater than or equal to 0.7 (eg: 0.7 or 0.71 or 0.8), then it's an immediate swipe right.

A value of 0.69 (or lower) will not result in an immediate swipe right, and the usual fuzzy system takes over.

### Example: both

Suppose `config.yaml` looks like this:

```yaml
dealbreakers:
  smokingv2: 0.1
  
dealmakers:
  drinkingv2: 0.7
```

Now, if a profile has a `drinkingv2` value of 0.8 (normally, an immediate swipe-right), and a `smokingv2` value of 0.09 (normally, an immediate swipe-left), the profile now has both dealbreakers and dealmakers. Therefore, immediate swiping logic is abandoned and the usual fuzzy system takes over.

In such cases, the number of dealbreakers and dealmakers is irrelevant. As long as there's at least one of each, immediate swiping logic is abandoned in favor of the usual fuzzy system.


# How it Works

This uses a Mamdani Fuzzy system to compute a composite based on the configured preferences and automatically swipe. Use at your own discretion.

## Authentication and Privacy

No personal information is sent to the author of this codebase.  
When the browser opens, the user is reponsible for authenticating and logging into Bumble. The program waits for the user to press `ENTER`, to actually start swiping.  
The user will need to authenticate every time the program is executed (since it has no memory of cookies, etc).