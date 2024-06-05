import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import requests
import os
from dotenv import load_dotenv
import csv


load_dotenv()
HF_TOKEN = os.getenv('HF_TOKEN')
API_URL = "https://api-inference.huggingface.co/models/lxyuan/distilbert-base-multilingual-cased-sentiments-student"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}


def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()


# Input the hashtag to be scraped
str1=input("Enter hashtag to analyze: ")
hashtag='#'+str1

# open browser and load twitter website
chrome_options = Options()
chrome_options.add_experimental_option("detach", True) # keeps the window open after execution
driver = webdriver.Chrome(options=chrome_options)
driver.get('https://twitter.com/i/flow/login')


# enter username
TWITTER_USERNAME = os.getenv('TWITTER_USERNAME')
time.sleep(5)
input_field = driver.find_element(By.CSS_SELECTOR, ".r-30o5oe.r-1dz5y72")
input_field.send_keys(TWITTER_USERNAME)
next_button = driver.find_element(By.XPATH, "//div[@role='button'][contains(.,'Next')]")
next_button.click()
time.sleep(3)


# enter password
TWITTER_PASSWORD = os.getenv('TWITTER_PASSWORD')
password_field = driver.find_element(By.XPATH, "//input[@name='password']")
password_field.send_keys(TWITTER_PASSWORD)
login_button = driver.find_element(By.XPATH, "//div[@role='button'][contains(.,'Log in')]")
login_button.click()
time.sleep(5)
driver.maximize_window()


# enter hashtag
time.sleep(10)
search_field = driver.find_element(By.XPATH, "//input[@placeholder='Search']")
search_field.send_keys(hashtag)
search_field.submit()
time.sleep(5)


tweet_text_content =[]
# scroll the page to load more tweets
for _ in range(5):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)

    # fetch html source code
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, "html.parser")

    # bs4 magic
    articles = soup.find_all('article', {'data-testid':"tweet"})
    for article in articles:
        try:
            text_div = article.find('div', {'data-testid':'tweetText'})
            text = text_div.find('span', class_="css-1qaijid r-bcqeeo r-qvutc0 r-poiln3").get_text()
            tweet_text_content.append(text)
        except:
            pass


output = query({
    "inputs": tweet_text_content,
})
print(output)

master_list=[]
for i in range(len(output)):
    best_score=0
    best_label=''
    for j in range(len(output[i])):
        if output[i][j]['score']>best_score:
            best_score=output[i][j]['score']
            best_label=output[i][j]['label']
    master_list.append([best_label,best_score,tweet_text_content[i].replace("\n", " ")])


# print("Master list:",master_list)       
headers0=['label','score','tweet']          
filename0='reviews.csv'
with open(filename0, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(headers0) # Write headers
    writer.writerows(master_list) # Write multiple rows


positive, negative, neutral = 0, 0, 0
for i in range(len(master_list)):
    if master_list[i][0]=='positive':
        positive+=1
    elif master_list[i][0]=='negative':
        negative+=1
    else:
        neutral+=1


filename1='count.csv'
headers1=['positive_count', 'negative_count', 'neutral_count']
count_list=[str(positive), str(negative), str(neutral)]
print(count_list)
with open(filename1, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(headers1) # Write headers
    writer.writerow(count_list)