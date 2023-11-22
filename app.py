from multiprocessing import context
from dotenv import load_dotenv
import os, requests, json
from bs4 import BeautifulSoup
from canvasapi import Canvas, calendar_event
from datetime import datetime
from datetime import date


'''
scraping assignment titles and due dates from shelby
'''

class Scraper:
    def fetch_data(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            response.raise_for_status()
    
    def parse_html(self, html):
        return BeautifulSoup(html, "html.parser")

    def extract_presentations(self, parsed_html):
        presentations = {}
        assignments = parsed_html.text.split("</tr>")
        for i in assignments:
            soup = BeautifulSoup(i, "html.parser")

            '''
            grabbing presentation titles and due dates 
            '''
            title = soup.find('td', class_='course__task_title')
            date = soup.find("td", class_='course__task_actual')

            if title and date:
               if 'Group B' in title.text:
                stripped_title = title.text.strip()
                stripped_date = date.text.strip()
                presentations[stripped_title] = stripped_date
        return presentations

    def extract_sprints(self, html):
        sprints = {}
        assignments = html.text.split("</tr>")
        for i in assignments:
            soup = BeautifulSoup(i, "html.parser")
            
            '''
            grabbing sprint due dates
            '''
            sprint_number = soup.find("td", class_='course__status_report_sprint_number')
            sprint_day = soup.find("td", class_='course__status_report_date_day')
            sprint_month = soup.find('td', class_='course__status_report_date_month')

            # place sprint blocks in a dictionary
            if sprint_number and sprint_day and sprint_month:
                stripped_sprint_number = sprint_number.text.strip()
                stripped_sprint_day = sprint_day.text.strip()
                stripped_sprint_month = sprint_month.text.strip()
                sprints[stripped_sprint_number] = stripped_sprint_month,stripped_sprint_day
        return sprints

class CalendarIntegration:
    def __init__(self, api_key):
        self.api_key = api_key
        self.api_url = "https://canvas.ewu.edu/api/v1/calendar_events"
        self.headers = {
            "Authorization":f"Bearer {self.api_key}"
        }
        self.canvas = Canvas("https://canvas.ewu.edu", KEY)
        self.user = self.canvas.get_current_user()


    def create_calendar_event(self, data):
        #sending calendar event data        
        response = requests.post(self.api_url, headers=self.headers, data=data)
        if response.status_code == 200 or response.status_code == 201:
            return response.json()
        else:  
            response.raise_for_status()

    def format_presentations(self, presentations):
        context_code = f"user_{str(self.user.id)}"
        events = []
        for obj in presentations:
            #key
            title = obj
            #value
            date = presentations[obj]
            day, month = date.split(" ")
            current_year = datetime.now().year
            year = current_year if month in ["Nov","Dec"] else current_year+1
            combined_end_date = datetime.strptime(f'{month} {str(int(day) + 1)} 2023 07:59:59' , '%b %d %Y %H:%M:%S')
            combined_start_date = datetime.strptime(f"{month} {day} 2023 08:00:00", '%b %d %Y %H:%M:%S')
            T_end = str(combined_end_date).replace(" ","T")
            full_time_end = T_end + "Z"
            T_start = str(combined_start_date).replace(" ", "T")
            full_time_start = T_start + "Z" 
            data = {
                "calendar_event[context_code]": context_code,
                "calendar_event[title]": title,
                "calendar_event[start_at]": full_time_start,
                "calendar_event[end_at]": full_time_end
                }
            events.append(data)
        return events
    
    def format_sprints(self, sprints):
        context_code = f"user_{str(self.user.id)}"
        events = []
        trigger = False
        for obj in sprints:
            sprints_title = obj
            sprints_month, sprints_day = sprints[obj]
            current_year = datetime.now().year
            year = current_year if sprints_month in ["Nov","Dec"] else current_year+1
            if not trigger:
                combined_end_date = datetime.strptime(f'{sprints_month} {str(int(sprints_day)+1)} {str(year)} 06:59:59','%b %d %Y %H:%M:%S')
                trigger = True
            else:
                combined_end_date = datetime.strptime(f'{sprints_month} {str(int(sprints_day)+1)} {str(year)} 07:59:59','%b %d %Y %H:%M:%S')
            combined_start_date = datetime.strptime(f"{sprints_month} {sprints_day} 2023 00:00:00", '%b %d %Y %H:%M:%S')

            T_end = str(combined_end_date).replace(" ","T")
            full_time_end = T_end + "Z"
            T_start = str(combined_end_date).replace(" ", "T")
            full_time_start = T_start + "Z"
        # generate calendar event data
            data = {
            "calendar_event[context_code]": context_code,
            "calendar_event[title]": f"Sprint {sprints_title}",
            "calendar_event[start_at]": full_time_start,
            "calendar_event[end_at]": full_time_end
            }
            events.append(data)
        return events

if __name__ == "__main__":
    load_dotenv()
    KEY = os.getenv("API_KEY")
    scrape = Scraper()
    calendar_integration = CalendarIntegration(KEY)

    scrape_url = "http://shelby.ewu.edu/redirect?target=362F1Y6E46462B2B2R0J5V6B121J6U3N"
    html_content = scrape.fetch_data(scrape_url)
    parsed_html = scrape.parse_html(html_content)
    presentations = scrape.extract_presentations(parsed_html)
    sprints = scrape.extract_sprints(parsed_html)

    presentation_events = calendar_integration.format_presentations(presentations)
    for event in presentation_events:
        calendar_integration.create_calendar_event(event)
    
    sprint_events = calendar_integration.format_presentations(sprints)
    for event in sprint_events:
        calendar_integration.create_calendar_event(event)
