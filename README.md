# Overview

This project aims integrate due dates from the senior project website designed by Professor Dan Tappen into Canvas. 
I wrote this specifically because I continuously forget to check the website.

# Installation

To get this working you need to generate an access token for your account in Canvas.
```
Account -> Settings -> New Access Token
```
Save this access token inside a file that you will create inside the project directory named ".env"
```
API_KEY = "KEY HERE"
```

To make things easy:
```
git clone https://github.com/alhumaw/shelby2canvas
cd shelby2canvas
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo "API_KEY=KEYHERE" > .env
python3 app.py
```

# Current Issues
The project does not always account for daylight savings time.

