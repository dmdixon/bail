import smtplib
import os
import config
from datetime import datetime
import pytz
import itertools
from email.message import EmailMessage

def DCut(dataframe,columns,conditions,values): #Function to more easily conditionally slice dataframe
    for n in range(len(conditions)):
        column=columns[n]
        condition=conditions[n]
        value=values[n]
        if condition=='eq':
            dataframe=dataframe[dataframe[column]==value].reset_index(drop=True)
        elif condition=='ls':
            dataframe=dataframe[dataframe[column]<value].reset_index(drop=True)
        elif condition=='gr':
            dataframe=dataframe[dataframe[column]>value].reset_index(drop=True)
        elif condition=='neq':
            dataframe=dataframe[dataframe[column]!=value].reset_index(drop=True)
        elif condition=='leq':
            dataframe=dataframe[dataframe[column]<=value].reset_index(drop=True)
        elif condition=='geq':
            dataframe=dataframe[dataframe[column]>=value].reset_index(drop=True)
        else: 
            print('Condition not understood, no cuts made...')
    return dataframe

def D_Essemble(dataframe,columns):
    values=list(itertools.product(*[dataframe[column].dropna().unique().tolist() for column in columns]))
    d_enssemble={}
    for value in values:
        df=DCut(dataframe,columns,['eq']*len(columns),value)
        if len(df)>0:
            d_enssemble[value]=DCut(dataframe,columns,['eq']*len(columns),value)
    return d_enssemble


def Email(user_email,password,subject,attachments,addresses):
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login(user_email, password)

    msg = EmailMessage()
    msg['Subject'] = subject

    for attachment in attachments:
        with open(attachment,'r') as f:
            msg.add_attachment(f.read())

    server.sendmail(user_email,','.join(addresses),msg.as_string())
    

def Error_Log(step,trbck,stime,errfile,mxfsize=100):
    ftime=datetime.now(pytz.timezone(config.timezone))

    with open(errfile,'a+') as f:
        fsize=os.path.getsize(errfile)/1e3
        if fsize < mxfsize:
            f.write('#'*30+'\n')
            f.write('Program failed after '+str(round((ftime-stime).seconds/60,2))+' minutes, on '+ftime.strftime('%b %d, %Y %H:%M %p')+' during '+step+' due to the following reason(s): \n')
            f.write('\n'+str(trbck))
            f.write('#'*30+'\n') 
            f.write('\n\n\n')
        else:
            print('Error log is larger than max size. Change max size or clear error log')