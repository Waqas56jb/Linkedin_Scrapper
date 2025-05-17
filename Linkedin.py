import time
import random
import pandas as pd
from DrissionPage import ChromiumPage
from colorama import init, Fore, Style
import smtplib
from email.mime.text import MIMEText
import getpass
import os
import re
from DataRecorder import Recorder
import csv
import smtplib
from email.message import EmailMessage



# Initialize colorama for colored CLI output



def display_banner():
        banner = r"""                          

                                                                              

                                 
  _      _       _            _ _____          _____        __ _                           __      ____ 
 | |    (_)     | |          | |_   _|        / ____|      / _| |                          \ \    / /_ |
 | |     _ _ __ | | _____  __| | | |  _ __   | (___   ___ | |_| |___      ____ _ _ __ ___   \ \  / / | |
 | |    | | '_ \| |/ / _ \/ _` | | | | '_ \   \___ \ / _ \|  _| __\ \ /\ / / _` | '__/ _ \   \ \/ /  | |
 | |____| | | | |   <  __/ (_| |_| |_| | | |  ____) | (_) | | | |_ \ V  V / (_| | | |  __/    \  /   | |
 |______|_|_| |_|_|\_\___|\__,_|_____|_| |_| |_____/ \___/|_|  \__| \_/\_/ \__,_|_|  \___|     \/    |_|
                                                                                                           
                                                                                                    
    LinkedIn Automation Bot v1.0 (Logged-In Session)
        """
        print("\033[1;36m" + banner + "\033[0m")
        
page = ChromiumPage()

    # Navigate to LinkedIn and log in (update with your credentials)
#page.get('https://www.linkedin.com/login')





 #||===================================== Feature 1 =====================================||   






def Hiring_Post():
    # Initialize browser session
    page = ChromiumPage()

    # Navigate to LinkedIn and log in (update with your credentials)
    page.get('https://www.linkedin.com/login')
    

    # Perform search
    try:
        search_button = page.ele('xpath://button[@aria-label="Click to start a search"]', timeout=10)
        page.wait.ele_displayed(search_button, timeout=10)
        search_button.click(by_js=True)
        
        query = input("\033[1;32m Enter your search query: \033[0m")
        print(query)
        search_input = page.ele('xpath://div[@id="global-nav-typeahead"]//input[@role="combobox"]', timeout=10)
        search_input.input(query + '\n')
        time.sleep(8)  # Wait for search results
    except Exception as e:
        print(f"Error performing search: {e}")
        page.quit()
        exit()

    posts_data = []
    processed_post_ids = set()

    # Scroll to load initial posts and make "See all post results" button visible
    print("Scrolling to load initial posts...")
    for _ in range(1):
        page.scroll.down(1500)
        time.sleep(1)

    # Check for "See all post results" button and click it
    try:
        see_all_button = page.ele('xpath://div[contains(@class, "search-results__cluster-bottom-banner")]//a[text()="See all post results"]', timeout=10)
        if see_all_button:
            print("See all post results button found, clicking...")
            button_href = see_all_button.attr('href')
            if button_href and button_href.startswith('https://www.linkedin.com'):
                print(f"Navigating to button href: {button_href}")
                page.get(button_href)
                page.wait.doc_loaded()
                time.sleep(8)
            else:
                see_all_button.click(by_js=True)
                page.wait.doc_loaded()
                time.sleep(8)
            for _ in range(10):
                page.scroll.down(1500)
                page.scroll.to_bottom()
                time.sleep(1.5)
        else:
            print("See all post results button not found, proceeding with visible posts...")
    except Exception as e:
        print(f"Error finding See all post results button: {e}")
        print("Proceeding with visible posts...")

    while True:
        post_elements = page.eles('tag:div@data-urn:urn:li:activity:', timeout=5)
        if not post_elements:
            print("No post elements found, debugging page content...")
            login_prompt = page.ele('tag:div@id=login', timeout=2) or page.ele('tag:button@text():Sign in', timeout=2)
            if login_prompt:
                print("Login prompt detected, please ensure the script is logged in")
            potential_posts = page.eles('tag:div@data-urn:urn:li:', timeout=5) or \
                             page.eles('tag:div@data-id:urn:li:', timeout=5) or \
                             page.eles('tag:div@class=feed-shared-update-v2', timeout=5)
            print(f"Found {len(potential_posts)} potential post elements")
            if potential_posts:
                print(f"Sample post HTML: {potential_posts[0].html[:500]}...")
        
        print(f"Found {len(post_elements)} post elements in this iteration")
        
        for post in post_elements:
            post_id = post.attr('data-urn')
            if post_id in processed_post_ids:
                continue
            processed_post_ids.add(post_id)
            
            post_details = {}
            
            try:
                name_element = post.ele('tag:span@class=update-components-actor__title', timeout=2)
                if name_element:
                    name_span = name_element.ele('tag:span@dir=ltr').ele('tag:span@aria-hidden=true')
                    post_details['poster_name'] = name_span.text.strip() if name_span else 'Unknown'
                    print(f"Name found: {post_details['poster_name']}")
                else:
                    post_details['poster_name'] = 'Unknown'
                    print("Name element not found")
            except Exception as e:
                post_details['poster_name'] = 'Unknown'
                print(f"Error extracting poster name: {e}")
            
            try:
                date_element = post.ele('tag:span@class=update-components-actor__sub-description', timeout=2)
                
                date_element = post.ele('tag:span@text():mo', timeout=2)
                date_element2 = post.ele('tag:span@text():h', timeout=2)
                date_element3 = post.ele('tag:span@text():w', timeout=2)
                if date_element:
                    date_span = date_element.ele('tag:span@aria-hidden=true') or date_element
                    date_text = date_span.text.strip() if date_span else 'Unknown'
                    post_details['post_date'] = date_text.split('•')[0].strip() if '•' in date_text else date_text
                    #print(f"Date found: {post_details['post_date']}")
                else:
                    post_details['post_date'] = 'Unknown'
                    print("Date element not found")
                    print(f"Post HTML snippet: {post.html[:200]}...")
            except Exception as e:
                post_details['post_date'] = 'Unknown'
                print(f"Error extracting post date: {e}")
                if date_element2:
                    date_span = date_element2.ele('tag:span@aria-hidden=true') or date_element2
                    date_text = date_span.text.strip() if date_span else 'Unknown'
                    post_details['post_date'] = date_text.split('•')[0].strip() if '•' in date_text else date_text
                    print(f"Date found: {post_details['post_date']}")
                else:
                    post_details['post_date'] = 'Unknown'
                    print("Date element not found")
                    print(f"Post HTML snippet: {post.html[:200]}...")
            except Exception as e:
                post_details['post_date'] = 'Unknown'
                print(f"Error extracting post date: {e}")
                if date_element3:
                    date_span = date_element3.ele('tag:span@aria-hidden=true') or date_element3
                    date_text = date_span.text.strip() if date_span else 'Unknown'
                    post_details['post_date'] = date_text.split('•')[0].strip() if '•' in date_text else date_text
                    print(f"Date found: {post_details['post_date']}")
                else:
                    post_details['post_date'] = 'Unknown'
                    #print("Date element not found")
                    #print(f"Post HTML snippet: {post.html[:200]}...")
            except Exception as e:
                post_details['post_date'] = 'Unknown'
                print(f"Error extracting post date: {e}")
            
            try:
                url_element = post.ele('tag:a@class=update-components-actor__meta-link', timeout=2)
                if not url_element:
                    url_element = post.ele('tag:a@href:/in/', timeout=2)
                post_details['poster_url'] = url_element.attr('href') if url_element else 'Unknown'
                print(f"URL found: {post_details['poster_url']}")
            except Exception as e:
                post_details['post_date'] = 'Unknown'
                print(f"Error extracting poster URL: {e}")
            
            try:
                see_more_button = post.ele('tag:button@text():more', timeout=1) or \
                                 post.ele('tag:button@class=feed-shared-inline-show-more-text__see-more-less-toggle', timeout=1) or \
                                 post.ele('tag:span@text():See more', timeout=1)
                if see_more_button:
                    see_more_button.click(by_js=True)
                    time.sleep(1.5)
                
                content_element = post.ele('xpath://div[contains(@class, "update-components-text")]//span[@dir="ltr"]', timeout=2)
                if content_element:
                    content_text = content_element.text.strip()
                    content_text = re.sub(r'\s+', ' ', content_text)
                    content_text = re.sub(r'hashtag\s+', '', content_text)
                    post_details['post_content'] = content_text if content_text else 'No content available'
                    print(f"Content found: {post_details['post_content'][:50]}...")
                else:
                    post_details['post_content'] = 'No content available'
                    print("Content element not found")
                    description_area = post.ele('tag:div@class=feed-shared-update-v2', timeout=2)
                    print(f"Description area HTML: {description_area.html[:300] if description_area else 'Not found'}...")
            except Exception as e:
                post_details['post_content'] = 'No content available'
                print(f"Error extracting post content: {e}")
            
            posts_data.append(post_details)
        
        # Save scraped data to CSV after processing posts
        if posts_data:
            df = pd.DataFrame(posts_data, columns=['poster_name', 'post_date', 'poster_url', 'post_content'])
            df.insert(0, 'Post Number', range(1, len(df) + 1))
            df.columns = ['Post Number', 'Poster Name', 'Post Date', 'Poster URL', 'Post Content']
            df.to_csv('linkedin_posts.csv', index=False, encoding='utf-8')
            print(f"Exported {len(posts_data)} posts to linkedin_posts.csv")
        else:
            print("No posts found to export to CSV in this iteration")
        
        # Try to find the "Show more results" button with controlled scrolling
        show_more_button = None
        max_scroll_attempts = 3
        for attempt in range(max_scroll_attempts):
            print(f"Scroll attempt {attempt + 1}/{max_scroll_attempts} to find Show more results button...")
            for _ in range(10):
                page.scroll.down(1000)  # Precise scrolling
                time.sleep(1.5)
            time.sleep(3)  # Wait for button to be interactable
            show_more_button = page.ele('xpath://button[contains(@class, "scaffold-finite-scroll__load-button") and .//span[text()="Show more results"]]', timeout=8)
            if show_more_button:
                print("Show more results button found, clicking...")
                try:
                    show_more_button.click(by_js=True)
                    page.wait.doc_loaded()
                    time.sleep(8)
                    for _ in range(15):
                        page.scroll.to_bottom()
                        time.sleep(2)
                    break
                except Exception as e:
                    print(f"Error clicking Show more results button: {e}")
                    show_more_button = None
            else:
                print("Show more results button not found in this attempt...")
        
        if show_more_button:
            continue
        else:
            print("No Show more results button found after scrolling attempts, checking for new posts...")
            for _ in range(10):
                page.scroll.to_bottom()
                time.sleep(2)
            new_post_elements = page.eles('tag:div@data-urn:urn:li:activity:', timeout=5)
            print(f"Found {len(new_post_elements)} post elements after final scrolling")
            if len(new_post_elements) > len(post_elements):
                print("New posts found, continuing...")
                continue
            print("No new posts or Show more results button found, stopping...")
            break






    








#|||===================================== Feature 2  =====================================||| 




def send_connection_requests():
    page = ChromiumPage()

    time.sleep(5)

    with open('profiles.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            profile_url = row[0]
            page.get(profile_url)
            time.sleep(3)
            more_button = page.ele('xpath://button[@aria-label="More actions" and @type="button"]', timeout=5)
            if more_button:
                more_button.click(by_js=True)
            connect_button = page.ele('xpath://div[@role="button" and contains(@aria-label, "Invite") and contains(@aria-label, "connect")]', timeout=5)
            if connect_button:
                time.sleep(3)
                connect_button.click(by_js=True)
                print(f"Connection request sent to {profile_url}")
                time.sleep(3)
            
            send_button = page.ele('xpath://button[@aria-label="Send without a note"]')
            if send_button:
                send_button.click() 
            #     send_button = page.ele('t:button@text():Send', timeout=5)
            #     if send_button:
            #         send_button.click()
            #         print(f"Connection request sent to {profile_url}")
            #     else:
            #         print(f"No send button found for {profile_url}")
            # else:
            #     print(f"No connect button found for {profile_url}")
            # time.sleep(2)















#||===================================== Feature 3  =====================================|| 


def monitor_linkedin_messages():
    page = ChromiumPage()
    page.get('https://www.linkedin.com/messaging/?filter=unread')
    time.sleep(5)

    time.sleep(5)

    processed_messages = set()
    input("\033[1;32m Enter the 16-character Gmail App Password: \033[0m")
    sender_email = input("\033[1;32m Enter the sender's Gmail address (e.g., chawdharybilal.786@gmail.com): \033[0m")
    recipient_email =  input("\033[1;32m Enter the recipient's email address (e.g., helpdeskbizzkonn@gmail.com): \033[0m")
    app_password = input("\033[1;32m Enter the 16-character Gmail App Password: \033[0m")

    while True:
        items = page.eles('xpath://ul[@class="list-style-none msg-conversations-container__conversations-list"]/li[contains(@class, "msg-conversation-listitem")]')
        unread_messages = []

        for item in items:
            try:
                snippet = item.ele('xpath://p[contains(@class, "msg-conversation-card__message-snippet--unread")]')
                if snippet:
                    name_ele = item.ele('xpath://h3[contains(@class, "msg-conversation-listitem__participant-names")]//span[@class="truncate"]')
                    name = name_ele.text if name_ele else 'Unknown'
                    text = snippet.text
                    timestamp = item.ele('xpath://time[contains(@class, "msg-conversation-listitem__time-stamp")]').text
                    message_id = f"{name}_{text}_{timestamp}"
                    
                    if message_id not in processed_messages:
                        unread_messages.append((name, text, timestamp))
                        processed_messages.add(message_id)
            except:
                continue

        if unread_messages:
            msg = EmailMessage()
            msg['Subject'] = 'New LinkedIn Messages Alert'
            msg['From'] = sender_email
            msg['To'] = recipient_email
            body = ''
            for name, text, timestamp in unread_messages:
                body += f'From: {name}\nMessage: {text}\nTime: {timestamp}\n\n'
            msg.set_content(body)
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(sender_email, app_password)
                smtp.send_message(msg)
            print('New Unread Messages Detected!')
        else:
            print('No new messages.')

        time.sleep(60)
        page.refresh()










#||===================================== Feature 4 =====================================|| 






def scrape_linkedin_connections():
    page = ChromiumPage()
    page.get("https://www.linkedin.com/mynetwork/invite-connect/connections/")
    page.wait.doc_loaded()
    page.wait.ele_displayed('xpath://li[contains(@class, "mn-connection-card")]', timeout=10)
    time.sleep(random.uniform(2, 4))

    # Scroll to load all connections
    prev_connection_count = 0
    while True:
        try:
            # Check for "Show more results" button
            load_button = page.ele('xpath://button[contains(@class, "scaffold-finite-scroll__load-button")]', timeout=10)
            if not load_button:
                print("No more 'Show more results' button found. Scrolling complete.")
                break
            
            # Get current number of connections
            current_connections = page.eles('xpath://li[contains(@class, "mn-connection-card")]')
            current_count = len(current_connections)
            
            # Click the button
            load_button.click()
            time.sleep(random.uniform(1, 2))  # Initial delay before checking
            
            # Wait for new connections to load or button to disappear
            max_wait = 10  # Max wait time in seconds
            start_time = time.time()
            while time.time() - start_time < max_wait:
                new_connections = page.eles('xpath://li[contains(@class, "mn-connection-card")]')
                new_count = len(new_connections)
                if new_count > current_count or not page.ele('xpath://button[contains(@class, "scaffold-finite-scroll__load-button")]', timeout=2):
                    print(f"Loaded {new_count} connections (was {current_count})")
                    prev_connection_count = new_count
                    break
                time.sleep(0.5)  # Check every half second
            
            # If no new connections loaded and button still present, retry
            if new_count <= current_count:
                print("No new connections loaded, retrying...")
                time.sleep(random.uniform(2, 5))
                continue
            
            time.sleep(random.uniform(2, 5))  # Random delay to mimic human behavior
        
        except Exception as e:
            print(f"Error during scrolling: {e}")
            if not page.ele('xpath://button[contains(@class, "scaffold-finite-scroll__load-button")]', timeout=2):
                print("No more 'Show more results' button after error. Scrolling complete.")
                break
            time.sleep(random.uniform(2, 5))  # Wait before retrying

    # Scrape all connections after scrolling is complete
    connections_data = []
    connection_blocks = page.eles('xpath://li[contains(@class, "mn-connection-card")]')

    for block in connection_blocks:
        try:
            name = block.ele('xpath:.//span[contains(@class, "mn-connection-card__name")]').text.strip() if block.ele('xpath:.//span[contains(@class, "mn-connection-card__name")]') else "N/A"
            title = block.ele('xpath:.//span[contains(@class, "mn-connection-card__occupation")]').text.strip() if block.ele('xpath:.//span[contains(@class, "mn-connection-card__occupation")]') else "N/A"
            relative_url = block.ele('xpath:.//a[contains(@class, "mn-connection-card__link")]/@href').strip() if block.ele('xpath:.//a[contains(@class, "mn-connection-card__link")]') else "N/A"
            linkedin_url = f"https://www.linkedin.com{relative_url}" if relative_url != "N/A" else "N/A"
            company = "N/A"
            if " at " in title:
                company = title.split(" at ")[-1].strip()
            connections_data.append({
                "Name": name,
                "Title": title,
                "Company": company,
                "LinkedIn URL": linkedin_url
            })
        except Exception as e:
            print(f"Error processing connection: {e}")
            continue

    df = pd.DataFrame(connections_data)
    #timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"linkedin_connections.csv"
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

    page.close()
    return filename













#||===================================== Feature 5=====================================|| 




def send_greetings(page):
   print("Feature is under working")
def main():
    """Main function to run the LinkedIn Software."""
    display_banner()
    
    
    # Navigate to LinkedIn homepage to ensure session is active
    #page.get("https://www.linkedin.com/feed/")
    time.sleep(3)
    
    
    
    
    
    
    
    
    #||===================================== Main Menu =====================================|| 





    while True:
        menu = """
        \033[1;33mMAIN MENU:\033[0m
        1. Search Hiring Posts & Export
        2. Send Connection Requests
        3. Export Your Connections
        4. MessagesMonitor Messages
        5. Send Automatic GreetingsMonitor
        6. Exit
        
                """
        print(menu)
        
        choice = input("\033[1;32mEnter your choice (1-8): \033[0m")
        
        if choice == "1":
            Hiring_Post()
        elif choice == "2":
            send_connection_requests()
        elif choice == "3":
            scrape_linkedin_connections()
        elif choice == "4":
            monitor_linkedin_messages()
        elif choice == "5":
            send_greetings()
        elif choice == "6":
            print("Exiting LinkedIn Software v1...")
            break
        else:
            print("Invalid choice. Please try again.")
    
    

if __name__ == "__main__":
    main()