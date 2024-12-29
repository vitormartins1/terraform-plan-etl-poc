import json

# Read the JSON file
with open('stz-theme-tags/tags_with_placeholders.json', 'r') as file:
    data = json.load(file)

# Sort the JSON data by keys
sorted_data = dict(sorted(data.items()))

# Write the sorted JSON to a new file
with open('stz-theme-tags/sorted_tags_with_placeholders.json', 'w') as file:
    json.dump(sorted_data, file, indent=2)

print("JSON sorted and written to sorted_tags_with_placeholders.json")