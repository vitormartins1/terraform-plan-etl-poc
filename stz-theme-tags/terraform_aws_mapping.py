import json

# Carregar o arquivo theme.json
with open('stz-theme-tags/theme.json', 'r') as file:
    theme_data = json.load(file)

def extract_tags(theme_data):
    # Extrair elementos do arquivo theme.json
    elements = theme_data.get('elements', [])

    # Criar uma lista de tags com placeholders para Terraform types
    tags_with_placeholders = {}

    for element in elements:
        tag = element.get('tag', '')
        # Criar o formato desejado com placeholder para Terraform types
        tags_with_placeholders[tag] = ""

    return tags_with_placeholders

# Extrair as tags
tags_mapping = extract_tags(theme_data)

# Salvar as tags em um novo arquivo JSON
output_file = 'stz-theme-tags/tags_with_placeholders.json'
with open(output_file, 'w') as outfile:
    json.dump(tags_mapping, outfile, indent=4)

print(f"Tags with placeholders saved to {output_file}")
