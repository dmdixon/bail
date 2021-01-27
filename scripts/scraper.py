from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from datetime import datetime
from astropy.time import Time
import re
import string

options = Options()
options.headless = True

driver = webdriver.Chrome(options=options)
#driver.implicitly_wait(60)

def Query_Case_by_Case_Number(case_number):   #function to look up clerk court information for a given case number and output to dictionary
    #load search page for Nashville/Davidson County criminal court clerk website
    driver.get('https://sci.ccc.nashville.gov/')    
    
    #send query via case/warrant number
    case_number_field=driver.find_element_by_id(id_='warrantNumber') 
    case_number_field.send_keys(case_number)
    case_number_field.send_keys(Keys.ENTER)
    
    try:
        driver.find_element_by_link_text('Case Details').click()
    except:
        print('Case '+str(case_number)+' Not Found...') #returns None if no information for case number is not found
        return None
    
    #if data is found scrap data into proper data types
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
    bond_soup=re.compile('Amount: \$\d[0-9,.]+').findall(str(soup))
    if len(bond_soup)>0:
        bond = float(bond_soup[0].split(': $')[1].replace(',',''))
    else:
        bond=0
        
    # return case infomation as dictionary
    case={'case_number':case_number,'name':name,'oca_id':oca_id,'dob':dob,'case_status':case_status,'defendant_status':defendant_status,'fees':fees,'charge':charge,'bond':bond}
    return case

def Query_Cases_by_Name(last_name,first_name,oca_number=None):  #function to look up clerk court information for case numbers given inmate name
    #load search page for Nashville/Davidson County criminal court clerk website
    driver.get('https://sci.ccc.nashville.gov/')    
    
    #send query via first and last name
    first_name_field=driver.find_element_by_id(id_='firstName')
    last_name_field=driver.find_element_by_id(id_='lastName')

    first_name_field.send_keys(first_name)
    last_name_field.send_keys(last_name)
    last_name_field.send_keys(Keys.ENTER)
    
    #check if query returns table information and return None if not
    soup = BeautifulSoup(driver.page_source,'lxml')
    if soup.find('td').contents[0]=='No results for your criteria. Please search again!': 
        return None
    
    #read in table of names matching the query and the detail web links for each
    person_table = soup.find('table')
    persons=pd.read_html(str(person_table))[0]
    oca_numbers=np.array(persons['OCA Number']).astype(int)
    detail_links=driver.find_elements_by_link_text('Defendant Details')

    #match to oca number if provided.
    if oca_number != None:  
        match_index=np.where(oca_numbers==oca_number)[0]
    else:
        match_index=0
    
    #read cases of matched person and return table 
    detail_links[match_index].click()
    soup = BeautifulSoup(driver.page_source,'lxml')
    case_table=soup.find('table')
    cases= pd.read_html(str(case_table))[0]
    return cases
    
 
def Query_Cases_by_Case_Numbers(case_numbers):   #function to look up information for a list of case numbers and output to dataframe
    #loop Query_Case_by_Case_Number function
    cases=[Query_Case_by_Case_Number(case_number) for case_number in case_numbers]
    
    #remove null results from list and return remainder
    cases=pd.DataFrame(list(filter(None, cases)))
    return cases

def Query_Court_Schedule_by_Date(date,session_type='general'):   #function to look up information for court schedule on a given date and output to dataframe.
    #specify what kind of session to query schedule for
    if session_type=='general':
        driver.get('https://sci.ccc.nashville.gov/Reporting/GeneralSessionsScheduledAppearance')
    elif session_type=='trial':
        driver.get('https://sci.ccc.nashville.gov/Reporting/TrialCourtScheduledAppearance')
    else:
        print('No specified session...')
        return None
    
    #query given date and return schedule information as table
    report_date=driver.find_element_by_id(id_='reportDate')
    report_date.send_keys(date)
    report_date.send_keys(Keys.ENTER)
    soup = BeautifulSoup(driver.page_source,'lxml')
    if soup.find('td').contents[0]=='No results for your criteria. Please search again!':
        return None
    table = soup.find('table')   
    trials=pd.read_html(str(table))[0] 
    trials['Defendant']=trials['Defendant'].str.replace(', ','; ')
    trials['Offense']=trials['Offense'].str.replace(',','')
    trials['Court Room']=trials['Court Room'].str.replace(',','')
    if session_type=='general':
        trials['Judge']=trials['Judge'].str.replace(', ',' ')
        
    return trials

def Query_Court_Schedules_by_Dates(dates,session_type='general'):   #function to look up court schedule for a list of dates and output to dataframe.
    #loop Query_Court_Schedule_by_Date function and return table    
    trials=pd.concat([Query_Court_Schedule_by_Date(date,session_type) for date in dates])
    return trials

def Query_Recent_Bookings(query_clerk=False): #function to look up information for recent bookings and output to dataframe
    #load recent bookings page of sheriff office website
    driver.get('http://dcso.nashville.gov/Search/RecentBookings')
    
    #read in bookings information table for last 48 hours 
    soup = BeautifulSoup(driver.page_source,'lxml')
    table = soup.find('table')   
    recent_bookings=pd.read_html(str(table))[0]
    recent_bookings.drop(columns='Details',inplace=True)
    
    #find detail links for each inmate and loop through to read in information as proper data types
    details_set=soup.findAll('button',{'class':'btn btn-mini'})
    details_urls = ['http://dcso.nashville.gov/'+details.get('onclick').split('=\'')[1].split('\';')[0] for details in details_set]
    for i in range(len(details_urls)):
        driver.get(details_urls[i])
        soup = BeautifulSoup(driver.page_source,'lxml')
        charge_soup=soup.findAll('label', text='Arrested Charge')
        if charge_soup != None:
            charges=[charge.next_sibling.strip() for charge in charge_soup if charge.find_next_sibling() != None]
            charge_types=[charge.find_next_sibling().next_sibling.strip() for charge in charge_soup if charge.find_next_sibling() != None]
        else:
            charges=[]
            charge_types=[]
        bond_soup=soup.findAll('label', text='Bond')
        if bond_soup !=None:
            bonds_list=[bond.next_sibling.strip()[1:].replace(',','') for bond in bond_soup]
            bonds=';'.join(bonds_list)
            try:
                total_bond=np.nansum(list(map(float,bonds_list))) #sometimes bonds_list has empty string
            except:
                total_bond=0
        else:
            bonds=[]
            total_bond=0        
        case_number_soup=soup.findAll('label', text='Warrant')
        if case_number_soup != None:
            case_numbers=[case_number.next_sibling.strip() for case_number in case_number_soup]
        else:
            case_numbers=[]  
        if len(case_numbers) >0:
            clerk_case_numbers=[]
            clerk_bonds=[]
            if query_clerk:
                for case_number in case_numbers:
                    clerk_case=Query_Case_by_Case_Number(case_number)  
                    if clerk_case != None:
                        clerk_case_numbers.append(clerk_case)
                        clerk_bonds.append(clerk_case['bond'])
                        try:
                            clerk_total_bond=np.nansum(list(map(float,clerk_bonds))) #sometimes bonds has empty string
                        except:
                            clerk_total_bond=0
                    else:
                        clerk_bonds=[]
                    clerk_total_bond=0
        else:
            clerk_bonds=[]
            clerk_total_bond=0
            
        alert_soup=soup.find('div',{'class':'alert alert-danger'})
        if alert_soup != None:
            alert=alert_soup.text.strip()
        else:
            alert=''

        recent_bookings.at[i,'Number of Charges']=len(charges)
        recent_bookings.at[i,'Charges']=';'.join(charges)
        recent_bookings.at[i,'Charge Types']=';'.join(charge_types)
        recent_bookings.at[i,'Number of Misd']=charge_types.count('Misdemeanor')
        recent_bookings.at[i,'Number of Felonies']=charge_types.count('Felony')
        recent_bookings.at[i,'Case Numbers']=';'.join(case_numbers)
        recent_bookings.at[i,'Bonds']=';'.join(bonds)
        recent_bookings.at[i,'Total Bond']=total_bond 
        if query_clerk:
            recent_bookings.at[i,'Clerk Bonds']=';'.join(clerk_bonds)
            recent_bookings.at[i,'Clerk Total Bond']=clerk_total_bond
        recent_bookings.at[i,'Alert Notice']=alert
        
    #ensure proper data format for table columns
    recent_bookings['Age']=[int(dob[-3:-1]) if type(dob)==str else np.nan for dob in recent_bookings['Date of Birth']]
    recent_bookings['Inmate Name']=recent_bookings['Inmate Name'].str.replace(u'\xa0', u' ').str.replace(', ','; ')
    recent_bookings['Date of Birth']=recent_bookings['Date of Birth'].str[:-5].str.replace(', ','; ')
    recent_bookings['Admitted Date MJD']=[Time(datetime.strptime(admitted_date,'%b %d, %Y - %H:%M %p')).mjd for admitted_date in recent_bookings['Admitted Date']]
    recent_bookings['Admitted Date']=recent_bookings['Admitted Date'].str.replace(', ','; ')
    recent_bookings['Release Date MJD']=[Time(datetime.strptime(released_date,'%b %d, %Y - %H:%M %p')).mjd if pd.notnull(released_date) else np.nan for released_date in recent_bookings['Release Date']]
    recent_bookings['Release Date']=recent_bookings['Release Date'].str.replace(', ','; ')
    recent_bookings['Charges']=recent_bookings['Charges'].str.replace(re.compile(r'(?<=\d),(?=\d)'),'')
    recent_bookings['Charges']=recent_bookings['Charges'].str.replace(',','-')
    return recent_bookings

def Query_Active_Inmate_by_Name(last_name,first_name=None,query_clerk=False): #function to query sheriff office for inmate via name information
    #load inmate search page on sheriff office website and query for matching names
    driver.get('http://dcso.nashville.gov/Search/')
    if first_name !=None:
        first_name_field=driver.find_element_by_id(id_='firstName')
        first_name_field.send_keys(first_name)
    last_name_field=driver.find_element_by_id(id_='lastName')
    last_name_field.send_keys(last_name)
    last_name_field.send_keys(Keys.ENTER)
    
    #find all matches for query name and loop through detail web links for information
    soup = BeautifulSoup(driver.page_source,'lxml')
    table = soup.find('table',id='results-list')
    if table != None:    
        table=pd.read_html(str(table))[0]
        details_set=soup.findAll('button',{'class':'btn btn-mini'})
        details_urls = ['http://dcso.nashville.gov/'+details.get('onclick').split('=\'')[1].split('\';')[0] for details in details_set]
        for i in range(len(details_urls)):
            driver.get(details_urls[i])
            soup = BeautifulSoup(driver.page_source,'lxml')
            admit_soup=soup.find('label',text='Arrest Booking Date')
            if admit_soup != None:
                admitted_date=admit_soup.next_sibling.strip()
                admitted_date_mjd=Time(datetime.strptime(admitted_date,'%m/%d/%Y %H:%M:%S %p')).mjd
            else:
                admitted_date=''
                admitted_date_mjd=np.nan
            charge_soup=soup.findAll('label', text='Arrested Charge')
            if charge_soup != None:
                charges=[charge.next_sibling.strip() for charge in charge_soup if charge.find_next_sibling() != None]
                charge_types=[charge.find_next_sibling('br').next_sibling.strip() for charge in charge_soup if charge.find_next_sibling() != None]
            else:
                charges=[]
                charge_types=[]
            bond_soup=soup.findAll('label', text='Bond')
            if bond_soup !=None:
                bonds=[bond.next_sibling.strip()[1:].replace(',','') for bond in bond_soup]
                try:
                    total_bond=np.nansum(list(map(float,bonds))) #sometimes bonds has empty string
                except:
                    total_bond=0
            else:
                bonds=''
                total_bond=0
            case_number_soup=soup.findAll('label', text='Warrant')
            if case_number_soup != None:
                case_numbers=[case_number.next_sibling.strip() for case_number in case_number_soup]
            else:
                case_numbers=[]  
            if len(case_numbers) > 0:
                clerk_case_numbers=[]
                clerk_bonds=[]
                # if you want to query clerk court information for each case
                if query_clerk:
                    for case_number in case_numbers:
                        clerk_case=Query_Case_by_Case_Number(case_number)  
                        if clerk_case != None:
                            clerk_case_numbers.append(clerk_case)
                            clerk_bonds.append(str(clerk_case['bond']))
                            try:
                                clerk_total_bond=np.nansum(list(map(float,clerk_bonds))) #sometimes bonds has empty string
                            except:
                                clerk_total_bond=0
                        else:
                            clerk_bonds=[]
                            clerk_total_bond=0
            else:
                clerk_bonds=[]
                clerk_total_bond=0
           
            alert_soup=soup.find('div',{'class':'alert alert-danger'})
            if alert_soup != None:
                alert=alert_soup.text.strip()
            else:
                alert=''
            table.at[i,'Admitted Date']=admitted_date
            table.at[i,'Admitted Date MJD']=admitted_date_mjd
            table.at[i,'Number of Charges']=len(charges)
            table.at[i,'Charges']=';'.join(charges)
            table.at[i,'Charge Types']=';'.join(charge_types)
            table.at[i,'Number of Misd']=charge_types.count('Misdemeanor')
            table.at[i,'Number of Felonies']=charge_types.count('Felony')
            table.at[i,'Case Numbers']=';'.join(case_numbers)
            table.at[i,'Bonds']=';'.join(bonds)
            table.at[i,'Total Bond']=total_bond
            if query_clerk:
                table.at[i,'Clerk Bonds']=';'.join(clerk_bonds)
                table.at[i,'Clerk Total Bond']=clerk_total_bond
            table.at[i,'Alert Notice']=alert
        
        #ensure proper data format for table columns
        table.drop(columns='Details',inplace=True)
        table['Inmate Name']=table['Inmate Name'].str.replace(u'\xa0', u' ').str.replace(', ','; ')
        table['Age']=[int(dob[-3:-1]) if type(dob)==str else np.nan for dob in table['Date of Birth']]
        table['Date of Birth']=table['Date of Birth'].str[:-5].str.replace(', ','; ')
        table['Charges']=table['Charges'].str.replace(re.compile(r'(?<=d),(?=d)'),'')
        table['Charges']=table['Charges'].str.replace(',','-')
  

    return table

def Query_All_Active_Inmates(query_clerk=False): #function to query all active inmates on sheriff office website
    #make list of alphabet letters
    letters=[letter for letter in string.ascii_lowercase]
    
    #loop Query_Active_Inmate_by_Name over each letter to match all names
    master=pd.concat([Query_Active_Inmate_by_Name(letter,query_clerk=query_clerk) for letter in letters]).reset_index(drop=True)
    
    #make sure to drop duplicates in the table
    master.drop_duplicates(subset=['Control Number','Admitted Date']).reset_index(drop=True,inplace=True)
    
    return master
