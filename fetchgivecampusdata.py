from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
import os
import glob

import settings 

#erase old files
for fl in glob.glob(settings.download_dir+"\\GiveCampus*.csv"):
         os.remove(fl)

chrome_options = Options()  
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--headless")  
chrome_options.add_argument("--window-size=%s" % settings.WINDOW_SIZE)
chrome_options.add_experimental_option('prefs', {
    'credentials_enable_service': False,
    'download.prompt_for_download': False,
    'download.directory_upgrade': True,
    'download.default_directory': 'd:\Downloads',
    'safebrowsing.enabled': False,
    'safebrowsing.disable_download_protection': True,
    'profile': {
        'password_manager_enabled': False,
        'default_content_settings.popups': False
    }
})
chrome_options.binary_location = settings.CHROME_PATH

driver = webdriver.Chrome(executable_path=settings.CHROMEDRIVER_PATH,
                          chrome_options=chrome_options
                         )  

# Hack to get around Headless Chrome not allowing downloads. 
# SEE  https://stackoverflow.com/questions/45219676/selenium-chrome-headless-download-file
# AND  https://github.com/shawnbutton/PythonHeadlessChrome
driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': settings.download_dir}}
command_result = driver.execute("send_command", params)

 
#open GiveCampus 
#open login page
driver.get("https://www.givecampus.com/login")
assert "GiveCampus" in driver.title
elem = driver.find_element_by_xpath("//input[@id='user_email']")
elem.send_keys(settings.user)
elem = driver.find_element_by_xpath("//input[@id='user_password']")
elem.send_keys(settings.pwd)
elem = driver.find_element_by_xpath("//input[@type='submit']")
elem.click()
 
# check if on main admin page
assert "Admin" in driver.title
#  OPTIONALLY grap a screen grab, just to make sure you are on the right page, but since you are headless, you cannot see... but want to
driver.get_screenshot_as_file("capture.png")

driver.get("https://www.givecampus.com/schools/MacalesterCollege/admin/reporting")

#select the preceding year
elem = driver.find_element_by_id("start_date_1i").send_keys(Keys.ARROW_UP)
 
#click download
elem = driver.find_element_by_xpath("//input[@value='Download Donation Report']")
elem.click()
 
#keep the browser open to accomodate for some delay
time.sleep(2) # second
#driver.close()

#rename file  LINUX STYLE
for fl in glob.glob(settings.download_dir+"\\GiveCampus*.csv"):
         os.rename(fl,settings.download_dir+"\\GiveCampus.csv")



############# LLOYD UPLOAD PART

driver.get("https://advancement.macalester.edu/M/Gifts/Loader/")
driver.find_element_by_xpath("//input[@id='ctl00_MainContent_txtUsername']").send_keys(settings.matrix_user)
driver.find_element_by_xpath("//input[@id='ctl00_MainContent_txtPassword']").send_keys(settings.matrix_password)
driver.find_element_by_id("ctl00_MainContent_btnSubmit").click()
driver.get("https://advancement.macalester.edu/M/Gifts/Loader/GiveCampus.aspx")
driver.find_element_by_id("ctl00_MainContent_uxFileUpload").send_keys(settings.download_dir+"\\GiveCampus.csv")
driver.find_element_by_id("ctl00_MainContent_uxFileUploadButton").click()
driver.close()
