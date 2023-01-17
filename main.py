import requests
from bs4 import BeautifulSoup
import smtplib as sm
from dotenv import load_dotenv
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

MY_GMAIL = os.getenv("MY_GMAIL")
PASSWORD = os.getenv("PASSWORD")
GMAIL_PORT = int(os.getenv("PORT"))
PRODUCT_LINK = os.getenv("LINK")
WEB_DRIVER_PATH = os.getenv("DRIVER_PATH")

# Setting up web driver to use
options = webdriver.ChromeOptions()
options.add_argument("start-maximized")
options.add_argument("disable-infobars")

chrome_driver_path = Service(rf"{WEB_DRIVER_PATH}")
driver = webdriver.Chrome(options=options,service=chrome_driver_path)

driver.get("https://camelcamelcamel.com/")

################### At camelcamelcamel using search bar #######################

search_bar = driver.find_element(By.CLASS_NAME, "input-group-field")
search_bar.send_keys(f"{PRODUCT_LINK}")
time.sleep(1)
search_bar.send_keys(Keys.ENTER)
time.sleep(2)

product_avg_price = float(driver.find_element(By.XPATH, '//*[@id="histories"]/div[1]/div/div[2]/div/div/'
                                                  'table/tbody/tr[4]/td[2]').text.split("$")[1])
product_low_price = float(driver.find_element(By.XPATH, '//*[@id="histories"]/div[1]/div/div[2]/div/div/'
                                                        'table/tbody/tr[3]/td[2]').text.split("$")[1])
# print(product_avg_price)

## Variables used for testing
# product_price_placeholder = float(39.95)
# below_price = float(70.00)

########## Amazon scraping ###########

headers = {
    "User-Agent": "Defined",
    "Accept-Language": "en-US,en;q=0.5"
}

response = requests.get(PRODUCT_LINK, headers=headers)
response.raise_for_status()
soup_me = response.text

soup = BeautifulSoup(soup_me, "html.parser")

get_product_price = soup.find(name="span", class_="a-offscreen")
product_price = float(get_product_price.getText().split("$")[1])
# print(product_price)

get_product_name = soup.find(name="span", class_="product-title-word-break")
product_name = get_product_name.getText().strip()

# message = f"{product_name} IS NOW ${product_price}.\n{PRODUCT_LINK}"
message = f"Subject: Amazon Price Drop\n\n{product_name} IS NOW ${product_price}. " \
          f"It's lowest price is: {product_low_price}\n\n{PRODUCT_LINK}"

########## Gmail messaging if price is below set goal ###########
# if product_price_placeholder < below_price:
if product_price < product_avg_price:
    with sm.SMTP("smtp.gmail.com", GMAIL_PORT) as connection:
        connection.starttls()
        connection.login(user=MY_GMAIL, password=PASSWORD)
        connection.sendmail(from_addr=MY_GMAIL, to_addrs=MY_GMAIL, msg=message.encode("utf8"))
else:
    print(f"{product_name}\n is NOT on sale 😢. Its current price is: {product_price} lowest price is: {product_low_price}.")


