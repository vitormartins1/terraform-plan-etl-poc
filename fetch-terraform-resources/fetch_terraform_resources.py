from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import json
import os
import time

def fetch_terraform_resources_with_selenium():
    # Configurar o WebDriver
    edge_options = Options()
    edge_options.add_argument("--headless")
    edge_options.add_argument("--disable-gpu")
    edge_options.add_argument("--no-sandbox")
    service = Service(EdgeChromiumDriverManager().install())

    driver = webdriver.Edge(service=service, options=edge_options)

    # Acessar a página
    url = "https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources"
    driver.get(url)

    # Salvar o HTML para depuração
    with open("debug_page_source.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("Saved debug_page_source.html")

    # Fechar banners de consentimento ou elementos sobrepostos
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "consent-banner"))
        )
        consent_close_button = driver.find_element(By.TAG_NAME, "button")
        if consent_close_button:
            consent_close_button.click()
            time.sleep(1)
    except Exception as e:
        print("No consent banner found or could not close it:", e)

    # Esperar até que a página carregue completamente
    try:
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, "provider-docs-menu-content")))
    except Exception as e:
        print(f"Error: {e}")
        driver.quit()
        return {}

    # Capturar serviços na barra lateral
    services = driver.find_elements(By.CSS_SELECTOR, ".menu-list-category > .menu-list-category-link")

    # Verificar se existe progresso salvo
    mapping = {}
    progress_file = "fetch-terraform-resources/progress.json"
    if os.path.exists(progress_file):
        with open(progress_file, "r") as file:
            mapping = json.load(file)
        print("Resuming from saved progress...")

    # Conjunto global de URLs para garantir que não sejam repetidas
    global_resource_urls = set()

    # Iterar sobre os serviços
    for service in services:
        try:
            # Captura o nome do serviço
            service_name = service.find_element(By.CSS_SELECTOR, ".menu-list-category-link-title").text.strip()

            # Se o serviço já foi processado, pular
            if service_name in mapping:
                print(f"Skipping already processed service: {service_name}")
                continue

            print(f"Processing service: {service_name}")

            # Scroll para tornar o elemento visível antes de clicar
            driver.execute_script("arguments[0].scrollIntoView(true);", service)
            time.sleep(1)
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(service)).click()
            time.sleep(2)

            # Inicializar os dados dos recursos para o serviço atual
            resource_data = {}

            # Usar um set para garantir que os recursos sejam únicos para o serviço
            captured_resources = set()

            # Tentar capturar os links de recursos para este serviço
            try:
                # Verificar se a seção "Resources" aparece de uma maneira mais geral
                resources_section = driver.find_elements(By.XPATH, "//span[text()='Resources']/ancestor::li[1]//ul/li/a")
                if resources_section:
                    for resource in resources_section:
                        resource_name = resource.text.strip()
                        resource_link = resource.get_attribute("href")

                        # Adicionar o recurso ao dicionário se não for duplicado
                        if resource_link not in captured_resources and resource_link not in global_resource_urls:
                            resource_data[resource_name] = resource_link
                            captured_resources.add(resource_link)
                            global_resource_urls.add(resource_link)
                            print(f"Captured: {resource_name} -> {resource_link}")
                else:
                    print(f"No resources found for {service_name}. Skipping.")
            except Exception as e:
                print(f"Error locating resources section for {service_name}: {e}")
                continue

            # Fechar o menu de recursos após captura
            try:
                # Usar execute_script para alternar o ícone
                driver.execute_script("""
                    var menuIcon = document.querySelector("i.fa-angle-down");
                    if(menuIcon) {
                        menuIcon.click();  // Alternar o menu para fechado
                    }
                """)
                time.sleep(1)
                print(f"Closed resources menu for {service_name}")
            except Exception as e:
                print(f"Error closing resources menu for {service_name}: {e}")

            # Se encontrar recursos, adicionar ao mapeamento
            if resource_data:
                mapping[service_name] = resource_data  # Atualiza o mapeamento com dados atuais

                # Salvar o progresso após o processamento de cada serviço no arquivo
                with open(progress_file, "w") as file:
                    json.dump(mapping, file, indent=4)

        except Exception as e:
            print(f"Error processing service {service_name}: {e}")
            continue

    driver.quit()

    # Salvar o resultado final em um arquivo JSON
    with open("fetch-terraform-resources/terraform_resources.json", "w") as file:
        json.dump(mapping, file, indent=4)

    print("Terraform resources saved to terraform_resources.json")

# Executar a função
fetch_terraform_resources_with_selenium()
