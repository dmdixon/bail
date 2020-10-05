# NIDRAA

Hello and thank you for your interest in this project! The Nashville Inmate Data Retrieval And Analysis (NIDRAA) pipeline is a set of python scripts used to regularly scrap information from the Nashville/Davidson County Sheriff’s Office website (http://dcso.nashville.gov/) and output the data in the form of tables, figures and reports. To start with the pipeline has the following dependencies.

Python Dependencies:
*	numpy
*	pandas
*	scipy
*	matplotlib
*	import datetime
*	pytz
*	os
*	traceback
*	keyring
*	re
*	smtplib
*	email
*	itertools
*	string
*	bs4
*	selenium
*	astropy

Note: Code was developed in Python 3.8

Driver Dependencies:
It is necessary to download a Chrome Webdriver to use web scraping functions. Go to https://chromedriver.chromium.org/downloads for download options.

Latex Dependencies:
To create report and convert to pdf, pdflatex is necessary. Any distribution of Latex should work, it just depends on you OS. Go to https://www.latex-project.org/get/ and download which one you need.

The pipeline itself is made up of a set of scripts. The scripts that make it up are as follows.

scraper.py: 
This script contains all the functions for scraping the Sheriff’s Office website. It also contains functions for scraping the Criminal Court Clerk Office (https://ccc.nashville.gov/) given case numbers and/or names. If you just want to get the files and run your own analysis, this is really the only script you need.

main.py:
This script calls some of the functions from scraper.py to generate information csv files for the current inmate population in Nashville/Davidson County and inmates arrested in the last 48 hours. It then generates statistical tables and plots to create a simple report that can be distributed via email. How it does this is determined by config.py.

config.py:
This script is what determines the behavior of main.py. It allows you to skip certain parts of main.py if you determine they are unnecessary or in order to avoid pointlessly redoing steps. It also determines the working time zone, whether to supplement with Criminal Court Clerk Office information, etc. Ideally this should be the only file you need to edit if you are running the pipeline as is without personal edits. The comments in the script should properly explain each variable.

stats.py
This script holds all the functions for calculating statistics that main.py calls.

plots.py
This script holds all the functions for generating plots that main.py calls.

utils.py
This script holds helper functions for dataframe operations, logging errors and email notifications.

credential.py
This script sets up keyring password for sending email. You only need to do this if you want to distribute the report as an email notification. The default setup is to use a gmail account, so it will fail unless you use a gmail account or edit the code to use something else.

The code was developed thanks to the efforts of Code For Nashville (https://www.codefornashville.org/) and the Nashville Community Bail Fund (https://nashvillebailfund.org/). 

For more information about the code feel free to email me at dmdixon1992@gmail.com and I will get back with you as soon as possible. Thank you!  

