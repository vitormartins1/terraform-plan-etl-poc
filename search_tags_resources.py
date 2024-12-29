import json

# Carregar o arquivo JSON contendo o mapeamento (tag_to_resource_map.json)
with open('tag_to_resource_map.json', 'r') as file:
    tag_to_resource_map = json.load(file)

def buscar_tag_para_recurso(recurso):
    """
    Função que busca a tag correspondente a um recurso Terraform, 
    considerando o recurso mais específico primeiro, depois o mais geral.
    """
    # Primeiro, tentamos encontrar a tag para o recurso específico
    for tag, terraform_resource in tag_to_resource_map.items():
        if terraform_resource == recurso:
            return tag
    
    # Se não encontrar para o específico, tentamos para o genérico com "*"
    for tag, terraform_resource in tag_to_resource_map.items():
        if terraform_resource.endswith('*') and recurso.startswith(terraform_resource[:-1]):
            return tag

    # Caso não encontre nenhuma correspondência, retorna None ou uma string vazia
    return None

# Exemplo de uso
recursos_terraform = [
    "aws_api_gateway_rest_api",
    "aws_lambda_function",
    "aws_s3_bucket",
    "aws_instance"
]

# Buscar as tags correspondentes para os recursos fornecidos
resultado = {recurso: buscar_tag_para_recurso(recurso) for recurso in recursos_terraform}

# Exibir o resultado
for recurso, tag in resultado.items():
    print(f"Recurso: {recurso} -> Tag: {tag if tag else 'Nenhuma tag encontrada'}")
