import os
import numpy as np
import pandas as pd
from scipy.stats import f_oneway
from scipy.stats import kendalltau
import statsmodels.stats.multicomp as multi
from utils import *


#def Frequency(dataframe):
    
def Metrics(dataframe,columns,savepath=None):
    metrics=pd.DataFrame()
    for column in columns:

        data=dataframe[column]
        
        #__Average__Statistics__#
        metrics.at['mean',column]='{:,.2f}'.format(np.nanmean(data))
        metrics.at['median',column]='{:,.2f}'.format(np.nanmedian(data))
        
        #__Dispersion_Statistics__#
        metrics.at['standard deviation',column]='{:,.2f}'.format(np.nanstd(data))
        metrics.at['iqr',column]='{:,.2f}'.format(np.nanquantile(data,.75)-np.nanquantile(data,.25))
        
        #__Extrema_Statistics__#
        metrics.at['min',column]='{:,.2f}'.format(np.nanmin(data))
        metrics.at['max',column]='{:,.2f}'.format(np.nanmax(data))
    
    metrics=metrics.round(3)
    if savepath != None:
        metrics.to_latex(savepath)
    return metrics

def Kendall_Tau(dataframe,savepath=None):
    corrs = pd.DataFrame()
    
    for index in dataframe.columns:
        for column in dataframe.columns:
            tau,pval=kendalltau(dataframe[index],dataframe[column])
            if pval <1e-6:
                corrs.at[index,column]=', '.join(['T'+': '+'{:,.3f}'.format(tau),r'p: 1e-6'])
            else:
                corrs.at[index,column]=', '.join(['T'+': '+'{:,.3f}'.format(tau),r'p: '+'{:.2e}'.format(pval)])
    if savepath != None:
        corrs.to_latex(savepath,encoding='utf-8')
    return corrs

def ANOVA_1Way(dataframe,cat_cols,distr_cols,savepath=None):
    corrs=pd.DataFrame()
    for distr_col in distr_cols:
        for cat_col in cat_cols:
            values=dataframe[cat_col].dropna().unique().tolist()
            distr=[np.array(DCut(dataframe,[cat_col],['eq'],[value])[distr_col]) for value in values]
            fstat,pval=f_oneway(*distr)
            if pval < 1e6:
                corrs.at[cat_col,distr_col]=', '.join(['F'+': '+'{:,.3f}'.format(fstat),r'p: 1e-6'])
            else:
                corrs.at[cat_col,distr_col]=', '.join(['F'+': '+'{:,.3f}'.format(fstat),r'p: '+'{:.2e}'.format(pval)])
            posthoc=multi.pairwise_tukeyhsd(dataframe[distr_col],dataframe[cat_col],alpha=.05)
            posthoc=pd.DataFrame(posthoc._results_table.data[1:], columns=posthoc._results_table.data[0])
            if savepath != None:
                savename=os.path.dirname(savepath)+'/'+distr_col+'_'+cat_col+'_tukeyhsd.tex'
                posthoc.to_latex(savename.replace(' ','_'),index=False,encoding='utf-8')
    if savepath != None:
        corrs.to_latex(savepath,encoding='utf-8')
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
    corrs=Kendall_Tau(dataframe,savepath)
    return corrs

def ANOVA_1Way_by_Race_Sex(dataframe,columns,savepath=None):
   anova=ANOVA_1Way(dataframe,['Race','Sex'],columns,savepath)
   return anova
