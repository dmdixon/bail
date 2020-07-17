# -*- coding: utf-8 -*-
"""
Created on Fri Jul 10 19:28:53 2020

@author: dmdixon
"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from datetime import datetime
from datetime import timedelta




options = Options()
options.headless = True

driver = webdriver.Chrome(options=options)

def Query_Case(case_number):
    driver.get('https://sci.ccc.nashville.gov/')
    search_type=driver.find_element_by_id(id_='search-type')
    search_type.send_keys('Case Number')
    case_number_field=driver.find_element_by_id(id_='warrantNumber')
    case_number_field.send_keys(case_number)
    case_number_field.send_keys(Keys.ENTER)
    try:
        driver.find_element_by_link_text('Case Details').click()
    except:
        print('Case '+str(case_number)+' Not Found...')
        return None
    soup = BeautifulSoup(driver.page_source,'lxml')
    id_soup=driver.find_element_by_xpath('/html/body/div[3]/div[2]/div[1]/div/div[1]/div').text.split('\n')
    name=id_soup[0]
    dob,oca_id=id_soup[1].split('-')
    dob=dob.split(':')[1].strip()
    oca_id=oca_id.split(':')[1].strip()
    status_soup=soup.find('span',{'class':'case-status'}).text.split('\n')
    status=[s.strip() for s in status_soup if s.strip()]
    case_status=status[0].split(': ')[1]
    defendant_status=status[1].split(': ')[1]
    try:
        fees=float(status[2].split()[-1].split('$')[1].replace(',',''))
    except:
        fees=0
    charge=soup.find('span',{'class':'charge-description'}).text.strip()
    bond=float(driver.find_element_by_xpath('//*[@id="main"]/div[2]/div[2]/div/div[1]/ul[2]/li[2]').text.split(': $')[1].replace(',',''))
    case={'case_number':case_number,'name':name,'oca_id':oca_id,'dob':dob,'case_status':case_status,'defendant_status':defendant_status,'fees':fees,'charge':charge,'bond':bond}
    return case
 
def Query_Cases(case_numbers):
    cases=[Query_Case(case_number) for case_number in case_numbers]
    cases=pd.DataFrame(list(filter(None, cases)))
    return cases

def Query_Court_Schedule(date,session_type='general'):
    if session_type=='general':
        driver.get('https://sci.ccc.nashville.gov/Reporting/GeneralSessionsScheduledAppearance')
    elif session_type=='trial':
        driver.get('https://sci.ccc.nashville.gov/Reporting/TrialCourtScheduledAppearance')
    else:
        print('No specified session...')
        return None
    report_date=driver.find_element_by_id(id_='reportDate')
    report_date.send_keys(date)
    report_date.send_keys(Keys.ENTER)
    soup = BeautifulSoup(driver.page_source,'lxml')
    if soup.find('td').contents[0]=='No results for your criteria. Please search again!':
        return None
    table = soup.find('table')   
    trials=pd.read_html(str(table))[0]  
    return trials

def Query_Court_Schedules(dates,session_type='general'):
    trials=pd.concat([Query_Court_Schedule(date,session_type) for date in dates])
    return trials

def Query_Recent_Bookings():
    driver.get('http://dcso.nashville.gov/Search/RecentBookings')
    soup = BeautifulSoup(driver.page_source,'lxml')
    table = soup.find('table')   
    recent_bookings=pd.read_html(str(table))[0]
    recent_bookings.drop(columns='Details',inplace=True)
    details_set=soup.findAll('button',{'class':'btn btn-mini'})
    details_urls = ['http://dcso.nashville.gov/'+details.get('onclick').split('=\'')[1].split('\';')[0] for details in details_set]
    for i in range(len(details_urls)):
        driver.get(details_urls[i])
        soup = BeautifulSoup(driver.page_source,'lxml')
        charge_soup=soup.findAll('label', text='Arrested Charge')
        charges=','.join([charge.next_sibling.strip() for charge in charge_soup])
        charge_types=','.join([charge.find_next_sibling('br').next_sibling.strip() for charge in charge_soup])
        bond_soup=soup.findAll('label', text='Bond')
        bonds_list=[bond.next_sibling.strip()[1:].replace(',','') for bond in bond_soup]
        bonds=','.join(bonds_list)
        total_bond=np.nansum(list(map(float,bonds_list)))
        case_number_soup=soup.findAll('label', text='Warrant')
        case_numbers=','.join([case_number.next_sibling.strip() for case_number in case_number_soup])
        
        recent_bookings.at[i,'Number of Charges']=len(charges.split(','))
        recent_bookings.at[i,'Charges']=charges
        recent_bookings.at[i,'Charge Types']=charge_types
        recent_bookings.at[i,'Case Numbers']=case_numbers
        recent_bookings.at[i,'Bonds']=bonds 
        recent_bookings.at[i,'Total Bond']=total_bond         
    return recent_bookings