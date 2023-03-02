import browser_cookie3
from http.cookies import SimpleCookie
from minet.web import CookieResolver
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
import sys
from webdriver_manager.chrome import ChromeDriverManager

try:
    jar = getattr(browser_cookie3, "chrome")()
except browser_cookie3.BrowserCookieError:
    print("Could not extract cookies from chrome!")
    sys.exit()

resolver = CookieResolver(jar)

# Insert the wanted FACEBOOK_POST_LINK
cookie = resolver("FACEBOOK_POST_LINK")
facebook_cookie = []
parsed = SimpleCookie(cookie)
for morsel in parsed.values():
    facebook_cookie.append({"name": morsel.key, "value": morsel.coded_value})

options = webdriver.ChromeOptions()
# options.add_argument(r"--user-data-dir=/home/lauramiguel/.config/google-chrome") #e.g. C:\Users\You\AppData\Local\Google\Chrome\User Data
# options.add_argument(r'--profile-directory=Profile 1') #e.g. Profile 3
options.add_argument("--headless")
driver = webdriver.Chrome(service=ChromeService(executable_path=ChromeDriverManager().install()), options=options)
driver.get("https://www.facebook.com")
for cookie in facebook_cookie:
    driver.add_cookie(cookie)

# Insert the wanted FACEBOOK_POST_LINK
driver.get("FACEBOOK_POST_LINK")
driver.save_screenshot("data/facebook.png")
driver.close()

driver.quit()
