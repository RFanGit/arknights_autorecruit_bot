import re
import json

# Load JSON data
with open("character_table.json", "r", encoding="utf-8") as f:
    character_table = json.load(f)

with open("gacha_table.json", "r", encoding="utf-8") as f:
    gacha_table = json.load(f)

# Recruitment overrides
recruitable_name_to_id_override = {"Justice Knight": "char_4000_jnight"}
name_overrides = {"THRM-EX": "Thermal-EX", "Justice Knight": "'Justice Knight'"}
recruit_detail = gacha_table.get("recruitDetail", "")

def profession_to_class(profession):
    mapping = {
        "PIONEER": "Vanguard", "WARRIOR": "Guard", "SPECIAL": "Specialist",
        "TANK": "Defender", "SUPPORT": "Supporter"
    }
    return mapping.get(profession, profession.title())

# Recruitment calculation
def parse_recruitable_operators():
    rarity_mapping = {1: 1, 3: 2, 6: 3, 10: 4, 15: 5, 21: 6}
    operator_name_to_id = {
        op_data["name"]: op_id
        for op_id, op_data in character_table.items()
        if not op_id.startswith("trap")
    }
    recruitment_strings = recruit_detail.split("★")
    recruitable_operators = [
        line.replace("\n", "").split(" / ")
        for line in recruitment_strings[1:]
    ]
    recruitment = []
    for r, op_names in enumerate(recruitable_operators):
        print(op_names)
        for op_name in op_names:
            # Remove any text within <...> tags
            clean_name = re.sub(r"<[^>]*>", "", op_name).strip().rstrip("-")
            op_id = recruitable_name_to_id_override.get(clean_name) or operator_name_to_id.get(clean_name)
            
            if not op_id:
                continue
            
            op_data = character_table[op_id]
            rarity = rarity_mapping.get(r + 1, r + 1)
            tags = op_data.get("tagList", []) + [
                op_data.get("position", "").title(),
                profession_to_class(op_data.get("profession", ""))
            ]
            if rarity == 1:
                tags.append("Robot")
            elif rarity == 6:
                tags.append("Top Operator")
            if rarity >= 5:
                tags.append("Senior Operator")

            recruitment.append({
                "id": op_id,
                "name": name_overrides.get(clean_name, clean_name),
                "rarity": rarity,
                "tags": tags
            })
    
    # Additional recruitment entries
    recruitment.extend([
        {
            'id': 'char_423_blemsh',
            'name': 'Blemishine',
            'rarity': 6,
            'tags': ['Melee', 'Defender', 'Defense', 'Healing', 'DPS']
        },
        {
            'id': 'char_4136_phonor',
            'name': 'Aosta',
            'rarity': 5, 
            'tags': ['Ranged', 'AoE', 'Sniper']
        },
        {
            'id': 'char_4136_phonor',
            'name': 'Bubble',
            'rarity': 4,
            'tags': ['Defender', 'Melee', 'Defense']
        },
        {
            'id': 'char_4136_phonor',
            'name': 'PhonoR',
            'rarity': 1,
            'tags': ['Support', 'Robot', 'Ranged', 'Elemental', 'Supporter']
        }
    ])

    return recruitment

# Generate JSON file
def generate_recruitment_json(output_file="recruitment_database.json"):
    recruitment_data = parse_recruitable_operators()
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(recruitment_data, f, ensure_ascii=False, indent=4)
    print(f"Recruitment database saved to {output_file}")

# Run the generation process
generate_recruitment_json()