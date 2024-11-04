import re
import json
from itertools import combinations

# Define the RECRUITMENT_TAGS array
RECRUITMENT_TAGS = [
    "Top Operator", "Senior Operator", "Starter", "Robot", "Melee", "Ranged",
    "Caster", "Defender", "Guard", "Medic", "Sniper", "Specialist", "Supporter",
    "Vanguard", "AoE", "Crowd-Control", "DP-Recovery", "DPS", "Debuff", "Defense",
    "Fast-Redeploy", "Healing", "Nuker", "Shift", "Slow", "Summon", "Support", "Survival",
    "Elemental"
]

# Load recruitment database
def load_recruitment_database(file_path="recruitment_database.json"):
    with open(file_path, "r", encoding="utf-8") as f:
        recruitment_data = json.load(f)
    return recruitment_data

def compare_with_recruitment_tags(text_results):
    matched_tags = []
    for text in text_results:
        normalized_text = re.sub(r'[\s-]', '', text).lower()
        for i in range(len(RECRUITMENT_TAGS)):
            tag = RECRUITMENT_TAGS[i]
            normalized_tag = re.sub(r'[\s-]', '', tag).lower()
            if normalized_text == normalized_tag:
                matched_tags.append(tag)
                break  # Stop further checking once a match is found
    return matched_tags

# Calculate possible recruit combinations
def calculate_combinations(input_tags, recruitment_data):
    tag_sets = [list(combinations(input_tags, i + 1)) for i in range(3)]
    flat_tag_sets = [set(tags) for sublist in tag_sets for tags in sublist]
    results_array = []
    for tag_set in flat_tag_sets:
        matched_operators = [
            op for op in recruitment_data if tag_set.issubset(op["tags"])
        ]
        if matched_operators:
            matched_operators.sort(key=lambda x: x["rarity"], reverse=True)
            matched_operator_ids = [op["name"] for op in matched_operators]
            rarity_operators = [op["rarity"] for op in matched_operators]
            if "Top Operator" not in tag_set:
                filtered_ids_rarities = [
                    (id, rarity) for id, rarity in zip(matched_operator_ids, rarity_operators) if rarity != 6
                ]
                matched_operator_ids, rarity_operators = zip(*filtered_ids_rarities) if filtered_ids_rarities else ([], [])
            if len(rarity_operators) > 0:
                results_array.append([
                    sorted(tag_set),           # Tag combination as sorted list
                    list(matched_operator_ids), # List of matched operator IDs
                    list(rarity_operators)      # List of rarities of matched operators
                ])
    return results_array

# Categorize results
def categorize_results(results_array):
    six_stars, five_stars, four_stars, robots, three_stars = [], [], [], [], []
    for tag_combination, matched_operator_ids, rarity_operators in results_array:
        lowest_rarity = min([r for r in rarity_operators if r > 1], default=None)
        if "Top Operator" in tag_combination:
            six_stars.append([tag_combination, matched_operator_ids, rarity_operators])
        elif lowest_rarity == 5:
            five_stars.append([tag_combination, matched_operator_ids, rarity_operators])
        elif lowest_rarity == 4:
            four_stars.append([tag_combination, matched_operator_ids, rarity_operators])
        elif 1 in rarity_operators and 2 not in rarity_operators and 3 not in rarity_operators:
            robots.append([tag_combination, matched_operator_ids, rarity_operators])
        else:
            three_stars.append([tag_combination, matched_operator_ids, rarity_operators])
    return six_stars, five_stars, four_stars, robots, three_stars

def process_recruitment(text_results, recruitment_data):
    matched_tags = compare_with_recruitment_tags(text_results)
    recruitment_results = calculate_combinations(matched_tags, recruitment_data)
    six_stars, five_stars, four_stars, robots, three_star = categorize_results(recruitment_results)
    return matched_tags, six_stars, five_stars, four_stars, robots, three_star

# Function to evaluate scores
def evaluate_array(array_of_arrays, target_name, current_score):
    best_score = current_score
    best_array = None
    for element in array_of_arrays:
        _, names, rarities = element
        if target_name in names:
            rarity = rarities[names.index(target_name)]
            count_same_rarity = rarities.count(rarity)
            if count_same_rarity < best_score:
                best_score = count_same_rarity
                best_array = element
    return best_score, best_array

def process_recruitment_results(matched_tags, six_stars, five_stars, four_stars, robots, three_star):
    # Load user preferences from preferences.json
    with open("preferences.json", "r") as f:
        preferences = json.load(f)

    primary_target = preferences.get("primary_target")
    primary_target_name = primary_target['name']
    primary_target_rarity = primary_target['rarity']
    secondary_target = preferences.get("secondary_target")
    secondary_target_name = secondary_target['name']
    secondary_target_rarity = secondary_target['rarity']
    stop_on_robot_tag = preferences.get("stop_on_robot_tag", False)  # Get the stop_on_robot_tag flag
    priority_over_four_star = preferences.get("priority_over_four_star", False)  # Get the stop_on_four_star_tag flag
    
    # print("The primary target is", primary_target_name)
    
    # Check conditions for setting the stop flag
    if len(six_stars) > 0 :
        stop_flag = 0
        return stop_flag, []
    
    elif len(five_stars) > 0 :
        stop_flag = 1
        return stop_flag, []
    
    # Check for the "Robot" tag in matched_tags and the stop_on_robot_tag flag
    elif stop_on_robot_tag and "Robot" in matched_tags:
        stop_flag = 2
        return stop_flag, []
    
    # Initialize high scores with 99
    primary_fourstar_score = 99
    primary_robot_score = 99
    primary_threestar_score = 99

    secondary_threestar_score = 99

    # Track which arrays contain the best scores
    best_fourstar_array = None
    best_robot_array = None
    best_threestar_array = None
    
    # Track which arrays contain the best scores
    secondary_threestar_array = None

    # Calculate scores for primary and secondary targets in each category
    primary_fourstar_score, best_fourstar_array = evaluate_array(four_stars, primary_target_name, primary_fourstar_score)
    primary_robot_score, best_robot_array = evaluate_array(robots, primary_target_name, primary_robot_score)
    primary_threestar_score, best_threestar_array = evaluate_array(three_star, primary_target_name, primary_threestar_score)

    secondary_threestar_score, secondary_threestar_array = evaluate_array(three_star, secondary_target_name, secondary_threestar_score)

    # Display best arrays containing each score
    # print("\nBest array for primary four-star score:", best_fourstar_array, ' with score ', primary_fourstar_score)
    # print("\nBest array for primary robot score:", best_robot_array, ' with score ', primary_robot_score)
    # print("\nBest array for primary three-star score:", best_threestar_array, ' with score ', primary_threestar_score)

    # print("\nBest array for secondary three-star score:", secondary_threestar_array, "with score", secondary_threestar_score)

    # If it's robot, start looking in robots
    
    ##We have to keep of track of whether or not the target is a robot or not in the recruitment timer process.
    if primary_target_rarity >=3:
        stop_flag = 3 #9 hours for high rarity
    else:
        stop_flag = 4 #3:50
        
    
    if primary_target_rarity == 1:
        if primary_robot_score < 90:
            return stop_flag, best_robot_array
    # else start looking in 4 stars
    if primary_fourstar_score <90: #If there was a 4 star option
        return stop_flag, best_fourstar_array
    if len(four_stars)>0 and priority_over_four_star == False:
        #if the 4 star flag takes priority, then just send in a four star option
        return 3, four_stars[0]
    #else, we send in a three star option if its good
    if primary_threestar_score < 90:
        return stop_flag, best_threestar_array
    #finally, no good three star option, no four star option, look for the secondary
    if secondary_threestar_score < 90:
        if secondary_target_rarity >=3:
            stop_flag = 3 #9 hours for high rarity
        else:
            stop_flag = 4 #3:50
        return stop_flag, secondary_threestar_array
    return 5, []
    

#Example usage
recruitment_data = load_recruitment_database()
sample_tags = ["Fast-Redeploy", "DPS"]
matched_tags, six_star, five_star, four_star, robot, three_star = process_recruitment(sample_tags, recruitment_data)

print("6-Star Combinations:", six_star)
print("5-Star Guarantee:", five_star)
print("4-Star Guarantee:", four_star)
print("Robot Guarantee:", robot)
print("3-Star Tags:", three_star)

print("\n\n")

flag, result = process_recruitment_results(matched_tags, six_star, five_star, four_star, robot, three_star)

print ("The selected result is ")
print (flag, ' ', result)

