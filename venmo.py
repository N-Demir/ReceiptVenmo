import gspread
from oauth2client.service_account import ServiceAccountCredentials
import numpy as np


# use creds to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)

# Find a workbook by name and open the first sheet
# Make sure you use the right name here.
sheet = client.open("Thursday dinner").sheet1
sheet = np.array(sheet.get_all_values())

people_charged = []
charge_totals = []
charge_receipts = []

for name_idx, name in enumerate(sheet[:,0]):
	if name_idx == 0:
		continue

	if name == "":
		break

	receipt_string = ""

	# Add Meals

	seen_blank = False

	for meal_idx, meal in enumerate(sheet[0, :]):
		if meal_idx == 0:
			continue

		if meal == "":
			if seen_blank:
				break
			else:
				seen_blank = True
				continue

		# Check if person needs to be charged
		amount = sheet[name_idx, meal_idx]

		if amount != "":

			amount_string = amount + "(" + meal + ")"

			if receipt_string == "":
				receipt_string += amount_string
			else:
				receipt_string += " + " + amount_string


	# Equals Total
	total = float(sheet[name_idx, -1])
	receipt_string += " = " + str(total)

	# Fire off Venmo charge
	people_charged.append(name)
	charge_totals.append(total)
	charge_receipts.append(receipt_string)



##########
from setup import chromedriver_path, venmo_url, username, password
import os, time, pickle, smtplib
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

PATH = os.path.normpath(chromedriver_path) #Path of ChromeDriver
OPTIONS = webdriver.ChromeOptions()
OPTIONS.add_experimental_option('prefs', {'credentials_enable_service': False}) # Ignore saving password
BROWSER = webdriver.Chrome(executable_path=PATH,chrome_options=OPTIONS) # Create the Chrome browser
BROWSER.get(venmo_url) # Go to Venmo URL to login.

def charge():
    if os.path.isfile('cookies.pkl'):
        cookies = pickle.load(open("cookies.pkl", "rb"))
        for cookie in cookies:
            BROWSER.add_cookie(cookie)
        # Find the Username box and insert username
        username_location = BROWSER.find_element_by_name("phoneEmailUsername")
        username_location.send_keys(username)

        # Find the Password box and insert password
        password_location = BROWSER.find_element_by_name("password")
        password_location.send_keys(password)

        # Login
        send_button = BROWSER.find_element_by_tag_name("form").submit()
        time.sleep(5)
        # Go through each recipient and charge them.
        for person_idx, person in enumerate(people_charged):
            charge = BROWSER.find_element_by_id("onebox_charge_toggle").click() # Select Charge
            # Enter names of people being charged.
            recipient_location = BROWSER.find_element_by_name("onebox_recipient_typeahead")
            recipient_location.send_keys(person + Keys.ENTER)
            time.sleep(2)

            # Enter price and notes.
            note_area = BROWSER.find_element_by_id("onebox_details")
            note_area.send_keys(charge_totals[person_idx] + charge_receipts[person_idx])
            time.sleep(2)

            # Locate the charge button and submit.
            final_submit = BROWSER.find_element_by_xpath("//*[@id=\"onebox_send_button\"]").click()

            time.sleep(15) # Wait  20 seconds before next iteration.

    else: # First time logging in will allow us to gather cookies to reuse in future scheduling tasks.
        print("Please Login for the first time")
        time.sleep(60) # Allow for 60 seconds to login and do 2 step verification.
        pickle.dump(BROWSER.get_cookies(), open("cookies.pkl", "wb"))



charge()


#######
from setup import chromedriver_path, venmo_url, username, password
from selenium.webdriver import Chrome
from selenium.webdriver.common.keys import Keys
import cPickle as pickle
import SendKeys
import time
import datetime
import os

CHROME_DRIVER_PATH = chromedriver_path
VENMO_URL = venmo_url

browser = Chrome(CHROME_DRIVER_PATH)
browser.get(VENMO_URL)

if os.path.isfile('cookies.pkl'):
    # there is a cookie file

    cookies = pickle.load(open("cookies.pkl", "rb"))
    for cookie in cookies:
        browser.add_cookie(cookie)

    # click on the sign in link
    signin_link = browser.find_element_by_link_text("Sign in")
    signin_link.click()

    # enter the email and password and send it
    username_box = browser.find_element_by_class_name("email-username-phone")
    username_box.send_keys(username)
    password_box = browser.find_element_by_class_name("password")
    password_box.send_keys(password)
    send_button = browser.find_element_by_class_name("login")
    send_button.click()

    # enter the person's name you want to pay
    time.sleep(5)
    name_box = browser.find_element_by_class_name("onebox_prefill")
    name_box.click()
    name_text_box = browser.find_element_by_class_name("paddingUnifier")
    name_text_box.send_keys(venmoInfo.payee_name)
    name_text_box.send_keys(Keys.ENTER)
    payment_box = browser.find_element_by_class_name("mainTextBox")
    time.sleep(1)
    payment_box.click()
    datetime_now = datetime.datetime.now()
    SendKeys.SendKeys(venmoInfo.amount + venmoInfo.description, with_spaces=True)
    # click the pay button
    pay_button = browser.find_element_by_id("onebox_pay_toggle")
    pay_button.click()
    name_text_box = browser.find_element_by_class_name("paddingUnifier")
    name_text_box.send_keys(venmoInfo.payee_name)

    # click the send button
    send_button = browser.find_element_by_id("onebox_send_button")
    send_button.click()

else:
    # click on the sign in link
    signin_link = browser.find_element_by_link_text("Sign in")
    signin_link.click()
    print("Couldn't find the cookie file, you will need two factor authorization and then cookie will be saved")
    # wait a while until the user fully signs in
    time.sleep(60)
    # Save the cookies
    pickle.dump(browser.get_cookies(), open("cookies.pkl", "wb"))

time.sleep(10)


		

