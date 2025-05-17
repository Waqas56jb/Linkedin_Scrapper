import time
import random
import pandas as pd
from DrissionPage import ChromiumPage
from colorama import init, Fore, Style
import smtplib
from email.mime.text import MIMEText
import getpass
import os

# Initialize colorama for colored CLI output
init()

def display_title():
    """Display the software title in a bold, stylish manner."""
    print(Fore.CYAN + Style.BRIGHT + """                          

                                                                              

                                 
  _      _       _            _ _____          _____        __ _                           __      ____ 
 | |    (_)     | |          | |_   _|        / ____|      / _| |                          \ \    / /_ |
 | |     _ _ __ | | _____  __| | | |  _ __   | (___   ___ | |_| |___      ____ _ _ __ ___   \ \  / / | |
 | |    | | '_ \| |/ / _ \/ _` | | | | '_ \   \___ \ / _ \|  _| __\ \ /\ / / _` | '__/ _ \   \ \/ /  | |
 | |____| | | | |   <  __/ (_| |_| |_| | | |  ____) | (_) | | | |_ \ V  V / (_| | | |  __/    \  /   | |
 |______|_|_| |_|_|\_\___|\__,_|_____|_| |_| |_____/ \___/|_|  \__| \_/\_/ \__,_|_|  \___|     \/    |_|
                                                                                                           
                                                                                                    
                                                                                                   
    """ + Style.RESET_ALL)
    print("Welcome to LinkedIn Automation!\n")

def smart_search(page):
    """Feature 1: Smart Search and Export to Excel."""
    print("\nSmart Search and Export to Excel")
    search_type = input("Search for (1) People or (2) Posts? Enter 1 or 2: ")
    
    if search_type == "1":
        job_title = input("Enter job title (e.g., Senior Java Architect): ")
        location = input("Enter location (e.g., Hyderabad): ")
        
        query = f"{job_title} {location}"
        page.ele("css:input[placeholder*='Search']").input(query)
        page.ele("css:button[aria-label*='Search']").click()
        time.sleep(3)
        
        # Placeholder for scraping people
        profiles = []
        results = page.eles("css:li.reusable-search__result-container")[:5]  # Limit to 5 for demo
        for result in results:
            name = result.ele("css:span.entity-result__title-text").text
            profile_url = result.ele("css:a.app-aware-link").attr("href")
            profiles.append({"Name": name, "Profile URL": profile_url})
        
        df = pd.DataFrame(profiles)
        df.to_excel("linkedin_people_search.xlsx", index=False)
        print("People search results saved to linkedin_people_search.xlsx")
    
    elif search_type == "2":
        hashtag_query = input("Enter hashtag query (e.g., #hiring #java Texas): ")
        page.ele("css:input[placeholder*='Search']").input(hashtag_query)
        page.ele("css:button[aria-label*='Search']").click()
        time.sleep(3)
        
        # Placeholder for scraping posts
        posts = []
        post_elements = page.eles("css:div.feed-shared-update-v2")[:5]  # Limit to 5
        for post in post_elements:
            name = post.ele("css:span.feed-shared-actor__name").text
            url = post.ele("css:a.app-aware-link").attr("href")
            date = post.ele("css:span.feed-shared-actor__sub-description").text
            content = post.ele("css:span.feed-shared-text").text
            posts.append({"Name": name, "URL": url, "Date": date, "Content": content})
        
        df = pd.DataFrame(posts)
        df.to_excel("linkedin_posts_search.xlsx", index=False)
        print("Posts search results saved to linkedin_posts_search.xlsx")

def send_connection_requests(page):
    """Feature 2: Send Connection Requests with Custom Message."""
    print("\nSend Connection Requests with Custom Message")
    excel_file = input("Enter path to Excel file with profile links: ")
    message = input("Enter custom connection message: ")
    
    try:
        df = pd.read_excel(excel_file)
        profiles = df["Profile URL"].tolist()
    except Exception as e:
        print(f"Error reading Excel: {e}")
        return
    
    for profile in profiles[:5]:  # Limit to 5 for demo
        page.get(profile)
        time.sleep(random.uniform(2, 5))  # Random delay
        connect_button = page.ele("css:button[aria-label*='Invite']")
        if connect_button:
            connect_button.click()
            time.sleep(1)
            page.ele("css:button[aria-label*='Add a note']").click()
            page.ele("css:textarea").input(message)
            page.ele("css:button[aria-label*='Send']").click()
            print(f"Connection request sent to {profile}")
        
        # Random activity
        if random.choice([True, False]):
            page.get("https://www.linkedin.com/feed/")
            page.run_js("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(1, 3))
    
    print("Connection requests completed.")

def monitor_messages(page):
    """Feature 3: Monitor Messages and Send Alerts."""
    print("\nMonitor Messages and Send Alerts")
    email_to = input("Enter email for alerts: ")
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = input("Enter your Gmail email: ")
    smtp_pass = getpass.getpass("Enter your Gmail App Password: ")
    
    page.get("https://www.linkedin.com/messaging/")
    last_message_count = 0
    
    print("Monitoring messages... Press Ctrl+C to stop.")
    try:
        while True:
            messages = page.eles("css:li.msg-conversation-listitem")[:5]  # Check recent 5
            current_count = len(messages)
            if current_count > last_message_count:
                for msg in messages[last_message_count:]:
                    sender = msg.ele("css:span.msg-s-event-listitem__subject").text
                    content = msg.ele("css:div.msg-s-event-listitem__body").text
                    alert_message = f"New LinkedIn Message from {sender}:\n{content}"
                    
                    # Send email alert
                    msg = MIMEText(alert_message)
                    msg["Subject"] = "New LinkedIn Message Alert"
                    msg["From"] = smtp_user
                    msg["To"] = email_to
                    with smtplib.SMTP(smtp_server, smtp_port) as server:
                        server.starttls()
                        server.login(smtp_user, smtp_pass)
                        server.sendmail(smtp_user, email_to, msg.as_string())
                    print(f"Alert sent for new message from {sender}")
                
                last_message_count = current_count
            
            time.sleep(30)  # Check every 30 seconds
    except KeyboardInterrupt:
        print("Stopped monitoring messages.")

def export_connections(page):
    """Feature 4: Export All Your LinkedIn Connections."""
    print("\nExport All Your LinkedIn Connections")
    page.get("https://www.linkedin.com/mynetwork/invite-connect/connections/")
    time.sleep(3)
    
    connections = []
    while True:
        # Scroll to load more connections
        page.run_js("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        items = page.eles("css:li.mn-connection-card")[:10]  # Limit to 10 for demo
        for item in items:
            name = item.ele("css:span.mn-connection-card__name").text
            title = item.ele("css:span.mn-connection-card__occupation").text
            url = item.ele("css:a.mn-connection-card__link").attr("href")
            connections.append({"Name": name, "Title": title, "URL": f"https://www.linkedin.com{url}"})
        
        next_button = page.ele("css:button[aria-label*='Next']")
        if not next_button or not next_button.is_enabled():
            break
        next_button.click()
        time.sleep(2)
    
    df = pd.DataFrame(connections)
    df.to_excel("linkedin_connections.xlsx", index=False)
    print("Connections saved to linkedin_connections.xlsx")

def send_greetings(page):
    """Feature 5: Send Greetings Automatically."""
    print("\nSend Greetings Automatically")
    excel_file = input("Enter path to Excel file with names and messages (or leave blank for birthdays): ")
    
    if excel_file:
        try:
            df = pd.read_excel(excel_file)
            greetings = df[["Name", "Message"]].to_dict("records")
        except Exception as e:
            print(f"Error reading Excel: {e}")
            return
    else:
        # Placeholder for birthday greetings
        page.get("https://www.linkedin.com/notifications/")
        greetings = []
        notifications = page.eles("css:div.nt-card")[:5]  # Check recent notifications
        for noti in notifications:
            if "birthday" in noti.text.lower():
                name = noti.ele("css:span.nt-card__headline").text.split(" ")[0]
                greetings.append({"Name": name, "Message": "Happy Birthday! Wishing you a fantastic year ahead!"})
    
    for greeting in greetings:
        page.get("https://www.linkedin.com/messaging/")
        page.ele("css:input[placeholder*='Search messages']").input(greeting["Name"])
        time.sleep(1)
        page.ele("css:li.msg-conversation-listitem").click()
        page.ele("css:div.msg-form__contenteditable").input(greeting["Message"])
        page.ele("css:button.msg-form__send-button").click()
        print(f"Sent greeting to {greeting['Name']}")
        time.sleep(random.uniform(2, 5))
    
    print("Greetings sent.")

def main():
    """Main function to run the LinkedIn Software."""
    display_title()
    page = ChromiumPage()
    
    # Navigate to LinkedIn homepage to ensure session is active
    page.get("https://www.linkedin.com/feed/")
    time.sleep(3)
    
    while True:
        print("\nSelect a feature to run:")
        print("1. Smart Search and Export to Excel")
        print("2. Send Connection Requests with Custom Message")
        print("3. Monitor Messages and Send Alerts")
        print("4. Export All Your LinkedIn Connections")
        print("5. Send Greetings Automatically")
        print("6. Exit")
        
        choice = input("Enter your choice (1-6): ")
        
        if choice == "1":
            smart_search(page)
        elif choice == "2":
            send_connection_requests(page)
        elif choice == "3":
            monitor_messages(page)
        elif choice == "4":
            export_connections(page)
        elif choice == "5":
            send_greetings(page)
        elif choice == "6":
            print("Exiting LinkedIn Software v1...")
            break
        else:
            print("Invalid choice. Please try again.")
    
    page.quit()

if __name__ == "__main__":
    main()