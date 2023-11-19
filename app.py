from dotenv import load_dotenv
import os, requests, json
from bs4 import BeautifulSoup
from canvasapi import Canvas, calendar_event
from datetime import datetime
from datetime import date


load_dotenv()
KEY = os.getenv("API_KEY")

'''
scraping assignment titles and due dates from shelby
'''
def scrape():
    presentations = {}
    sprints = {}
    shelby = requests.get("http://shelby.ewu.edu/redirect?target=362F1Y6E46462B2B2R0J5V6B121J6U3N")
    assignments = shelby.text.split("</tr>")
    for i in assignments:
        soup = BeautifulSoup(i, "html.parser")

        '''
        grabbing presentation titles and due dates 
        '''
        title = soup.find('td', class_='course__task_title')
        date = soup.find("td", class_='course__task_actual')
        '''
        grabbing sprint due dates
        '''
        sprint_number = soup.find("td", class_='course__status_report_sprint_number')
        sprint_day = soup.find("td", class_='course__status_report_date_day')
        sprint_month = soup.find('td', class_='course__status_report_date_month')
        
        if title and date:
            # adjust this if you're in group A
            if 'Group B' in title.text:
                stripped_title = title.text.strip()
                stripped_date = date.text.strip()
                presentations[stripped_title] = stripped_date
        # place sprint blocks in a dictionary
        if sprint_number and sprint_day and sprint_month:
            stripped_sprint_number = sprint_number.text.strip()
            stripped_sprint_day = sprint_day.text.strip()
            stripped_sprint_month = sprint_month.text.strip()
            sprints[stripped_sprint_number] = stripped_sprint_month,stripped_sprint_day
    
    return presentations, sprints

'''
interacting with the canvas web api to insert due dates into canvas
this way I will not forget to turn in assignments on time (hopefully)
4044282
'''
def integration(presentations, sprints):
    api_url = "https://canvas.ewu.edu/api/v1/calendar_events"
    canvas = Canvas("https://canvas.ewu.edu", KEY)
    user = canvas.get_current_user()
    context_code = f"user_{str(user.id)}"
    # this is your API key
    headers = {
    "Authorization": f"Bearer {KEY}"
    }

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
        #generating calendar event data
        data = {
        "calendar_event[context_code]": context_code,
        "calendar_event[title]": title,
        "calendar_event[start_at]": full_time_start,
        "calendar_event[end_at]": full_time_end
        }
        #sending calendar event data        
        response = requests.post(api_url, headers=headers, data=data)
        if response.status_code == 200 or response.status_code == 201:
            print("Event created successfully")
            print(response.json())
        else:  
            print(f"Failed to create event. Status code: {response.status_code}")
            print(response.text) 
    
    # crude attempt at fixing daylight savings
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
        # send post request        
        response = requests.post(api_url, headers=headers, data=data)
        if response.status_code == 200 or response.status_code == 201:
            print("Event created successfully")
            print(response.json())
        else:
            print(f"Failed to create event. Status code: {response.status_code}")
            print(response.text)

if __name__ == "__main__":
    presentations, sprints = scrape()
    #print(sprints)
    integration(presentations, sprints)
