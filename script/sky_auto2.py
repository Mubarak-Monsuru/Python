from playwright.sync_api import sync_playwright
from datetime import datetime
import time
import re
import pyperclip
import imaplib
import email

# Email credentials
EMAIL_ACCOUNT = "skytrade.ui.test@gmail.com"
APP_PWD = "pmsw mkpn hhlv dygc"
EMAIL_FOLDER = "inbox"

def extract_verification_code(subject):
    """Extract a 6-digit verification code from the email subject."""
    match = re.search(r'\b\d{6}\b', subject)
    if match:
        return match.group(0)
    else:
        return None

def read_verification_email():
    # Connect to the Gmail IMAP server
    M = imaplib.IMAP4_SSL('imap.gmail.com')
    M.login(EMAIL_ACCOUNT, APP_PWD)
    M.select(EMAIL_FOLDER)

    # Search for all emails in the folder
    rv, data = M.search(None, "ALL")
    if rv != 'OK':
        print("No messages found!")
        return None

    # Fetch the latest email
    latest_email_id = data[0].split()[-1]
    rv, data = M.fetch(latest_email_id, '(RFC822)')
    if rv != 'OK':
        print("ERROR getting message", latest_email_id)
        return None

    # Extract the email content
    msg = email.message_from_bytes(data[0][1])
    email_subject = msg['Subject']
    email_body = ""

    # If the email is multipart, get the text part
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                try:
                    email_body = part.get_payload(decode=True).decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        email_body = part.get_payload(decode=True).decode('latin-1')
                    except UnicodeDecodeError:
                        print("Unable to decode email content")
                        return None
                break
    else:
        try:
            email_body = msg.get_payload(decode=True).decode('utf-8')
        except UnicodeDecodeError:
            try:
                email_body = msg.get_payload(decode=True).decode('latin-1')
            except UnicodeDecodeError:
                print("Unable to decode email content")
                return None

    M.logout()

    # Print the email subject and body
    print(f"Email Subject: {email_subject}")
    # print(f"Email Body: {email_body}")

    # Extract the 6-digit verification code from the subject
    verification_code = extract_verification_code(email_subject)
    
    if verification_code:
        print(f"Verification Code: {verification_code}")
        return verification_code
    else:
        print("No verification code found in the subject.")
        return None


def select_current_date(page):
    current_date = str(datetime.now().day)
    buttons = page.locator("button.MuiButtonBase-root.MuiPickersDay-root")

    for i in range(buttons.count()):
        if buttons.nth(i).inner_text() == current_date:
            buttons.nth(i).click()
            break

def click_available_button(page):
    points_button = page.locator("a[href='/points']")
    referral_button = page.locator("a[href='/referral']")

    # Check if the points button exists and click it
    if points_button.count() > 0:
        points_button.click()
    # Otherwise, check if the referral button exists and click it
    elif referral_button.count() > 0:
        referral_button.click()
    else:
        print("Neither button is available.")

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()

    try:
        # Get temporary email address 1
        # page_email = context.new_page()
        # page_email.goto("https://luxusmail.org/", timeout=0)
        # print("Opened luxusmail.org")
        # time.sleep(5)
        # copy_button = page_email.locator("div.btn_copy")
        # copy_button.wait_for(timeout=0)
        # copy_button.click()
        # time.sleep(1)
        # temp_email1 = pyperclip.paste()
        # print(f"Temporary email1: {temp_email1}")

        # Open new tab for SkyTrade
        page = context.new_page()
        page.goto("https://app.sky.trade/")
        page.wait_for_load_state("networkidle", timeout=0)
        print("Opened SkyTrade")

        # Accept cookie
        page.locator("button.rounded.text-white").click()
        page.wait_for_load_state("networkidle", timeout=0)
        print("Accepted cookies")

        # Register Testing
        page.locator("p[class='md:block hidden']").click()
        page.locator("span.cursor-pointer.font-bold").click()
        print("Opened Register page")

        # Register with temporary email
        page.locator("input[id='email']").fill(EMAIL_ACCOUNT)
        page.locator("button.bg-dark-blue").click()
        page.wait_for_load_state("networkidle", timeout=0)
        print("Filled email and clicked login")

        # Wait for the email to arrive and get its content
        time.sleep(10)  # Adjust this sleep based on your email delivery time
        verification_code = read_verification_email()

        if verification_code:
            # Go back to the original page and input the verification code
            page.bring_to_front()
            otp_inputs = page.locator(".otp-input-container .otp-input")
            for i, digit in enumerate(verification_code):
                otp_inputs.nth(i).fill(digit)
            print("Filled verification code")
            page.wait_for_load_state("networkidle", timeout=0)

        # Proceed with further actions...
        page.wait_for_load_state("networkidle", timeout=0)
        #time.sleep(10)

        # Check for Set up 2FA page and complete if exists
        try:
            if page.locator("p.text-lg.font-bold").count() > 0:
                page.locator("button.t-btn-primar").click()
                page.wait_for_load_state("networkidle", timeout=0)
                page.locator("input[placeholder='Enter device name']").fill("dvc") # Enter device name
                page.locator("input[id='clear-browser-history']").click() # Click on clear browser
                page.locator("button.t-btn-primary.rounded-full.block").click()
                page.wait_for_load_state("networkidle", timeout=0)
                page.locator("input[id='passwordless-email']").fill("+27-824378777") # Fill phone number
                page.locator("button.t-btn.t-btn-primary.rounded-full").click()
                page.wait_for_load_state("networkidle", timeout=0)
                print("Authorized 2FA")
            else:
                print("2FA not found")
        except Exception as e:
            print(f"Error during 2FA interaction: {e}")

        page.wait_for_load_state("networkidle", timeout=0)
        #time.sleep(10)

        # Check for first login page and wait for it to escape
        first_login = page.locator("input[placeholder='email@mail.com']")
        first_login.wait_for(timeout=0)
        
        if first_login.count() > 0:
            #page.locator("button.bg-dark-blue").click()
            print("First login page found, waiting for the next step")
            page.wait_for_load_state("networkidle", timeout=0)
        else:
            print("First login page not found, proceeding to the next step")

        page.wait_for_load_state("networkidle", timeout=0)
        #time.sleep(10)

        # Check if the page has moved to the Get Started Page
        get_started = page.locator("p.text-center.text-base")
        get_started.wait_for(timeout=0)

        if get_started.count() > 0:
            page.locator("button.bg-dark-blue").click()
            print("Clicked Get Started")
        else:
            print("Get Started page not found, proceeding to the next step")

        page.wait_for_load_state("networkidle", timeout=0)   

        # Fill Customer Information
        page.locator("input[type='name']").fill("Joe Rex")
        page.locator("div[class='react-international-phone-country-selector']").click()
        list_box = page.locator("ul[class='react-international-phone-country-selector-dropdown']")
        county_selector = list_box.page.locator("li[id='react-international-phone__za-option']").click()
        page.locator("input[class='react-international-phone-input']").fill("27824659512")
        page.locator("input[id='individual']").click()
        page.locator("div.justify-center.text-white").click()
        print("Filled Customer Information")
        page.wait_for_load_state("networkidle", timeout=0)

        # Airspace Claim Testing
        dash_board = page.locator("div.relative.z-20")
        airspace_section = dash_board.locator("a[href='/airspaces']").click()
        reactour_close = page.locator("button.reactour__close-button")
        reactour_close.wait_for(timeout=0)
        reactour_close.click()
        airspace_address = page.locator("input[id='searchAirspaces']")
        airspace_address.fill("20 Henley Street, Port Elizabeth")
        page.locator("div[class='w-full p-5 text-left text-[#222222]']").nth(0).click()
        page.locator("div.Claim-airspacebtn-step").click()
        page.locator("select[id='timeZone']").select_option("Africa/Harare")
        page.locator("input[id='hasStorageHub']").click()
        page.keyboard.press('PageDown')
        page.wait_for_timeout(1000)

        # Daily Availability
        daily_availability = [
            ('0', '6', '21'),  # Sunday
            ('1', '7', '20'),  # Monday
            ('2', '7', '20'),  # Tuesday
            ('3', '7', '20'),  # Wednesday
            ('6', '6', '21')   # Saturday
        ]

        for day, start, end in daily_availability:
            page.locator(f"select[id='{day}/start']").select_option(start)
            page.locator(f"select[id='{day}/end']").select_option(end)
        
        # Thursday and Friday (Unavailability)
        page.locator("label.cursor-pointer.items-center").nth(4).click()  # Thursday
        page.locator("label.cursor-pointer.items-center").nth(5).click()  # Friday

        time.sleep(2)

        page.keyboard.press('PageDown')
        page.wait_for_timeout(1000)

        page.locator("input[id='zone-dont-know']").click()
        page.locator("div.Claim-airspacebtn2-step").click()
        print("Airspace Claiming Completed")
        page.wait_for_load_state("networkidle", timeout=0)
        #time.sleep(5)

        #Fund testing
        page.locator("a[href='/funds']").click()
        page.locator("div.transform.transition-transform.duration-300").click() # Payment option dropdown
        page.keyboard.press('PageDown')
        page.wait_for_timeout(1000)
        page.locator("li.flex").nth(0).click() # Select Native Payment Option
        page.locator("div.relative").nth(4).click() # Copy Deposit Wallet ID
        time.sleep(1)  # Give a moment for the clipboard to update
        deposit_id = pyperclip.paste()
        print(f"Wallet Id: {deposit_id}")
        page.keyboard.press('PageUp')
        page.wait_for_timeout(1000)
        page.locator("div.text-center.cursor-pointer.w-full").nth(1).click() # Withdrawal button
        page.keyboard.press('PageDown')
        page.wait_for_timeout(1000)
        page.locator("input[id='amount']").fill("300") # Amount
        page.locator("input[id='walletId']").fill(deposit_id) # Paste Deposit Wallet ID
        page.locator("button.text-white.flex.items-center").click() # Final withdrawal button
        print("Fund Testing Completed")
        page.wait_for_load_state("networkidle", timeout=0)

        # Airspace Rent Testing
        dash_board.locator("a[href='/rent']").click()
        #page.locator("a[href='/rent']").click()
        page.wait_for_load_state("networkidle", timeout=0)
        time.sleep(40)
        page.locator("input[id='searchAirspaces']").fill("1025 Robertson Street, Fort Collins, Colorado")
        #address = page.locator("div[data-value='2955 Baseline Rd, Boulder, Colorado 80303, United States']")
        address = page.locator("div[class='w-full p-5 text-left text-[#222222]  ']").nth(0)
        address.wait_for(timeout=0)
        address.click()
        time.sleep(15)
        rent_to_click = page.locator("div[data-value='1025 Robertson St Fort Collins CO']").nth(0)
        rent_to_click.wait_for(timeout=0)
        rent_to_click.locator("span.rounded-lg.text-center").click()
        page.locator("svg[data-testid='CalendarIcon']").click()
        select_current_date(page)
        #page.locator("button[aria-colindex='4']").nth(4).click()
        page.locator("li[aria-label='10 hours']").click()
        page.locator("li[aria-label='PM']").click()
        page.locator("button.flex").click()
        page.locator("div.text-center").click()
        print("Airspace Renting Completed")
        page.wait_for_load_state("networkidle", timeout=0)
        #time.sleep(5)

    finally:
        browser.close()
