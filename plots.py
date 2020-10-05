import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from utils import *
import config

#__Distribution_Functions__#
def Plot_Hist(dataframes,columns,linestyles,xlabel,bins,methods,normalize=True,legends=None,axis_space=['linear','linear'],outliers=None,savepath=None): #Function for plotting Histogram(s) on a single figure.
    plt.figure(figsize=(10,8))
    for n in range(len(dataframes)):
        dataframe=dataframes[n]
        column=columns[n]
        linestyle=linestyles[n]
        x=np.array(dataframe[column].dropna().reset_index(drop=True))
        if outliers!=None:
            mad=np.nanmedian(np.abs(x-np.nanmedian(x)))
            x=x[(x<np.nanmedian(x)+config.plot_outliers*mad)&(x>np.nanmedian(x)-config.plot_outliers*mad)]
        
        if methods[n]=='binwidth':
            binwidth=bins[n]
        elif methods[n]=='Nbins':
            binwidth=(np.nanmax(x)-np.nanmin(x))/bins[n] 
            
        print(binwidth)
    
        if normalize==True:
            if legends!=None:
                plt.hist(x,weights=np.ones(len(x))/len(x)*100,histtype='step',linestyle=linestyle,bins=np.arange(np.nanmin(x), np.nanmax(x) + binwidth, binwidth),color='black',label=legends[n])
            else:
                plt.hist(x,weights=np.ones(len(x))/len(x)*100,histtype='step',linestyle=linestyle,bins=np.arange(np.nanmin(x), np.nanmax(x) + binwidth, binwidth),color='black')
        else:
            if legends!=None:
                plt.hist(x,histtype='step',linestyle=linestyle,bins=np.arange(np.nanmin(x), np.nanmax(x) + binwidth, binwidth),color='black',label=legends[n])
            else:
                plt.hist(x,histtype='step',linestyle=linestyle,bins=np.arange(np.nanmin(x), np.nanmax(x) + binwidth, binwidth),color='black')

    
    if all(pd.notnull(legends)):
        plt.legend()
    
    plt.xlabel(xlabel,fontsize=24)
    plt.xscale(axis_space[0])
    plt.yscale(axis_space[1])

    if normalize==True:
        plt.ylabel('Percent %',fontsize=24)
    else:
        plt.ylabel('Counts',fontsize=24)
    plt.tight_layout()
    if savepath != None:
        plt.savefig(savepath,format='pdf')
    plt.show()


def Plot_Culm(dataframes,xcols,ycols,linestyles,xlabel,ylabel,legends=None,axis_space=['linear','linear'],normalize=True,savepath=None): #Function for plotting Culmulative Distribution(s) on a single figure.
    fig,ax = plt.subplots(1,1,figsize=(12,10))
    for n in range(len(dataframes)):
        dataframe=dataframes[n]
        dataframe.sort_values(xcols[n],inplace=True)
        if ycols[n]==None:
            if legends!=None:
                if normalize==True:
                    ax.plot(dataframe[xcols[n]],(np.arange(len(dataframe))+1)/len(dataframe[xcols[n]]),color='black',marker='',linestyle=linestyles[n],label=legends[n])
                else:
                    ax.plot(dataframe[xcols[n]],np.arange(len(dataframe))+1,color='black',marker='',linestyle=linestyles[n],label=legends[n])
            else:
                if normalize==True:
                    ax.plot(dataframe[xcols[n]],(np.arange(len(dataframe))+1)/len(dataframe[xcols[n]]),color='black',marker='',linestyle=linestyles[n])
                else:
                    ax.plot(dataframe[xcols[n]],np.arange(len(dataframe))+1,color='black',marker='',linestyle=linestyles[n])
        else:
            if legends!=None:
                if normalize==True:
                    ax.plot(dataframe[xcols[n]],np.cumsum(dataframe[ycols[n]])/len(dataframe[xcols[n]]),color='black',marker='',linestyle=linestyles[n],label=legends[n])
                else:
                    ax.plot(dataframe[xcols[n]],np.cumsum(dataframe[ycols[n]]),color='black',marker='',linestyle=linestyles[n],label=legends[n])

            else:
                if normalize==True:
                    ax.plot(dataframe[xcols[n]],np.cumsum(dataframe[ycols[n]])/len(dataframe[xcols[n]]),color='black',marker='',linestyle=linestyles[n])
                else:
                    ax.plot(dataframe[xcols[n]],np.cumsum(dataframe[ycols[n]]),color='black',marker='',linestyle=linestyles[n])

    ax.set_xlabel(xlabel,fontsize=24)
    ax.set_ylabel(ylabel,fontsize=24)
    plt.xscale(axis_space[0])
    plt.yscale(axis_space[1])
    if legends !=None:
        plt.legend(fontsize=24)
    plt.tight_layout()
    if savepath != None:
        plt.savefig(savepath,format='pdf')
    plt.show()
    
def Plot_Bar(dataframe,column,ylabel,savepath=None):
     d=dict(dataframe[column].value_counts())
     plt.figure(figsize=(14,14))
     plt.bar(list(d.keys()),list(d.values()),color='green',alpha=.3)
     plt.legend(loc='best', fontsize=30)
     plt.ylabel(ylabel,fontsize=30)
     plt.xticks(rotation=15)
     plt.tight_layout()
     if savepath!=None:
        plt.savefig(savepath,format='pdf')
     plt.show()
        
def Plot_BoxP(dataframe,columns,distr,outliers,other=.01,savepath=None):
    df_dict=D_Essemble(dataframe,columns)
    df_distrs=[]
    labels=[]
    for key in df_dict.keys():
        df_distr=df_dict[key][distr]
        if outliers!=None:
            mad=np.nanmedian(np.abs(df_distr-np.nanmedian(df_distr)))
            df_distr=df_distr[(df_distr<np.nanmedian(df_distr)+config.plot_outliers*mad)&(df_distr>np.nanmedian(df_distr)-config.plot_outliers*mad)]
        if len(df_distr)/len(dataframe) > other:
             df_distrs.append(df_distr)
             labels.append(key)
    plt.figure(figsize=(10,12))
    plt.boxplot(df_distrs,showmeans=True,vert=0,labels=labels)
    matplotlib.rcParams['xtick.labelsize'] = 20
    matplotlib.rcParams['ytick.labelsize'] = 20 
    plt.xlabel(distr)
    plt.yticks(rotation=30)
    plt.tight_layout()
    if savepath!=None:
        plt.savefig(savepath,format='pdf')
    plt.show()
    
def Plot_Pies(dataframes,columns,usevals=None,other=.01,suptitles='None',savepath=None): #Function for plotting pie chart distribution of a given column.
    matplotlib.rcParams['font.size'] = 28
    
    for n in range(len(dataframes)):
        dataframe=dataframes[n]
        if usevals != None:
            index_list=[]
            for val in usevals:
                index=np.where(dataframe[column]==val)[0]
                index_list.append(index)
            dataframe=dataframe.iloc[np.concatenate(index_list)].reset_index(drop=True)
        
        for column in columns:
            vcnts=dict(dataframe[column].value_counts())
            if other!=None:
                other_count=0
                drop_list=[]
                for key in vcnts.keys():
                    frac=vcnts[key]/np.sum(list(vcnts.values()))
                    if frac < other:
                        other_count+=vcnts[key]
                        drop_list.append(key)
                for key in drop_list:
                    del vcnts[key]
                if other_count!=0:
                    vcnts['Other']=other_count
            plt.figure(figsize=(10,8))
            pd.Series(vcnts).plot.pie(autopct='%.2f%%',textprops=dict(ha='center',va='center'))
            plt.plot()
            plt.ylabel('')
            if suptitles!=None:
                plt.suptitle(suptitles[n])
            plt.tight_layout()
            if savepath != None:
                plt.savefig(savepath+'_'.join(suptitles[n].split())+'.pdf',format='pdf')
            plt.show()
 
    
def Plot_Race_Pies_by_Sex(dataframe,savepath=None):
    Plot_Pies([DCut(dataframe,['Sex'],['eq'],['M']),DCut(dataframe,['Sex'],['eq'],['F']),dataframe],['Race'],usevals=None,other=.01,suptitles=['Race Distribution (Men)','Race Distribution (Women)','Race Distribution (Total)'],savepath=savepath)
  
def Plot_Age_BoxP_by_Race_Sex(dataframe,savepath=None):
    Plot_BoxP(dataframe,['Race','Sex'],'Age',config.plot_outliers,config.plot_other,savepath=savepath) 

def Plot_TBond_BoxP_by_Race_Sex(dataframe,savepath=None):
    Plot_BoxP(dataframe,['Race','Sex'],'Total Bond',config.plot_outliers,config.plot_other,savepath=savepath)
    
def Plot_NCharges_BoxP_by_Race_Sex(dataframe,savepath=None):
    Plot_BoxP(dataframe,['Race','Sex'],'Number of Charges',config.plot_outliers,config.plot_other,savepath=savepath)

def Plot_NMisd_BoxP_by_Race_Sex(dataframe,savepath=None):
    Plot_BoxP(dataframe,['Race','Sex'],'Number of Misd',config.plot_outliers,config.plot_other,savepath=savepath)

def Plot_NFel_BoxP_by_Race_Sex(dataframe,savepath=None):
    Plot_BoxP(dataframe,['Race','Sex'],'Number of Felonies',config.plot_outliers,config.plot_other,savepath=savepath)
