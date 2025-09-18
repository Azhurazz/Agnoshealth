from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import requests
import json
from bs4 import BeautifulSoup
import pandas as pd

driver = webdriver.Chrome()
driver.get("https://www.agnoshealth.com/forums/search")

def wait_until_all_cards_loaded(driver, timeout=30, check_interval=1):
    """
    Wait until the number of <article> elements stops changing
    within the given timeout.
    """
    end_time = time.time() + timeout
    prev_count = -1
    
    while time.time() < end_time:
        cards = driver.find_elements(By.TAG_NAME, "article")
        curr_count = len(cards)
        
        if curr_count == prev_count:
            return cards
        
        prev_count = curr_count
        time.sleep(check_interval)
    
    return driver.find_elements(By.TAG_NAME, "article")

data = []
page = 1

while True:
    print(f"Scraping page {page}...")
    
    # Wait until all cards are loaded
    cards = wait_until_all_cards_loaded(driver, timeout=60, check_interval=10) # timeout=60s, check every 10s
    if not cards:
        print("⚠️ No cards found on this page, stopping.")
        break

    # Extract each card
    for card in cards:
        try:
            gender_age_text = card.find_element(By.CSS_SELECTOR, "p.text-sm.text-gray-500").text
        except:
            gender_age_text = None

        gender, age = None, None
        if gender_age_text:
            parts = gender_age_text.split("|")
            if len(parts) >= 2:
                gender = parts[0].strip()
                age_match = re.search(r"อายุ\s*(\d+)", parts[1])
                if age_match:
                    age = int(age_match.group(1))

        try:
            title = card.find_element(By.CSS_SELECTOR, "p.font-bold").text
        except:
            title = None
        try:
            date = card.find_element(By.TAG_NAME, "time").text
        except:
            date = None
        try:
            badges = [b.text for b in card.find_elements(By.CSS_SELECTOR, "ul li")]
        except:
            badges = []
        try:
            detail = card.find_element(By.CSS_SELECTOR, "p.text-sm.text-gray-500.line-clamp-3").text
        except:
            detail = None

        data.append({
            "gender": gender,
            "age": age,
            "title": title,
            "date": date,
            "symptom_badge": ", ".join(badges),
            "detail_symptom": detail
        })

    # Check if page returned no useful data (safety break)
    if len(data) == 0 or all(v is None for v in data[-len(cards):][0].values()):
        print(f"⚠️ Page {page} returned empty data. Stopping.")
        break

    # Try to click "Next Page"
    try:
        next_btn = driver.find_element(By.CSS_SELECTOR, "button.bg-primary_blue-500")
        driver.execute_script("arguments[0].click();", next_btn)
        page += 1
        time.sleep(3)
    except:
        print("Last page reached.")
        break

driver.quit()

# Save to CSV
df = pd.DataFrame(data)
df.to_csv("agnos_forums.csv", index=False, encoding="utf-8-sig")

print("Saved", len(df), "records.")

# Save to JSON
import json
with open("agnos_forums.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Saved", len(df), "records to CSV and JSON.")