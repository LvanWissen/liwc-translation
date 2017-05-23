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

    df.insert(0, 'skew_aut', df1.skew())
    df.insert(0, 'max_aut', df1.max())
    df.insert(0, 'min_aut', df1.min())
    df.insert(0, 'median_aut', df1.median())

    df.insert(0, 'skew_man', df0.skew())
    df.insert(0, 'max_man', df0.max())
    df.insert(0, 'min_man', df0.min())
    df.insert(0, 'median_man', df0.median())

    return df

def evaluate(results_en, results_nl, results_trans, run):
    """
    """

    rundir = os.path.join('runs', run)

    df0 = pd.read_csv(results_en, sep='\t', index_col='Filename').sort_index()
    df1 = pd.read_csv(results_nl, sep='\t', index_col='Filename').sort_index()
    df2 = pd.read_csv(results_trans, sep='\t', index_col='Filename').sort_index()

    # Drop files with low WC
    for i in df0.index:
        if float(df0.get_value(i, 'WC')) < 999 \
        or float(df0.get_value(i, 'WC')) < 999 \
        or float(df0.get_value(i, 'WC')) < 999:
            i = list(df0.index).index(i)
            df0.drop(df0.index[[i]], inplace=True)
            df1.drop(df1.index[[i]], inplace=True)
            df2.drop(df2.index[[i]], inplace=True)


    # correlation
    en_nlman = stats(df0,df1)
    en_nlaut = stats(df0,df2)

    plot1 = en_nlman['corr']
    plot2 = en_nlaut['corr']

    avg_corr_en_nlman = round(en_nlman['corr'].mean(), 4)
    avg_corr_en_nlaut = round(en_nlaut['corr'].mean(), 4)

    df = pd.concat([plot1, plot2], axis=1)
    df.columns = ['EN-NL_man: {}'.format(avg_corr_en_nlman), 'EN-NL_aut: {}'.format(avg_corr_en_nlaut)]

    ax = df.plot(kind='barh', figsize=(5,25), title='Correlation').legend(loc='lower center', bbox_to_anchor=(0.5, -0.05))
    fig = ax.get_figure()
    fig.savefig(os.path.join(rundir, 'correlation.png'))

    # effect
    plot1 = en_nlman['effect']
    plot2 = en_nlaut['effect']

    avg_effect_en_nlman = round(en_nlman['effect'].mean(),4)
    avg_effect_en_nlaut = round(en_nlaut['effect'].mean(),4)

    df = pd.concat([plot1, plot2], axis=1)
    df.columns = ['EN-NL_man: {}'.format(avg_effect_en_nlman), 'EN-NL_aut: {}'.format(avg_effect_en_nlaut)]

    ax = df.plot(kind='barh', figsize=(5,25), title='Effect size', xlim=(0,4)).legend(loc='lower center', bbox_to_anchor=(0.5, -0.05))
    fig = ax.get_figure()
    fig.savefig(os.path.join(rundir, 'effect.png'))

    s0 = stats(df0,df1)
    s0.to_csv(os.path.join(rundir, 'stats_en_nlman.csv'), sep=';', decimal=',')

    s1 = stats(df0,df2)
    s1.to_csv(os.path.join(rundir, 'stats_en_nlaut.csv'), sep=';', decimal=',')

    s0 = stats(df2,df1)
    s0.to_csv(os.path.join(rundir, 'stats_nlman_nlaut.csv'), sep=';', decimal=',')

    return avg_corr_en_nlaut, avg_effect_en_nlaut

if __name__ == "__main__":
    avg_corr, avg_eff = evaluate('runs/results_LIWC2007_English080730_utf8.dic.csv', 'runs/results_Dutch_LIWC2007_Dictionary_final_utf8.dic.csv', 'runs/201701271218/results_201701271218.dic.csv', '201701271218')

    avg_corr = str(avg_corr).replace('.', ',')
    avg_eff = str(avg_eff).replace('.', ',')

    print(avg_corr, avg_eff)