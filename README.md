# terraform-plan-etl-poc

Este repositório contém scripts para extrair, classificar e processar recursos de um plano Terraform, além de buscar e mapear tags para recursos específicos. Este projeto é uma prova de conceito que visa viabilizar o desenvolvimento de um ETL para o Terraform plan. Abaixo está a documentação dos principais arquivos e suas funcionalidades.

## Arquivos Principais

### [`extract_plan.py`](extract_plan.py)

Este script é responsável por extrair e classificar recursos de um plano Terraform.

- **Funções Principais:**
  - [`extract_resources(plan_file)`](../../../c:/projects/terraform-plan-etl-poc/extract_plan.py): Extrai e mapeia os recursos do JSON de um plano Terraform.
  - [`classify_resources(resources)`](../../../c:/projects/terraform-plan-etl-poc/extract_plan.py): Classifica os recursos extraídos com base no tipo identificado no "address".
  - [`save_classified_resources_to_file(classified_resources, output_file)`](../../../c:/projects/terraform-plan-etl-poc/extract_plan.py): Salva os recursos classificados em um arquivo JSON.
  - [`extract_references_from_classified(classified_resources)`](../../../c:/projects/terraform-plan-etl-poc/extract_plan.py): Extrai referências e dependências de recursos classificados.
  - [`save_references_to_file(references, output_file)`](../../../c:/projects/terraform-plan-etl-poc/extract_plan.py): Salva as referências extraídas em um arquivo JSON.

### [`fetch_terraform_resources.py`](fetch_terraform_resources.py)

Este script utiliza Selenium para buscar recursos Terraform da documentação oficial e salvar os dados em um arquivo JSON.

- **Funções Principais:**
  - [`fetch_terraform_resources_with_selenium()`](../../../c:/projects/terraform-plan-etl-poc/fetch-terraform-resources/fetch_terraform_resources.py): Configura o WebDriver, acessa a página de documentação, captura os recursos e salva os dados em um arquivo JSON.

### [`search_tags_resources.py`](search_tags_resources.py)

Este script busca tags correspondentes a recursos Terraform a partir de um mapeamento JSON.

- **Funções Principais:**
  - [`buscar_tag_para_recurso(recurso)`](../../../c:/projects/terraform-plan-etl-poc/search_tags_resources.py): Busca a tag correspondente a um recurso Terraform, considerando o recurso mais específico primeiro, depois o mais geral.

### [`terraform_aws_mapping.py`](terraform_aws_mapping.py)

Este script extrai tags de um arquivo `theme.json` e cria um mapeamento com placeholders para tipos Terraform.

- **Funções Principais:**
  - [`extract_tags(theme_data)`](../../../c:/projects/terraform-plan-etl-poc/stz-theme-tags/terraform_aws_mapping.py): Extrai elementos do arquivo `theme.json` e cria uma lista de tags com placeholders para tipos Terraform.

### [`sort_json.py`](sort_json.py)

Este script lê um arquivo JSON, ordena os dados por chave e salva o JSON ordenado em um novo arquivo.

- **Funções Principais:**
  - Leitura do arquivo JSON.
  - Ordenação dos dados por chave.
  - Escrita dos dados ordenados em um novo arquivo JSON.
