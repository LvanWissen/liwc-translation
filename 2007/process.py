import csv
import itertools
from LIWCtools.LIWCtools import *
from functools import partial
from multiprocessing import Pool, freeze_support


def process(run, dictionarypath, testfilesdir, filepath=None):
    """
    Process on some test files (a parallel corpus for example).
    :param run: runid
    :param dictionarypath: where is the test dictionary located?
    :param testfilesdir: where are the test files?
    :param filepath: where to store the result (percentages and counts)
    :return:
        filepath to results
    """
    pool = Pool(os.cpu_count() - 1)
    freeze_support()

    LD = LDict(dictionarypath)

    all_filenames = []
    for root, dirs, files in os.walk(testfilesdir):
        filenames = [os.path.join(root, file) for file in files]

        all_filenames += filenames

    func = partial(getcounts, LD=LD)
    outputs = pool.map(func, all_filenames)

    root, dictionary = os.path.split(dictionarypath)

    if not filepath:
        filepath = os.path.join('runs', run, 'results_' + dictionary + '.csv')
        filepath_counts = os.path.join('runs', run, 'counts_' + dictionary + '.zip')
    else:
        filepath_counts = os.path.join('runs', 'counts_' + dictionary + '.zip')

    with open(filepath, 'w', encoding='utf-8') as csvfile:
        columns = LD.catDict.getCatDescList()
        columns.insert(0, 'WC')
        columns.insert(0, 'Filename')
        dictwriter = csv.DictWriter(csvfile, fieldnames=columns, restval=0, lineterminator='\n', delimiter='\t')

        dictwriter.writeheader()
        dictwriter.writerows(outputs)

    # counts
    print("Computing the most frequent word for each category...")

    cr = LD.LDictCount(all_filenames)

    cr.write(filepath_counts, dictionary)

    print(filepath_counts)
    return filepath


def getcounts(file, LD):
    """
    """

    with open(file, encoding='utf-8') as infile:
        string = infile.read()

    counts = LD.LDictCountString(string)

    returndict = dict(counts)
    for k, v in returndict.items():
        if k == 'WC':
            continue
        returndict[k] = v / returndict['WC']
    returndict['Filename'] = file

    return returndict


def gethtmlcounts(dict_nl, dict_trans, matchfile, rundir):
    """
    Generate HTML compare file with differences between each category.
    :param dict_nl:
    :param dict_trans:
    :return:
    """

    LDM = LDictMatch(matchfile)

    LDold = LDict(dict_nl)
    LDnew = LDict(dict_trans)

    LDM.HtmlView(os.path.join(rundir, 'compare.html'), LDold, LDnew)


def gethtmlreport(dictpath, htmlpath):
    """
    Generate HTML report on dictfile.
    :param dictpath:
    :param htmlpath:
    :return:
    """

    LD = LDict(dictpath)
    LD.LDictHtml(htmlpath)


if __name__ == "__main__":
    print(process('201701040951', 'dicts/translated.dic', 'corpora/testbestanden_sample'))