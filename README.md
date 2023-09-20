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

# How it Works

This uses a Mamdani Fuzzy system to compute a composite based on the configured preferences and automatically swipe. Use at your own discretion.

## Authentication and Privacy

No personal information is sent to the author of this codebase.  
When the browser opens, the user is reponsible for authenticating and logging into Bumble. The program waits for the user to press `ENTER`, to actually start swiping.  
The user will need to authenticate every time the program is executed (since it has no memory of cookies, etc).