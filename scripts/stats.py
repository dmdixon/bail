import numpy as np
import pandas as pd
from scipy.stats import f_oneway
from utils import *


#def Frequency(dataframe):
    
def Metrics(dataframe,columns,savepath=None):
    metrics=pd.DataFrame()
    for column in columns:

        data=dataframe[column]
        
        #__Average__Statistics__#
        metrics.at['mean',column]=str(round(np.nanmean(data),2))
        metrics.at['median',column]=str(np.nanmedian(data))
        
        #__Dispersion_Statistics__#
        metrics.at['standard deviation',column]=str(round(np.nanstd(data),2))
        metrics.at['iqr',column]=str(np.nanquantile(data,.75)-np.nanquantile(data,.25))
        
        #__Extrema_Statistics__#
        metrics.at['min',column]=str(np.nanmin(data))
        metrics.at['max',column]=str(np.nanmax(data))
    
    metrics=metrics.round(3)
    if savepath != None:
        metrics.to_latex(savepath)
    return metrics

def Kendall_Tau(dataframe,savepath=None):
    corr=dataframe.corr(method='kendall')
    corr=corr.round(3)
    if savepath != None:
        corr.to_latex(savepath)
    return corr

def ANOVA_1Way(dataframe,cat_cols,distr_cols,savepath=None):
    corrs=pd.DataFrame()
    for distr_col in distr_cols:
        for cat_col in cat_cols:
            values=dataframe[cat_col].dropna().unique().tolist()
            distr=[np.array(DCut(dataframe,[cat_col],['eq'],[value])[distr_col]) for value in values]
            corrs.at[cat_col,distr_col]=f_oneway(*distr)[0]
    corrs=corrs.round(3)
    if savepath != None:
        corrs.to_latex(savepath)
    return corrs


def Metrics_by_Race_Sex(dataframe,columns,savepath=None):
    df_dict=D_Essemble(dataframe,['Race','Sex'])
    metrics={}
    for key in df_dict.keys():
        metrics[key]=Metrics(df_dict[key],columns)
        metrics[key].to_latex(savepath+('_'.join(key))+'.tex')
    return metrics


def Kendall_Tau_by_Race_Sex(dataframe,columns,savepath=None):
    dataframe=dataframe[columns]
    corr=Kendall_Tau(dataframe)
    if savepath != None:
        corr.to_latex(savepath)
    return corr

def ANOVA_1Way_by_Race_Sex(dataframe,columns,savepath=None):
   anova=ANOVA_1Way(dataframe,['Race','Sex'],columns)
   if savepath != None:
       anova.to_latex(savepath)
   return anova
            

    
