import pandas as pd
from datetime import datetime
import pytz
import os
import traceback
import keyring
import config
import re
from scraper import *
from utils import *
from stats import *
from plots import *

if __name__=='__main__':
    if config.query_date==None:
        query_date=datetime.now(pytz.timezone(config.timezone))
        starttime = query_date
    else:
        query_date = pytz.timezone(config.timezone).localize(datetime.strptime(config.query_date,'%m/%d/%Y'))
        starttime = datetime.now(pytz.timezone(config.timezone))
    if config.Web_Scrape=='Y':
        try:
            #__Web_Scraping__#
            print('Perfoming Web Scraping...\n')
            rb=Query_Recent_Bookings(query_clerk=config.query_clerk)
            aai=Query_All_Active_Inmates(query_clerk=config.query_clerk)
            
            if isinstance(rb,pd.DataFrame)==True:
                rb.to_csv(r'../data/recent_bookings_'+query_date.strftime('%b_%d_%Y')+'.csv',index=False)
            if isinstance(aai,pd.DataFrame)==True:
                aai.to_csv(r'../data/active_inmates_'+query_date.strftime('%b_%d_%Y')+'.csv',index=False)
        except Exception as e:
            Error_Log('Web Scraping',traceback.format_exc(),query_date)
            raise e
    elif config.Web_Scrape=='N':
        rb=None
        aai=None
        print('Skipping Web Scraping...\n')
        
    else:
        error='No Y/N indicated whether to Web Scrape in config file. Program killed, please check config.py...'
        Error_Log('Web Scraping',error,query_date)
        raise Exception(error)
    
    
    
    
    
    if config.Calc_Stats=='Y':
        try:
            #__Calculating_Statistics__#
            print('Solving Relevant Statistics...\n')
            if isinstance(rb,pd.DataFrame)==False:
                rb=pd.read_csv('../data/recent_bookings_'+query_date.strftime('%b_%d_%Y')+'.csv')
            if isinstance(aai,pd.DataFrame)==False:
                aai=pd.read_csv('../data/active_inmates_'+query_date.strftime('%b_%d_%Y')+'.csv')
            
            aai_num=['Age','Total Bond','Number of Charges','Number of Misd','Number of Felonies']
            
            Metrics(aai,aai_num,savepath='../tables/metrics.tex')

            Metrics_by_Race_Sex(aai,aai_num,savepath='../tables/')

            Kendall_Tau_by_Race_Sex(aai,aai_num,'../tables/kendall.tex')
            
            ANOVA_1Way_by_Race_Sex(aai,aai_num,'../tables/anova.tex')
        except Exception as e:
            Error_Log('Calculating Statistics',traceback.format_exc(),query_date,r'../misc/error.txt')
            raise e
            
    elif config.Calc_Stats=='N':
        print('Skipping Calculation of Statistics...\n')
    else:
        error='No Y/N indicated whether to Calc Stats in config file. Killing program, please check config.py...'
        Error_Log('Calculating Statistics',error,query_date,r'../misc/error.txt')
        raise Exception(error)
    
    
    
    
    
    if config.Plot_Dists=='Y':
        try:
            #__Plotting_Distributions__#
            print('Plotting Parameter Distributions...\n')
            if isinstance(aai,pd.DataFrame)==False:
                aai=pd.read_csv('../data/active_inmates_'+query_date.strftime('%b_%d_%Y')+'.csv')
            
            #__All_Active_Inmates__#
            Plot_Bar(aai,'Facility','Number of Inmates',savepath='../plots/Facilities.pdf')
            Plot_Age_BoxP_by_Race_Sex(aai,savepath='../plots/Age_BoxP.pdf')
            Plot_TBond_BoxP_by_Race_Sex(aai,savepath='../plots/Tbond_BoxP.pdf')
            Plot_NCharges_BoxP_by_Race_Sex(aai,savepath='../plots/NCharges_BoxP.pdf')
            Plot_NMisd_BoxP_by_Race_Sex(aai,savepath='../plots/NMisd_BoxP.pdf')
            Plot_NFel_BoxP_by_Race_Sex(aai,savepath='../plots/NFel_BoxP.pdf')
            Plot_Race_Pies_by_Sex(aai,'../plots/')
            
        except Exception as e:
            Error_Log('Generating Plots',traceback.format_exc(),query_date,r'../misc/error.txt')
            raise e
            
    elif config.Plot_Dists=='N':
        print('Skipping Plot Generation...\n')
    else:
        error='No Y/N indicated whether to Plot Dists in config file. Killing program, please check config.py...'
        Error_Log('Generating Plots',error,query_date,r'../misc/error.txt')
        raise Exception(error)
        
        
        
        
        
    if config.Gen_Report=='Y':
        try:
            print('Generating Report PDF...\n')
            if isinstance(rb,pd.DataFrame)==False:
                rb=pd.read_csv('../data/recent_bookings_'+query_date.strftime('%b_%d_%Y')+'.csv')
            if isinstance(aai,pd.DataFrame)==False:
                aai=pd.read_csv('../data/active_inmates_'+query_date.strftime('%b_%d_%Y')+'.csv')
            
            cdcmdf_ratio=len(aai[(aai['Facility']=='Correctional Development Center') | (aai['Facility']=='Metro Detention Facility')])/len(aai)
            
            ctd=dict(pd.Series([ct for cts in aai['Charge Types'] if pd.notnull(cts) for ct in cts.split(';')]).value_counts())
            
            drug_p=re.compile('drug|marijuana|cocaine|paraphernalia',re.IGNORECASE)
            ice_p=re.compile('ice - detainer',re.IGNORECASE)
            
            drugc=0
            icec=0
            for n in range(len(aai)):
                if pd.notnull(aai['Charges'][n]):
                    if len(drug_p.findall(aai['Charges'][n]))>0:
                        drugc+=1
                if pd.notnull(aai['Alert Notice'][n]):
                    if len(ice_p.findall(aai['Alert Notice'][n]))>0:
                        icec+=1

            with open(r'../reports/Incarceration_Report_'+query_date.strftime('%b_%d_%Y')+'.tex','w+',encoding='utf-8') as f:
                content=open(config.latex_template).read()
                content=content.replace(r'<<date>>',query_date.strftime('%B %d, %Y'))
                content=content.replace(r'<<Ninmates>>','{:,}'.format(len(aai)))
                content=content.replace(r'<<Ncharges>>','{:,}'.format(ctd['Misdemeanor']+ctd['Felony']))
                content=content.replace(r'<<medNcharges>>',str(np.nanmedian(aai['Number of Charges'])))
                content=content.replace(r'<<medTbond>>','\${:,.2f}'.format(np.nanmedian(aai['Total Bond'])))
                content=content.replace(r'<<Nmisd>>','{:,}'.format(ctd['Misdemeanor']))
                content=content.replace(r'<<Nfel>>','{:,}'.format(ctd['Felony']))
                content=content.replace(r'<<Ndrgoff>>',str(drugc))
                content=content.replace(r'<<Nice>>',str(icec))
                content=content.replace(r'<<Pcdcmdf>>',str(round(cdcmdf_ratio,2)*100))
                content=content.replace(r'<<Nrb>>',str(len(rb)))
                content=content.replace(r'<<Nrbrel>>',str(len(rb[pd.notnull(rb['Release Date'])])))
                content=content.replace(r'<<plot\_outliers>>',str(config.plot_outliers))
                content=content.replace(r'<<plot\_other>>',str(config.plot_other*100))
                content=content.replace(r'<<plot\_other>>',str(config.plot_other*100))
                content=content.replace(r'<<aaifsize>>',str(os.path.getsize('../data/active_inmates_'+query_date.strftime('%b_%d_%Y')+'.csv')/1e3)+' KB')
                content=content.replace(r'<<rbfsize>>',str(os.path.getsize('../data/recent_bookings_'+query_date.strftime('%b_%d_%Y')+'.csv')/1e3)+' KB')
                
                if config.data_web_directory == None:
                    content=content.replace(r'<<dwd>>','')
                else:
                    content=content.replace(r'<<dwd>>',' The data files are publically available at '+config.data_web_directory+'.')
                
                f.write(content)
            
            os.system(r'pdflatex -output-directory ../reports/ ../reports/Incarceration_Report_'+query_date.strftime('%b_%d_%Y')+'.tex')
        except Exception as e:
            Error_Log('Writing Report',traceback.format_exc(),query_date,r'../misc/error.txt')
            raise
            
    if config.Email_Noti=='Y':
        try:
            if pd.isnull(config.user_email):
                print('User email needs to be set in config before sending emails.')
            else:
                password=keyring.get_password('gmail',config.user_email)
                if pd.isnull(password):
                    print('Keyring for secure credentials is not set up. Please run credential.py before attempting to send emails...')
                else:
                    with open(config.email_recipients) as f:
                        addresses = [address.rstrip() for address in f]
                        if len(addresses) > 0:
                            Email_PDF(config.user_email,password,'Incarceration_Report_'+query_date.strftime('%b_%d_%Y'),'../reports/Incarceration_Report_'+query_date.strftime('%b_%d_%Y')+'.pdf',addresses)
                        else:
                            print('There are no email recipients in recipients.txt to send emails to...')
  
        except Exception as e:
            Error_Log('Emailing Notifications',traceback.format_exc(),query_date,r'../misc/error.txt')
            raise e
     
    elif config.Email_Noti=='N':
        print('Skipping Email Notifications...\n')
        
    else:
        error='No Y/N indicated whether to Email Noti in config file. Killing program, please check config.py...'
        Error_Log('Emailing Notifications',error,query_date,r'../misc/error.txt')
    
    print('Code Complete! ','Runtime: ',round((datetime.now(pytz.timezone(config.timezone))-starttime).seconds/60,2),' min')
