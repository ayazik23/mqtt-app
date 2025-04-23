from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests
import webbrowser
import os

def configure_webdriver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--disable-notifications')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36')

    try:
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    except Exception:
        try:
            driver_path = "./chromedriver"
            os.environ["webdriver.chrome.driver"] = driver_path
            return webdriver.Chrome(service=Service(driver_path), options=options)
        except Exception as error:
            print("Driver initialization failed:", error)
            return None

def create_fallback_result(query, url):
    return {
        'name': query,
        'description': f"No detailed data found for '{query}'",
        'url_content': url,
        'clothing': '',
        'shoes': ''
    }

def search_asos_fallback(query):
    print("Fallback to requests/BeautifulSoup for ASOS search")
    query_encoded = query.replace(' ', '+')
    search_url = f"https://www.asos.com/search/?q={query_encoded}"

    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept-Language': 'en-US,en;q=0.9'
    }

    try:
        res = requests.get(search_url, headers=headers)
        if res.status_code != 200:
            return create_fallback_result(query, search_url)

        soup = BeautifulSoup(res.text, 'html.parser')
        product = soup.select_one('article._2qG85dG')
        if not product:
            return create_fallback_result(query, search_url)

        name = product.select_one('p._3x-5VWa')
        image = product.select_one('img._2r7rDJP')
        link = product.find('a', href=True)
        product_url = f"https://www.asos.com{link['href']}" if link else search_url
        webbrowser.open(product_url)

        return {
            'name': name.text.strip() if name else query,
            'description': f"ASOS listing for {query}",
            'url_content': product_url,
            'image': image['src'] if image and 'src' in image.attrs else '',
            'gender': ''
        }
    except Exception as err:
        print("Error during fallback search:", err)
        return create_fallback_result(query, search_url)

def search_product(query):
    print(f"Initiating ASOS search for: {query}")
    return search_asos_fallback(query)
