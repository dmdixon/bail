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
