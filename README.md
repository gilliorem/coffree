# MY SUTD DAILY FREE COFFEE

*This project is part of the SUTD Academy Program AI Task force*

My SUTD Daily Coffee is an app that provide daily location with free coffee for student via Telegram.

## Context
As an APM (Assistant to the Programme Manager) in SUTD, I have access to the daily workshops in the university. During these workshops, foods and beverage is being provided for the participants.
All the time, there is some overdue and lots of coffee ends up being wasted.
To prevent that, I want to share the coffee locations across the school, so the student can come and help themselves.

## Architecture and environment

### THE COFFEE LOCATION 'BACKEND'
- `https://sutdapac.sharepoint.com/:x:/s/SUTDAcademy-ProgrammeManagement/IQDwDO9sgw_CQrrBruTXIhvEAdJiAU3n33cGgIIq984tabE?e=iyV4fX&nav=MTVfezBCOTkxM0M1LTQ0RkEtNDJGMi1CRTM5LTM1RDdBRjA5NDdDN30`

this links to the shaired schedule with other APMs. this is my entry point, where I can see the location of daily coffee:
For example the 1100th row looks like this:
PDStory IMDA	TT19	ST	ST	ST	CVP	Zoom	TT	TT		AIFE	TT24/25	RG	RG	RG	IDS OCBC	TT20	JT	JT	JT

the format of the sheet is 

WORKSHOP NAME | LOCATION | APM's name | APM's name | APM's name | WORKSHOP NAME | LOCATION | APM's name | APM's name | APM's name | 

The format is not strict and not always like that because class like 'Zoom' will not have a location.
Here is the first row of the schedule sheet:
CLASSROOM	"Shift 1 8am - 9.30am"	"Shift 2 12.30pm - 2pm"	"Shift 3 4.30pm - 6pm"	EVENT 2	CLASSROOM	Shift 1	Shift 2	Shift 3	EVENT 3	CLASSROOM	Shift 1	Shift 2	Shift	

*most of the time the location will start with 'TT' follow by a number* but it can also be *Comp LAB* or *2.612A* or *Offsite*(should be ignored)

it is in this document that I can access the worshop location


### THE TELEGRAM BOT 'FRONT END'
I call this the front end because it will be the main user interface:
A Telegram bot that will text the student will the location of the daily free coffee.
The Telegram bot will text the user every morning, so it will be some kind 


## STEP BY STEP PROCESS

- Fetch the location data *Different options* 
    1st option: read the data from the sharepoint directly (using the excel sharepoint API if possible)
    2nd option: make a copy of that file, save it as a csv, read the data from this local csv file
    3rd option: scrap the webpage and collect the data by parsing the html webpage

- Transfer the data to the Frontend user (Telegram)
    For that part I am actually not to sure of how it would work: I would assume the Telegram bot is going to have access to the 'backend data' (which is the csv/datasheet).

