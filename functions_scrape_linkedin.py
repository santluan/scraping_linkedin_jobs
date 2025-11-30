import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from unidecode import unidecode
import re

def get_job_description(job_id):
    
    JOB_URL = "https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

    target_url = JOB_URL.format(job_id)
    try:
        response = requests.get(target_url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            
            # The description is usually in a div with this specific class
            description_box = soup.find("div", class_="show-more-less-html__markup")
            
            if description_box:
                return description_box.get_text(strip=True)
            else:
                return "Description not found"
        else:
            return f"Error: Status {response.status_code}"
    except Exception as e:
        return f"Error: {e}"

def categorize(nivel):

    # Niveis
    estagio = ['estagio', 'estagiario', 'intern', 'internship']
    junior = ['junior', 'jr']
    pleno = ['pleno', 'pl', 'mid']
    senior = ['senior', 'sr']
    especialista = ['especialista', 'specialist']

    # tratamento de dados
    nivel.lower()
    nivel.replace('iii','sr')
    nivel.replace('ii','pl')
    unidecode(string=nivel)

    # Atribuindo o nível a vaga
    if any(re.search(pattern, nivel, re.IGNORECASE) for pattern in estagio):
        return "Estágio"
    elif any(re.search(pattern, nivel, re.IGNORECASE) for pattern in junior):
        return "Junior"
    elif any(re.search(pattern, nivel, re.IGNORECASE) for pattern in pleno):
        return "Pleno"
    elif any(re.search(pattern, nivel, re.IGNORECASE) for pattern in senior):
        return "Senior"
    elif any(re.search(pattern, nivel, re.IGNORECASE) for pattern in especialista):
        return "Especialista"
    else:
        return "Outros"


def scrape_linkedin_jobs(keyword, location, start_page, end_page):

    job_list = []

    SEARCH_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    
    print(f"Starting scrape Linkedin Jobs for {keyword} in {location}")

    for page in range(start_page, end_page+1):
        start_offset = page * 25
        params = {
            "keywords": keyword,
            "location": location,
            "start": start_offset
        }

        try:
            response = requests.get(SEARCH_URL, params=params, headers=headers)
            
            if response.status_code != 200:
                print(f"Scrape failed for page {page+1}. Status code:{response.status_code}")
                break

            soup = BeautifulSoup(response.text, "html.parser")
            job_cards = soup.find_all("li")
            
            for card in job_cards:
                title_tag = card.find("h3", class_="base-search-card__title")
                company_tag = card.find("h4", class_="base-search-card__subtitle")
                location_tag = card.find("span", class_="job-search-card__location")
                date_tag = card.find("time", class_="job-search-card__listdate")
                link_tag = card.find("a", class_="base-card__full-link")
                jobid_tag = card.find("div", class_="base-card")
                id = jobid_tag['data-entity-urn'].split(":")[-1]

                job_data = {
                    "Title": title_tag.text.strip() if title_tag else "NA",
                    "Company": company_tag.text.strip() if company_tag else "NA",
                    "Location": location_tag.text.strip() if location_tag else "NA",
                    "Date_Posted": date_tag['datetime'] if date_tag else "NA",
                    "Description": get_job_description(id),
                    "Link": link_tag['href'] if link_tag else "NA",
                    "Level": categorize(title_tag.text.strip()) if title_tag else "NA"
                }
                
                job_list.append(job_data)

                
            
            print(f"Page {page} complete. Total jobs: {len(job_list)}")
            time.sleep(random.uniform(2, 5))

        except Exception as e:
            return print(f"Error: {e}")
    
    return pd.DataFrame(job_list)  


