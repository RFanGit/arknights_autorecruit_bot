import json

# User-defined preferences
primary_target_name = "PhonoR"  # Name of the primary target operator
secondary_target_name = "Vulcan"  # Name of secondary target operator

# New user preferences
target_priority_over_four_star = False  # If True, target operator takes priority over four-star guarantees
stop_on_robot_tag = False  # If True, automatically stops the program when a robot tag is found

# Load recruitment database and verify operator names
recruitment_database_path = "recruitment_database.json"

with open(recruitment_database_path, "r", encoding="utf-8") as db_file:
    recruitment_data = json.load(db_file)

# Check if specified operator names exist in the recruitment database and extract their details
operator_names = [primary_target_name, secondary_target_name]
found_operators = [op for op in recruitment_data if op["name"] in operator_names]

# Extract rarities for targets
primary_target_rarity = None
secondary_target_rarity = None

for operator in found_operators:
    if operator["name"] == primary_target_name:
        primary_target_rarity = operator["rarity"]
    elif operator["name"] == secondary_target_name:
        secondary_target_rarity = operator["rarity"]

print("\nOperator details from recruitment_database.json:")
for operator in found_operators:
    print(f"\nName: {operator['name']}")
    print(f"ID: {operator['id']}")
    print(f"Rarity: {operator['rarity']}")
    print(f"Tags: {', '.join(operator['tags'])}")

# Check if all specified operators were found
found_names = {op["name"] for op in found_operators}
missing_operators = [name for name in operator_names if name not in found_names]
if missing_operators:
    print("\nError: The following specified operators were not found in recruitment_database.json:")
    for name in missing_operators:
        print(f"- {name}")

# Organize the preferences into a dictionary for JSON output
preferences = {
    "primary_target": {
        "name": primary_target_name,
        "rarity": primary_target_rarity,
        "priority_over_four_star": target_priority_over_four_star
    },
    "secondary_target": {
        "name": secondary_target_name,
        "rarity": secondary_target_rarity
    },
    "stop_on_robot_tag": stop_on_robot_tag
}

# Save preferences to JSON file
with open("preferences.json", "w") as json_file:
    json.dump(preferences, json_file, indent=4)
print("Preferences have been successfully saved to preferences.json.")