import json
import requests
from time import sleep
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

BASE_URL = "http://quotes.toscrape.com"


def selenium_login():

    service = Service("chromedriver.exe")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=chrome")
    with webdriver.Chrome(service=service, options=options) as driver:
        driver.get("https://quotes.toscrape.com/login")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "password"))
        )
        username = driver.find_element(by=By.ID, value="username")
        password = driver.find_element(by=By.ID, value="password")

        username.send_keys("admin")
        password.send_keys("admin")

        button = driver.find_element(
            by=By.XPATH, value="/html//input[@class='btn btn-primary']"
        )
        button.click()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "footer"))
        )
        sleep(1)
        cookies = driver.get_cookies()

    return {cookie["name"]: cookie["value"] for cookie in cookies}


def get_urls(cookies):

    urls = ["/"]
    current_url = "/"
    while True:
        response = requests.get(BASE_URL + current_url, cookies=cookies)
        soup = BeautifulSoup(response.text, "lxml")
        next_link = soup.select_one("li.next > a")
        if next_link:
            current_url = next_link["href"]
            urls.append(current_url)
        else:
            break
    return urls


def spider(url, authors, cookies):

    quotes = []
    response = requests.get(BASE_URL + url, cookies=cookies)
    soup = BeautifulSoup(response.text, "lxml")
    quote_blocks = soup.find_all("div", class_="quote")
    for block in quote_blocks:
        text = block.find("span", class_="text").get_text(strip=True)
        author = block.find("small", class_="author").get_text(strip=True)
        tags = [tag.get_text(strip=True) for tag in block.find_all("a", class_="tag")]
        quotes.append({"quote": text, "author": author, "tags": tags})

        if not any(a["fullname"] == author for a in authors):
            author_link = block.find("a")["href"]
            author_url = BASE_URL + author_link
            author_response = requests.get(author_url, cookies=cookies)
            author_soup = BeautifulSoup(author_response.text, "lxml")
            born_date = author_soup.find("span", class_="author-born-date").get_text(
                strip=True
            )
            born_location = author_soup.find(
                "span", class_="author-born-location"
            ).get_text(strip=True)
            description = author_soup.find("div", class_="author-description").get_text(
                strip=True
            )
            authors.append(
                {
                    "fullname": author,
                    "born_date": born_date,
                    "born_location": born_location,
                    "description": description,
                }
            )
    return quotes


def main(urls, cookies):

    all_quotes = []
    authors = []
    for url in urls:
        all_quotes.extend(spider(url, authors, cookies))
        sleep(1)
    return all_quotes, authors


if __name__ == "__main__":

    session_cookies = selenium_login()
    urls = get_urls(session_cookies)

    quotes_data, authors_data = main(urls, session_cookies)
    print("Scraping completed.")

    with open("qoutes.json", "w", encoding="utf-8") as qf:
        json.dump(quotes_data, qf, ensure_ascii=False, indent=4)
    with open("authors.json", "w", encoding="utf-8") as af:
        json.dump(authors_data, af, ensure_ascii=False, indent=4)
