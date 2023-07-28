from selenium import webdriver
from selenium.webdriver.common.by import By
import string
import time
import json
import os

BASE_URL = "https://www.ines.gov.br/dicionario-de-libras/"

CURRENT_FILE_TARGET =  "metadataClassy.json"

def load_metadata():
    if os.path.exists(CURRENT_FILE_TARGET):
        with open(CURRENT_FILE_TARGET, 'r') as f:
            return json.load(f)
    else:
        return {}

def save_metadata(metadata):
    with open(CURRENT_FILE_TARGET, 'w') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=4)

def get_word_data(driver, letter, metadata):
    # Find the letter element and click it
    letter_element = driver.find_element(By.ID, f'letter-{letter.upper()}')
    letter_element.click()

    # Wait for the page to load after clicking
    time.sleep(0.1)

    select_element = driver.find_element(By.ID, 'input-palavras')
    options = select_element.find_elements(By.TAG_NAME, 'option')

    # Iterate over each word on the page
    for word_element in options[1:]:
        palavra = word_element.text.strip()

        if palavra in metadata:
            print(f"Skipping word {palavra}")
            continue

        print(palavra)  # print the text of the option

        try:
            # Click the word
            word_element.click()

            # Wait for the page to load after clicking
            time.sleep(0.01)

            # Extract the metadata from the word's page
            subjects = driver.find_element(By.ID, 'input-assunto').text.strip()
            meaning = driver.find_element(By.ID, 'input-acepcao').text.strip()
            example = driver.find_element(By.ID, 'input-exemplo').text.strip()
            example_libras = driver.find_element(By.ID, 'input-libras').text.strip()
            classe = driver.find_element(By.ID, 'input-classe').text.strip()

            video_element = driver.find_element(By.ID, 'input-video').find_element(By.TAG_NAME, 'source')
            video_url = video_element.get_attribute('src')

            image_element = driver.find_element(By.ID, 'input-mao').find_element(By.TAG_NAME, 'img')
            image_url = image_element.get_attribute('src')

            metadata[palavra] = {
                'Assuntos': subjects,
                'Acepção': meaning,
                'Classe' : classe,
                'Exemplo': example,
                'ExemploLibras': example_libras,
                'Video': video_url,
                'MaoUrl': image_url,
            }

            print(metadata[palavra])

        except Exception as e:
            print(f"Error processing word {palavra}: {e}")

    return metadata

if __name__ == "__main__":
    # Create a driver
    driver = webdriver.Chrome() # change this to the webdriver you have installed
    driver.get(BASE_URL)

    metadata = load_metadata()

    for letter in string.ascii_lowercase:
        metadata = get_word_data(driver, letter, metadata)
        # Save metadata after each letter
        save_metadata(metadata)

    driver.quit()

    print(metadata)
