import json
from collections import defaultdict

def extract_resources(plan_file):
    """
    Extrai e mapeia os recursos do JSON de um plano Terraform focando nas seções especificadas.

    Args:
        plan_file (str): Caminho para o arquivo JSON do plano Terraform.

    Returns:
        dict: Dicionário com os recursos extraídos e mapeados por "address".
    """
    def extract_from_module(module_data, mapped_resources, hierarchy_prefix=""):
        """
        Extrai recursos de um módulo e submódulos recursivamente.

        Args:
            module_data (dict): Dados do módulo.
            mapped_resources (dict): Dicionário para armazenar os recursos mapeados.
            hierarchy_prefix (str): Prefixo hierárquico para recursos em submódulos.
        """
        # Extrair recursos no nível atual do módulo
        resources = module_data.get("resources", [])
        for resource in resources:
            address = resource.get("address")
            if address:
                resource_type = address.split(".")[0]
                # Ignorar tipos não desejados
                if resource_type not in ["data", "null_resource", "local_file"]:
                    full_address = f"{hierarchy_prefix}{address}"
                    mapped_resources[full_address] = resource

        # Verificar submódulos dentro de "child_modules"
        child_modules = module_data.get("child_modules", [])
        for child_module in child_modules:
            extract_from_module(child_module, mapped_resources, hierarchy_prefix)

    with open(plan_file, 'r') as file:
        plan_data = json.load(file)

    mapped_resources = {}

    # Extração de "configuration.root_module.resources"
    root_module = plan_data.get("configuration", {}).get("root_module", {})
    extract_from_module(root_module, mapped_resources)

    # Extração de "configuration.module_calls" e seus submódulos
    module_calls = root_module.get("module_calls", {})
    for module_name, module_data in module_calls.items():
        module = module_data.get("module", {})
        module_hierarchy_prefix = f"module.{module_name}."
        extract_from_module(module, mapped_resources, module_hierarchy_prefix)

    return mapped_resources

def classify_resources(resources):
    """
    Classifica os recursos extraídos com base no tipo identificado no "address".

    Args:
        resources (dict): Dicionário de recursos extraídos mapeados por "address".

    Returns:
        dict: Dicionário com listas de recursos classificados por tipo.
    """
    classified_resources = defaultdict(list)

    for address, resource in resources.items():
        # Determinar o tipo principal do recurso a partir do "address"
        if address.startswith("module."):
            # Recurso dentro de um módulo
            parts = address.split(".")
            module_hierarchy = ".".join(parts[:-2])  # Manter a hierarquia até o módulo
            resource_type = parts[-2]  # Tipo do recurso
            classified_resources[f"{module_hierarchy}.{resource_type}"].append(resource)
        else:
            # Recurso na raiz
            resource_type = address.split(".")[0]
            classified_resources[resource_type].append(resource)

    return classified_resources

def save_classified_resources_to_file(classified_resources, output_file):
    """
    Salva os recursos classificados em um arquivo JSON.

    Args:
        classified_resources (dict): Dicionário de recursos classificados.
        output_file (str): Caminho para o arquivo JSON de saída.
    """
    with open(output_file, 'w') as file:
        json.dump(classified_resources, file, indent=2)

def extract_references_from_classified(classified_resources):
    """
    Extrai referências e dependências de recursos classificados.

    Args:
        classified_resources (dict): Dicionário de recursos classificados.

    Returns:
        list: Lista de objetos representando referências e dependências entre recursos.
    """
    def is_valid_reference(reference):
        """
        Verifica se a referência é válida, ignorando prefixos indesejados.

        Args:
            reference (str): A referência a ser verificada.

        Returns:
            bool: True se a referência for válida, False caso contrário.
        """
        invalid_prefixes = ["var", "path", "count", "data", "null_resource", "each", "local", "local_file"]
        return not any(reference.startswith(prefix) for prefix in invalid_prefixes)

    def get_base_reference(reference):
        """
        Obtém a base de uma referência, removendo índices e atributos adicionais.

        Args:
            reference (str): A referência original.

        Returns:
            str: A base da referência.
        """
        return reference.split("[")[0].split(".")[0]

    references_by_from = defaultdict(set)

    for resource_type, resources in classified_resources.items():
        for resource in resources:
            address = resource.get("address")

            # Processa references em expressions
            expressions = resource.get("expressions", {})
            for expr_name, expr_data in expressions.items():
                if isinstance(expr_data, dict):
                    for ref in expr_data.get("references", []):
                        if is_valid_reference(ref):
                            references_by_from[address].add((ref, "reference"))

            # Processa depends_on
            for dependency in resource.get("depends_on", []):
                if is_valid_reference(dependency):
                    references_by_from[address].add((dependency, "depends_on"))

    # Filtrar e priorizar referências menos específicas, com prioridade para depends_on
    filtered_references = []
    for from_address, refs in references_by_from.items():
        grouped_refs = defaultdict(list)
        for ref, ref_type in refs:
            base_ref = get_base_reference(ref)
            grouped_refs[base_ref].append((ref, ref_type))

        for base_ref, ref_list in grouped_refs.items():
            # Escolher a referência menos específica dentro do grupo, priorizando depends_on
            sorted_refs = sorted(ref_list, key=lambda x: (x[1] != "depends_on", x[0].count(".")))
            chosen_ref = sorted_refs[0]
            filtered_references.append({
                "from": from_address,
                "to": chosen_ref[0],
                "type": chosen_ref[1]
            })

    return filtered_references

def save_references_to_file(references, output_file):
    """
    Salva as referências extraídas em um arquivo JSON.

    Args:
        references (list): Lista de referências extraídas.
        output_file (str): Caminho para o arquivo JSON de saída.
    """
    with open(output_file, 'w') as file:
        json.dump(references, file, indent=2)

if __name__ == "__main__":
    # Caminho para o arquivo JSON do plano Terraform
    plan_file_path = "terraform_plan.json"

    # Caminho para o arquivo de saída de recursos classificados
    output_file_path = "classified_resources.json"

    # Caminho para o arquivo de saída de relacionamentos
    relationships_file_path = "resource_relationships.json"

    # Extrai os recursos e os mapeia
    resources = extract_resources(plan_file_path)

    # Classifica os recursos
    classified_resources = classify_resources(resources)

    # Salva os recursos classificados em um arquivo JSON
    save_classified_resources_to_file(classified_resources, output_file_path)

    # Extrai as referências dos recursos classificados
    references = extract_references_from_classified(classified_resources)

    # Salva as referências em um arquivo JSON
    save_references_to_file(references, relationships_file_path)

    # Exibe a contagem total de recursos e mensagem de conclusão
    print(f"Total de recursos extraídos: {len(resources)}")
    print(f"Recursos classificados salvos em: {output_file_path}")

    # Exibe o número total de referências extraídas
    print(f"Total de referências extraídas: {len(references)}")
    print(f"Referências salvas em: {relationships_file_path}")
