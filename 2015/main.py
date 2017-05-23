"""LIWC Translation

    Usage:
        main.py [options]

    Options:
        -h --help           Show this screen.
        -d --dict FILE    Supply own dictionary.
        -c --corpus FOLDER  Specify test corpus [default: corpora/dpc].
    """
import csv
import os
import sys
from docopt import docopt
from datetime import datetime

sys.path.append('./')
from evaluation import evaluate
from process import process, gethtmlreport
import shutil

if __name__ == "__main__":
    args = docopt(__doc__, version=None)

    if args['--dict']:
        skip_translation = True
        owndict = args['--dict']
    else:
        skip_translation = False

    corpus = args['--corpus']
    print("Using corpus", corpus)
    CORPUS = os.path.join(corpus, 'nl')
    CORPUS_EN = os.path.join(corpus, 'en')

    DICTDIR = 'dicts/'
    ENGLISH_DICT = '2015-08-24-LIWC2015 Dictionary - Internal.dic'  # to be translated

    message = input("Describe this run for the runs.csv file: ")

    RUNSDIR = 'runs/'
    if not os.path.exists(RUNSDIR):
        os.makedirs(RUNSDIR)


    # new attempt
    run = "{:%Y%m%d%H%M}".format(datetime.now())
    os.makedirs(RUNSDIR + run, exist_ok=True)

    os.makedirs(os.path.join(RUNSDIR + run, 'scripts'))
    files = [f for f in os.listdir('.') if os.path.isfile(f) and f.endswith(".py")]
    for f in files:
        shutil.copy(f, os.path.join(RUNSDIR + run, 'scripts'))

    os.makedirs(os.path.join(RUNSDIR + run, 'rules'))
    files = [os.path.join('rules', f) for f in os.listdir('rules')]
    for f in files:
        shutil.copy(f, os.path.join(RUNSDIR + run, 'rules'))


    os.makedirs(os.path.join(RUNSDIR + run, 'corpora'))
    files = []
    files.append('corpora/gvertalingen_en_nl_2015.json')
    for f in files:
        shutil.copy(f, os.path.join(RUNSDIR + run, 'corpora'))

    print("Created new folder: {}".format(run))

    if not skip_translation:
        from translation import Translation
        from categories import solve_hierarchies
        # 1a Translation
        print("Translating...")
        translated_dict = Translation(DICTDIR + ENGLISH_DICT)
        translated_dict.to_dict(RUNSDIR + run + '/' + run + '.dic')
        dictpath = os.path.join('runs', run, run + '.dic')

        # Expand word categories by looking at the hierarchy of the English dict

        solve_hierarchies(dictpath, DICTDIR + ENGLISH_DICT)

    else:
        dictpath = shutil.copy(owndict, RUNSDIR + run)  # copy own dict to rundir


    print("Creating HTML report file")

    gethtmlreport(dictpath, os.path.join(RUNSDIR + run, 'report.html'))

    # 2 Processing on test files

    print("Counting CORPUS files for EN dict...")
    results_en = process(run, DICTDIR + ENGLISH_DICT, CORPUS_EN)

    print("Counting corpus files for translation attempt...")
    results_trans = process(run, dictpath, CORPUS)

    # 3 Evaluation
    print("Evaluation...")

    avg_corr, avg_eff = evaluate(results_en, results_trans, run)

    avg_corr = str(avg_corr).replace('.', ',')
    avg_eff = str(avg_eff).replace('.', ',')

    print("Score: {} ({})".format(avg_corr, avg_eff))

    dictname = os.path.basename(dictpath)

    results = {
        "run": run,
        "avg_corr": avg_corr,
        "avg_eff": avg_eff,
        "dict": dictname,
        "corpus": CORPUS,
        "message": message
        }

    file_exists = os.path.isfile(RUNSDIR + 'runs.csv')
    with open(RUNSDIR + 'runs.csv', 'a', encoding='utf-8') as resultsfile:

        resultswriter = csv.DictWriter(resultsfile, fieldnames=["run", "avg_corr", "avg_eff", "dict", "corpus", "message"], lineterminator='\n', delimiter=';')
        
        if not file_exists:
            resultswriter.writeheader()
        resultswriter.writerow(results)

