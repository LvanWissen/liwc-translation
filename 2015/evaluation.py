import numpy as np
import pandas as pd
import os
from scipy.stats import spearmanr, pearsonr
import matplotlib.pyplot as plt
plt.style.use('ggplot')

def cohens_d(df0, df1):
    """Calculate effect size between two dataframes"""
    return abs(df0.mean() - df1.mean()) / (np.sqrt((df0.std() ** 2 + df1.std() ** 2) / 2))

def pval(df0, df1):
    """
    Calculate correlation, p-value and best method for two dataframes
    
    Reurns new dataframe with columns 'corr, method, pval'
    """
    colnames = df0.columns
    df = pd.DataFrame()
    methods = []
    corrs = []
    
    for c in colnames:
        if -1.5 < df0[c].skew() < 1.5 and -1.5 < df1[c].skew() < 1.5:
            method = 1  # pearson
            corr, p = pearsonr(df0[c].T, df1[c].T)
        else:
            method = 2  # spearman
            
            corr, p = spearmanr(df0[c], df1[c])

        df.insert(0, c, [p])
        methods.append(method)
        corrs.append(corr)
        
    methods = list(reversed(methods))
    corrs = list(reversed(corrs))
   
    df = df.T
    df.insert(0, 'method', methods)
    df.insert(0, 'corr', corrs)
    df.columns = ['corr', 'method', 'pval']
    return df

def stats(df0, df1):
    """
    Building statistics df.
    """

    df = pval(df0, df1)
    df.insert(0, 'effect', cohens_d(df0, df1))

    df.insert(0, 'skew_nl', df1.skew())
    df.insert(0, 'max_nl', df1.max())
    df.insert(0, 'min_nl', df1.min())
    df.insert(0, 'median_nl', df1.median())

    df.insert(0, 'skew_en', df0.skew())
    df.insert(0, 'max_en', df0.max())
    df.insert(0, 'min_en', df0.min())
    df.insert(0, 'median_en', df0.median())

    return df

def evaluate(results_en, results_trans, run):
    """
    """

    rundir = os.path.join('runs', run)

    df0 = pd.read_csv(results_en, sep='\t', index_col='Filename').sort_index()
    df2 = pd.read_csv(results_trans, sep='\t', index_col='Filename').sort_index()

    # Drop files with low WC
    for ien, inl in zip(df0.index, df2.index):

        if float(df0.get_value(ien, 'WC')) < 999 \
        or float(df2.get_value(inl, 'WC')) < 999:
            ien = list(df0.index).index(ien)
            df0.drop(df0.index[[ien]], inplace=True)

            inl = list(df2.index).index(inl)
            df2.drop(df2.index[[inl]], inplace=True)


    # correlation
    en_nlaut = stats(df0,df2)

    plot2 = en_nlaut['corr']

    avg_corr_en_nlaut = round(en_nlaut['corr'].mean(), 4)

    df = pd.concat([plot2], axis=1)
    df.columns = ['EN-NL_aut: {}'.format(avg_corr_en_nlaut)]

    ax = df.plot(kind='barh', figsize=(5,25), title='Correlation').legend(loc='lower center', bbox_to_anchor=(0.5, -0.05))
    fig = ax.get_figure()
    fig.savefig(os.path.join(rundir, 'correlation.png'))

    # effect
    plot2 = en_nlaut['effect']

    avg_effect_en_nlaut = round(en_nlaut['effect'].mean(),4)

    df = pd.concat([plot2], axis=1)
    df.columns = ['EN-NL_aut: {}'.format(avg_effect_en_nlaut)]

    ax = df.plot(kind='barh', figsize=(5,25), title='Effect size', xlim=(0,4)).legend(loc='lower center', bbox_to_anchor=(0.5, -0.05))
    fig = ax.get_figure()
    fig.savefig(os.path.join(rundir, 'effect.png'))

    s1 = stats(df0,df2)
    s1.to_csv(os.path.join(rundir, 'stats_en_nlaut.csv'), sep=';', decimal=',')

    return avg_corr_en_nlaut, avg_effect_en_nlaut

if __name__ == "__main__":
    avg_corr, avg_eff = evaluate('runs/results_2015-08-24-LIWC2015 Dictionary - Internal.dic.csv', 'runs/201703221814/results_201703221814.dic.csv', '201703221814')

    avg_corr = str(avg_corr).replace('.', ',')
    avg_eff = str(avg_eff).replace('.', ',')

    print(avg_corr, avg_eff)