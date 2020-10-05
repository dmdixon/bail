Web_Scrape='Y'          #Update latest files with web scraper (Y/N)?
Calc_Stats='Y'          #Calculate relevant statistics for latest files (Y/N)?
Plot_Dists='Y'          #Plot distributions for latest files (Y/N)?
Gen_Report='Y'          #Generate human readable report for latest files (Y/N)?
Email_Noti='N'          #Send email notification/attachments to recipient list (Y/N)? 

timezone='US/Central'   #Timezone used in processing pytz.all_timezones shows all possible timezones
query_clerk=False       #Query clerk court information for each case, Note: takes substantially longer to run

plot_other=0.001        #Less than this fraction is congregated in "Other" for categorical distribution plots
plot_outliers=5         #Symmetric median absolute deviation (mad) clipping for outliers in plots

latex_template='../misc/latex_template.tex'     #Latex template for generating report
data_web_directory=None     #If set adds web link to online data file archive

email_recipients='../misc/email_recipients.txt' #file to append recipient email addresses
user_email=None #user email address used to send email notifications, run credential.py to set up keyring

