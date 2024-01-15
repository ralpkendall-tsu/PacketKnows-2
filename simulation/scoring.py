
def getPoints(userConfig, correctConfig):

    total_points = calculate_points(userConfig, correctConfig)

    # Print the total points
    return {"Total Points:": total_points}

def calculate_points(user, correct):
    # Define points and categories as dictionaries
    points = {
        "name": 2,
        "hostname": 2,
        "ip address": 5,
        "subnet mask": 3,
        "default gateway": 2,
        "shutdown": 1,
        "links": 2,
        "acl":2,
        "protocol":5, # Routing protocol
        "process id": 2,
        "ip domain-name lookup":1,
        "exec timeout":1,
        "login": 1,
        "service password-encryption":1,
        "banner motd": 1,
        "enable secret": 1,
        "static_nat":5,
        "interfaces":3,
        "static routes":5,
        "vlan":5
    }

    categories = {
        "physical": ["links"],
        "basic configuration": ["hostname", "name", "exec timeout", "login", "service password-encryption", "banner motd", "enable secret"],
        "ip": ["ip address", "subnet mask", "default gateway", "shutdown"],
        "routing": ["acl", "protocol", "process id", 'static_nat', 'interfaces', 'static routes'],
        "other": ["ip domain-name lookup", 'vlan']
    }
    
    # Initialize a dictionary to store points for each category
    total_points = {category: 0 for category in categories.keys()}

    for key, value in correct.items():
        if key == "links":
            # Handle the "links" key
            if isinstance(value, list) and isinstance(user.get(key), list):
                for link in value:
                    if link in user[key]:
                        total_points["physical"] += points.get(key, 0)
        elif key == "acl":
            for aclConfig in value:
                # numbered acl
                if aclConfig == "numbered acl" and aclConfig in user[key]:
                    for line in value.get(aclConfig):
                        if line in user[key].get(aclConfig):
                            total_points["routing"] += points.get("acl", 0)
                # named acl
                elif aclConfig in user[key]:
                    for config in value.get(aclConfig):
                        if config in user[key].get(aclConfig):
                            total_points["routing"] += points.get("acl", 0)
        elif isinstance(value, dict):
            if key in user:
                category = get_category(key, categories)
                nested_points = calculate_points(user[key], value)
                for category_key, category_points in nested_points.items():
                    total_points[category_key] += category_points
        elif key in user and user[key] == value:
            if key in points:
                category = get_category(key, categories)
                total_points[category] += points.get(key, 0)

    return total_points

def get_category(key, categories):
    # Determine the category for a given key based on the categories dictionary
    for category, keys in categories.items():
        if key in keys:
            return category
    return "other"  # Default to "other" if key is not found in any category

