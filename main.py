import os
import subprocess
import time
import re
import numpy as np
from tag_ocr import recruit_ocr
from recruit_calc import process_recruitment, process_recruitment_results, load_recruitment_database, compare_with_recruitment_tags

## The number of expedites to use.
expedites = 70

##==========Pixel Locations for Emulator Usage==============##
##The positions of buttons to click for the timer, and recruitment confirmation
##These can be extracted manually from a screenshot
timer_pos = [(920, 445), (675, 445), (930, 225), (680, 225)]
confirm_pos = [1465, 870]

##This file contains the information of where the tags are located
##This is in the form of rectangles, which are harder to calibate.
rectangle_data_file = 'tagbuttons.txt'  # Rectangle data file path

##The location of the recruit button we want to use, as well as the expedite button
recruit_spot = [705, 565]

##The location of confirming an expedite
expedite_loc = [1440, 765]

##The location of the recruitment skip button
skip_loc = [1840, 80]

##=========Time Values=========================##
##Increase these if you are concerned about being detected for botting, or decrease for extra speed.
#the average time between clicks on the main menu - this is related to server calls
#so best to be a bit long to not get flagged as a bot
tag_average_wait_time = 2  # Average wait time in seconds
menu_average_wait_time = 4 
recruit_sleep_time = 6 #how long it takes to load a recruit
recruit_text_time = 6 #how long it takes for the recruit text to load and be skipped

recruitment_data = load_recruitment_database()

def get_active_emulator():
    # Get the list of connected devices
    result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
    lines = result.stdout.splitlines()
    
    # Filter for active emulator devices (ignore offline devices)
    for line in lines[1:]:
        if ("emulator" in line or "localhost" in line) and "device" in line:
            device_id = line.split()[0]
            print(f"Found active emulator with ID: {device_id}")
            return device_id
    print("No active emulator found.")
    return None

def connect_to_emulator(device_id):
    # Check if the device is already connected
    result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
    if f"{device_id}\tdevice" in result.stdout:
        print(f"{device_id} is already connected.")
        return True
    
    # Attempt to connect to the emulator if not connected
    result = subprocess.run(["adb", "connect", device_id], capture_output=True, text=True)
    if "connected" in result.stdout or "already connected" in result.stdout:
        print(f"Successfully connected to {device_id}")
        return True
    else:
        print(f"Failed to connect to {device_id}: {result.stderr}")
        return False

def take_screenshot(device_id, filename="screenshot.png"):
    # Take a screenshot for a specific device ID and save it to the local system
    result = subprocess.run(["adb", "-s", device_id, "exec-out", "screencap", "-p"], capture_output=True)
    if result.returncode == 0:
        with open(filename, "wb") as f:
            f.write(result.stdout)
        print(f"Screenshot saved as {filename}")
        return filename
    else:
        print("Error taking screenshot:", result.stderr.decode())
        return None

def delete_file(file_path):
    try:
        os.remove(file_path)
        print(f"File '{file_path}' deleted successfully.")
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except Exception as e:
        print(f"Error deleting file '{file_path}': {e}")

def random_wait_normal(average_wait_time, std_dev=1.0):    # Draw a random wait time from a Poisson distribution with the specified average
    wait_time = max(1.0, np.random.normal(average_wait_time, std_dev))
    #print(f"Waiting for {wait_time} seconds to simulate human interaction.")
    time.sleep(wait_time)
    
def click_position(device_id, x, y):
    x = x + (int)(2- np.random.rand()*4)
    y = y + (int)(2- np.random.rand()*4)
    command = ["adb", "-s", device_id, "shell", "input", "tap", str(x), str(y)]
    result = subprocess.run(command, capture_output=True, text=True)
    
    #if result.returncode == 0:
        #print(f"Tapped on position ({x}, {y})")
    #else:
    #    print(f"Error tapping on position ({x}, {y}): {result.stderr}")

def click_tags(device_id, positions, indices, tag_average_wait_time):
    for index in indices:
        pos = positions[index]  # Get the position corresponding to the index in indices
        x, y = pos[0], pos[1]
        
        # Call function to click on the position
        click_position(device_id, x, y)
        
        # Wait for a random time before the next click to mimic human interaction
        random_wait_normal(tag_average_wait_time)

# Image processing and text extraction
def load_rectangle_data_from_file(file_path):
    rectangle_data = []
    with open(file_path, 'r') as file:
        for line in file:
            match = re.search(r'Center: \((\d+), (\d+)\), Width: (\d+), Height: (\d+)', line)
            if match:
                center_x = int(match.group(1))
                center_y = int(match.group(2))
                width = int(match.group(3))
                height = int(match.group(4))
                rectangle_data.append({'Center_X': center_x, 'Center_Y': center_y, 'Width': width, 'Height': height})
    return rectangle_data

# Function to perform the required sequence of clicks with delays
def timer_confirm(device_id, timer_pos, confirm_pos, nine_timer):
    timer_average_wait_time = 1 #This can be short - it's just selecting the timer.
    if nine_timer:
        print ("Setting to 9:00")
        # Click at the third position in timer_positions_fin once
        click_position(device_id, timer_pos[1][0], timer_pos[1][1])
        random_wait_normal(timer_average_wait_time)
    else:
        # Click the first position in timer_positions_fin three times
        for _ in range(3):
            click_position(device_id, timer_pos[3][0], timer_pos[3][1])
            random_wait_normal(timer_average_wait_time)
        # Click the fourth position in timer_positions_fin once
        click_position(device_id, timer_pos[0][0], timer_pos[0][1])
        random_wait_normal(timer_average_wait_time)
    random_wait_normal(3)
    click_position(device_id, confirm_pos[0], confirm_pos[1])

# Find an active emulator
device_id = get_active_emulator()
if device_id:
    # Connect to the emulator if found
    if connect_to_emulator(device_id):

        stop_flag = False
        
        while expedites > 0 and stop_flag == False:
            print ("Remaining expedites:                ", expedites)
            screenshot_path = take_screenshot(device_id)
            if screenshot_path:
                #average_wait_time = 5
                text_results, positions = recruit_ocr(rectangle_data_file, screenshot_path)
                matched_tags = compare_with_recruitment_tags(text_results)
                matched_tags, six_star, five_star, four_star, robot, three_star = process_recruitment(matched_tags, recruitment_data)

                flag, result = process_recruitment_results(matched_tags, six_star, five_star, four_star, robot, three_star)   # Clean up the screenshot file after each loop iteration if no conditions were met
                if flag == 0:
                    print ("Six star detected! Possible tags", six_star)
                    stop_flag = True
                         
                elif flag == 1:
                    print ("Five star detected! Possible tags", five_star)
                    stop_flag = True
                          
                elif flag == 2:
                    print ("Robot tag detected! Possible tags", robot)    
                    stop_flag = True
                    
                else:
                    if flag == 3:
                        print ("9:00 Recruitment.")
                        nine_timer = True
                    if flag == 4:
                        print ("3:50 Recruitment.")
                        nine_timer = False
                    if flag == 5:
                        nine_timer = True
                        print ("No tags found.")
                    else:
                        tag_decisions = result[0]
                        print ("Proceeding with tags ", tag_decisions , ' from ', matched_tags)
                        indices = [i for i, tag in enumerate(matched_tags) if tag in tag_decisions]
                        tag_average_wait_time = 2  # Average wait time in seconds
                        click_tags(device_id, positions, indices, tag_average_wait_time)
                    
                    ##Set the timer for this recruitment
                    timer_confirm(device_id, timer_pos, confirm_pos, nine_timer)
                    
                    ## The expedition process
                    #print ("Expediting!")
                    random_wait_normal(menu_average_wait_time)
                    click_position(device_id, recruit_spot[0], recruit_spot[1])
                    #print ("Confirm Expedite")
                    random_wait_normal(menu_average_wait_time)
                    click_position(device_id, expedite_loc[0], expedite_loc[1])
                    random_wait_normal(menu_average_wait_time)
                    #print ("Confirm Result")
                    click_position(device_id, recruit_spot[0], recruit_spot[1])
                    #print ("Click Skip")
                    time.sleep(recruit_sleep_time)
                    random_wait_normal(menu_average_wait_time)
                    click_position(device_id, skip_loc[0], skip_loc[1])
                    #print ("Wait for text line to finish.")
                    time.sleep(recruit_sleep_time)
                    random_wait_normal(menu_average_wait_time)
                    click_position(device_id, skip_loc[0], skip_loc[1])
                    random_wait_normal(menu_average_wait_time)
                    click_position(device_id, recruit_spot[0], recruit_spot[1])
                    random_wait_normal(menu_average_wait_time)
                    print ("Ready to recruit again!")
                    expedites = expedites - 1
    else:
        print("Could not connect to the emulator.")
else:
    print("No emulator available for connection.")
