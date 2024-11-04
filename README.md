# Recruitment Bot

This bot automates recruitment in Arknights, allowing users to target specific operators (like robots or five-star operators) efficiently using expedited plans.

It connects with an emulator via adb and uses OCR to determine the optimal tags for the character, and inputs them in before expediting.

## Features
- Automates recruitment based on image recognized tags and user priorities.
- Stops recruitment if guaranteed six star or five star operator tags are detected.
- (Optional) Prioritizes four star guarantees for yellow certificates if the primary operator's rarity cannot be guaranteed, or or stops recruitment if the Robot tag is detected. Specified by user preferences.

## Requirements
- Python 3.x
- Libraries: `numpy`, `opencv-python`, `pytesseract`
- Emulator with open adb connection

## Usage

### User Specifications
Open `preferences_gen.py` to configure preferences.
1. Set the `primary_target_name` to specify the primary operator and configure other settings as needed.

	A. Can specify whether or not to prioritize four star tags if the operator's rarity cannot be guaranteed.
	
	B. Can specify whether or not to stop the program if the "robot" tag is found.
	
	C. Can specify a secondary target if no tags for the primary target is found.

2. Run preferences_gen.py. It will search for the specified name in the recruitment database, and displays their tags. If you are satisfied, proceed to main.py

### Running the bot

1. Open Arknights in an emulator with a screen resolution of **1920x1080**.
2. Open the **top-left recruitment slot** window in Arknights.
3. Run `main.py` at the following window to start the bot.

![Screenshot of the Bot in Action](screenshot.png)

4. The bot will automatically detect tags via screenshots, calculate the optimal tags for the prioritized operator, click the tags, select the appropriate timer, hit confirm, and expedite.

	A. If a six star, five star, or one star operator can be guaranteed, the bot stops after displaying possible options, allowing the user to pick the tags specifically.

## Customization
To update your preferences:
1. Edit `preferences_gen.py` with your desired settings.
2. Run `preferences_gen.py` to generate a new `preferences.json` with your updated preferences.

- **primary_target_name**: The name of the main operator to be targeted.
- **stop_on_robot_tag**: Set this to `true` to stop the bot if the "Robot" tag is found.
- **target_priority_over_four_star**: If true, then ignore 4 star guarantees in hopes of prioritizing the main target. If false, then if there is no guarantee for the rarity of the main target, try a 4 star tag to obtain yellow certificates.

### Safety

To avoid detection, the bot clicks at randomized positions with intervals drawn from a Gaussian distribution. Adjust click times in `main.py` if needed (longer for more safety, smaller for more speed)

### Alternative Window Sizes

If using a screen resolution other than 1920x1080, adjust button positions in `main.py` and regenerate tag positions in `tagbuttons.txt`. Example code for generating new tag positions are found in the tag_positions folder.

### Updating Recruitment

Folder recruit_data_gen contains code used to generate recruitment_database.json, which is the database this program uses to calculate recruitments. If you want to update the list of recruitable operators, use the programs in this folder.

## File Structure

- **main.py**: Runs the recruitment bot.
- **preferences_gen.py**: Generates a `preferences.json` file based on user-defined recruitment priorities.
- **recruit_calc.py**: Calculates optimal recruitment tags using preferences. You can uncomment code here to send in custom tags to verify the program works for your purposes.
- **tag_ocr.py** retrieves text for the tags from the screenshots.
- Folders **tag_positions** and **recruit_data_gen** generate the positions of tags (tagbuttons.txt) and the recruitment_database.json (used to calculate recruitments).

## License
MIT License