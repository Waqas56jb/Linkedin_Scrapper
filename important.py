import time
import random
import pandas as pd
from DrissionPage import ChromiumPage
from colorama import init, Fore, Style
import smtplib
from email.mime.text import MIMEText
import os
import re
import csv
from email.message import EmailMessage
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox, simpledialog
import sys
import threading
import queue

# Initialize colorama
init(autoreset=True)

# Global browser instance
browser = ChromiumPage()

# ===================================== CORE FUNCTIONALITY =====================================

def linkedin_login(email, password):
    try:
        browser.get('https://www.linkedin.com/login')
        time.sleep(2)

        # Updated element selectors
        email_field = browser.ele('xpath://input[@autocomplete="username"]', timeout=10)
        password_field = browser.ele('xpath://input[@autocomplete="current-password"]', timeout=10)
        login_button = browser.ele('xpath://button[@aria-label="Sign in"]', timeout=10)

        email_field.input(email)
        password_field.input(password)
        login_button.click()
        time.sleep(5)

        # Verify login success
        if 'feed' in browser.url:
            return True
        if 'checkpoint/challenge' in browser.url:
            handle_verification()
        return False
    except Exception as e:
        print(f"Login error: {str(e)}")
        return False

def handle_verification():
    try:
        messagebox.showinfo("Verification Needed", "Please complete manual verification in the browser")
        while 'checkpoint/challenge' in browser.url:
            time.sleep(1)
        return True
    except Exception as e:
        print(f"Verification error: {str(e)}")
        return False

def search_and_scrape_posts(query):
    try:
        # Perform search
        search_box = browser.ele('xpath://input[@aria-label="Search"]', timeout=10)
        search_box.input(query + '\n')
        time.sleep(5)

        # Switch to posts tab
        posts_tab = browser.ele('xpath://button[contains(text(), "Posts")]', timeout=10)
        posts_tab.click()
        time.sleep(3)

        # Scraping logic...
        # (Keep your existing post scraping logic here)
        
        return True
    except Exception as e:
        print(f"Search error: {str(e)}")
        return False

# ===================================== GUI APPLICATION =====================================

class LinkedInBotGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LinkedIn Automation Suite Pro")
        self.geometry("1200x800")
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Login credentials
        self.email = ""
        self.password = ""
        
        # Create widgets
        self.create_widgets()
        self.check_login_status()

    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left panel
        control_frame = ttk.Frame(main_frame, width=300)
        control_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Right panel
        console_frame = ttk.Frame(main_frame)
        console_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Login controls
        login_btn = ttk.Button(control_frame, text="🔑 Login to LinkedIn", command=self.show_login_dialog)
        login_btn.pack(pady=10)

        # Features
        ttk.Label(control_frame, text="Automation Features", font=('Arial', 12, 'bold')).pack(pady=10)
        
        features = [
            ("🔍 Search Hiring Posts", self.start_post_search),
            ("🤝 Send Connections", self.send_connections),
            ("📤 Export Connections", self.export_connections),
            ("📩 Monitor Messages", self.monitor_messages),
            ("🎯 Extract Leads", self.extract_leads),
            ("💬 Send Greetings", self.send_greetings)
        ]
        
        for text, cmd in features:
            btn = ttk.Button(control_frame, text=text, command=cmd)
            btn.pack(fill=tk.X, pady=5)

        # Console
        self.console = scrolledtext.ScrolledText(console_frame, wrap=tk.WORD, state="disabled")
        self.console.pack(fill=tk.BOTH, expand=True)

        # Redirect stdout
        sys.stdout = TextRedirector(self.console)

    def show_login_dialog(self):
        login_window = tk.Toplevel(self)
        login_window.title("LinkedIn Login")
        
        ttk.Label(login_window, text="Email:").grid(row=0, column=0, padx=5, pady=5)
        email_entry = ttk.Entry(login_window)
        email_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(login_window, text="Password:").grid(row=1, column=0, padx=5, pady=5)
        password_entry = ttk.Entry(login_window, show="*")
        password_entry.grid(row=1, column=1, padx=5, pady=5)
        
        def perform_login():
            self.email = email_entry.get()
            self.password = password_entry.get()
            if linkedin_login(self.email, self.password):
                messagebox.showinfo("Success", "Logged in successfully!")
                login_window.destroy()
            else:
                messagebox.showerror("Error", "Login failed")
        
        ttk.Button(login_window, text="Login", command=perform_login).grid(row=2, column=1, pady=10)

    def start_post_search(self):
        query = simpledialog.askstring("Search Query", "Enter your search query:")
        if query:
            threading.Thread(target=self.run_post_search, args=(query,)).start()

    def run_post_search(self, query):
        if not self.check_login_status():
            return
        if search_and_scrape_posts(query):
            messagebox.showinfo("Success", "Posts scraped successfully!")
        else:
            messagebox.showerror("Error", "Failed to scrape posts")

    def check_login_status(self):
        if not browser.url.startswith("https://www.linkedin.com/feed"):
            messagebox.showwarning("Login Required", "Please login first")
            return False
        return True

    def on_close(self):
        if messagebox.askokcancel("Quit", "Do you want to exit?"):
            browser.quit()
            self.destroy()

class TextRedirector:
    def __init__(self, widget):
        self.widget = widget

    def write(self, text):
        self.widget.config(state="normal")
        self.widget.insert("end", text)
        self.widget.see("end")
        self.widget.config(state="disabled")
    
    def flush(self):
        pass

# ===================================== MAIN EXECUTION =====================================

if __name__ == "__main__":
    app = LinkedInBotGUI()
    app.mainloop()