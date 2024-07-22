from parsel import Selector
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import csv

# configure webdriver
options = Options()
options.headless = True  # show GUI
options.add_argument("--window-size=1920,1080")  # set window size to native GUI size
options.add_argument("start-maximized")  # ensure window is full-screen
# configure chrome browser to not load images and javascript
options.add_experimental_option(
    "prefs", {"profile.managed_default_content_settings.images": 2}
)

driver = webdriver.Chrome(options=options)
driver.get("https://www.twitch.tv/directory/game/Art")

# wait for page to load
element = WebDriverWait(driver, timeout=5).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-target=directory-first-item]'))
)

sel = Selector(text=driver.page_source)
parsed = []
for item in sel.xpath("//div[contains(@class,'tw-tower')]/div[@data-target]"):
    parsed.append({
        'title': item.css('h3::text').get(),
        'url': item.css('.tw-link::attr(href)').get(),
        'username': item.css('.tw-link::text').get(),
        'tags': item.css('.tw-tag ::text').getall(),
        'viewers': ''.join(item.css('.tw-media-card-stat::text').re(r'(\d+)')),
    })

# Save parsed data to CSV with UTF-8 encoding
csv_file = 'parsed_data.csv'
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=['title', 'url', 'username', 'tags', 'viewers'])
    writer.writeheader()
    writer.writerows(parsed)

print(f'Data has been saved to {csv_file}')

driver.execute_script("""
let items=document.querySelectorAll('.tw-tower>div');
items[items.length-1].scrollIntoView();
""")

# Find the search box using the updated method
search_box = driver.find_element(By.CSS_SELECTOR, 'input[aria-label="Search Input"]')

# Enter the search term
search_box.send_keys('fast painting')

# Either press the enter key
search_box.send_keys(Keys.ENTER)

# Or click the search button (if necessary)
search_button = driver.find_element(By.CSS_SELECTOR, 'button[icon="NavSearch"]')
search_button.click()

# Keep the browser open for 5 seconds
time.sleep(5)

driver.quit()
