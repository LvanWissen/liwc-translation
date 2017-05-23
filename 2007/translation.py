import csv, json, html
from nltk import pos_tag
import pickle
from categories import get_category, add_elex_categories
import re
from time import sleep

prefix = """%
1\tfunct
2\tpronoun
3\tppron
4\ti
5\twe
6\tyou
7\tshehe
8\tthey
9\tipron
10\tarticle
11\tverb
12\tauxverb
13\tpast
14\tpresent
15\tfuture
16\tadverb
17\tpreps
18\tconj
19\tnegate
20\tquant
21\tnumber
22\tswear
121\tsocial
122\tfamily
123\tfriend
124\thumans
125\taffect
126\tposemo
127\tnegemo
128\tanx
129\tanger
130\tsad
131\tcogmech
132\tinsight
133\tcause
134\tdiscrep
135\ttentat
136\tcertain
137\tinhib
138\tincl
139\texcl
140\tpercept
141\tsee
142\thear
143\tfeel
146\tbio
147\tbody
148\thealth
149\tsexual
150\tingest
250\trelativ
251\tmotion
252\tspace
253\ttime
354\twork
355\tachieve
356\tleisure
357\thome
358\tmoney
359\trelig
360\tdeath
462\tassent
463\tnonfl
464\tfiller
%
"""

from collections import defaultdict
poscat = defaultdict(lambda: None, {
        '2': 'pron', 
        '10': 'det',
        '11': 'v',
        '16': 'r',
        '17': 'prep',
        '18': 'conj'
    })

possolve = defaultdict(lambda: None, {
        'NNP': 'n',
        'NN': 'n',
        'NNS': 'n',
        'NNPS': 'n',
        'JJ': 'a',
        'JJR': 'a',
        'JJS': 'a',
        'MD': 'aux',
        'DT': 'art',
        'VB': 'v',
        'VBD': 'v',
        'VBG': 'v',
        'VBN': 'v',
        'VBP': 'v',
        'VBZ': 'v',
        'RB': 'r',
        'RBR': 'r',
        'RBS': 'r',
        'PRP': 'ppron',
        'PRP$': 'pron',
        'WP': 'pron',
        'Wh$': 'pron',
        'IN': 'prep',
        'CC': 'conj',
    })

with open('corpora/elex/reference_nl.pickle', 'rb') as picklefile:
    reference_nl = pickle.load(picklefile)

# faster tagger using nltk. For better results probably use the Stanford one.
def tagger(word):
    return pos_tag([word])[0][1]

def remove_categories(categories, stoplist=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 17, 18, 21]):
    """
    Removes predifined categories from Word's categories.
    :param categories:
    :return:
    """
    new_categories = []

    for cat in categories:

        cat = int(cat)

        if cat in stoplist:
            continue
        else:
            new_categories.append(cat)

    return new_categories

class Translation():
    
    def __init__(self, dict_en):
        self.tokenlist = []

        self.translations = []
        
        self.dict_en = dict_en.rstrip('/')[0] #filepath hack

        dicreader = csv.reader(open(dict_en), delimiter="\t")
        totals = []

        wordlist = g_ngram(path='corpora/ngrams/1gms/vocab_cs', min_freq=750000)

        # skip the prefix
        line = next(dicreader)
        line = next(dicreader)

        while line != ['%']:
            line = next(dicreader)

        line = next(dicreader)

        while line != ['%']:
            totals.append(line)

            try:
                line = next(dicreader)
            except:
                break

            while "" in line:
                line.remove("")

        # add words as objects
        for word in totals:
            token, *categories_unfiltered = word

            categories = []
            for cat in categories_unfiltered:
                cat = re.findall('\d+', cat)  # to solve strange category descriptions in LIWC dict
                for c in cat:
                    categories.append(c)

            #wildcards
            if token.endswith("*"):
                wordforms = solve_wildcard(token[:-1], wordlist)
                
                for wf in wordforms:
                    self.tokenlist.append(self.Word(wf, categories, wildcard=token))
                    
            else:
                self.tokenlist.append(self.Word(token, categories))

        self.translate()

    def __enter__(self):
        return self
    
    # def categories(self):
    #     for word in self.tokenlist:
    #         if 'ppron' in word.pos and '3' not in word.categories:
    #             word.categories.append('3')
    #             word.categories.append('2')
    #         if 'pron' in word.pos and '2' not in word.categories:
    #             word.categories.append('2')
    #         if 'art' in word.pos and '10' not in word.categories:
    #             word.categories.append('10')
    #         if 'aux' in word.pos and '12' not in word.categories:
    #             word.categories.append('11')
    #             word.categories.append('12')
    #         if 'v' in word.pos and '11' not in word.categories:
    #             word.categories.append('11')
    #         if 'r' in word.pos and '16' not in word.categories:
    #             word.categories.append('16')
    #         if 'prep' in word.pos and '17' not in word.categories:
    #             word.categories.append('17')
    #         if 'conj' in word.pos and '18' not in word.categories:
    #             word.categories.append('18')

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            print(exc_type, exc_value, traceback)

    def translate(self, services=['google', 'treetagger', 'elex']):
        """
        Translate lemmas using two services:
            1. Google translate
            2. Treetagger to add lemmas and correct word categories
            3. Elex categories
        """
        if 'google' in services:
            for item in self.tokenlist:
                token = item.token
                categories = remove_categories(item.categories)
                translation = translator.translate(token)

                if translation in reference_nl:
                    self.translations.append((translation, categories))

        translator.dump('corpora/gvertalingen_en_nl.json')


        if 'treetagger' in services:
            print('Treetagging')
            translations = self.translations.copy()
            for n, (translation, categories) in enumerate(translations):

                wordcatlist = get_category(translation)

                if categories is None:
                    categories = []

                for word, cats in wordcatlist:
                    allcat = []

                    for cat in categories:
                        allcat.append(cat)
                    for cat in cats:
                        allcat.append(cat)

                    self.translations.append((word, set(allcat)))

                    print(n, (word, set(allcat)))

        if 'elex' in services:
            print("Using eLex")

            elexsetrules = 'rules/elexset.csv'
            wordcatlist = add_elex_categories(elexsetrules)

            for wordcat in wordcatlist:
                self.translations.append(wordcat)

            # Negative examples
            # Words that don't belong in other categories

            elexsetrules_negative = 'rules/elexset_negative.csv'
            wordcatlist_negative = add_elex_categories(elexsetrules_negative)

            to_be_removed = []
            to_be_added = []

            for wordcat in self.translations:
                for w, cl in wordcatlist_negative:

                    if wordcat[0] == w:

                        print('Remove:', wordcat)
                        to_be_removed.append(wordcat)
                        to_be_added.append((w,cl))

            self.translations = [wordcat for wordcat in self.translations if wordcat not in to_be_removed]

            for wordcat in to_be_added:
                self.translations.append(wordcat)


    def to_dict(self, filename_nl):
        """
        Write the dictionary to a file with filename_nl.

        Alphabetical order, categories combined for each word.
        """
        self.filename_nl = filename_nl
        self.d = defaultdict(set)

        for word, categories in self.translations:
            if categories:
                self.d[word.lower()].update(categories)

        with open(self.filename_nl, 'w', encoding='utf-8') as dicfile:
            dicfile.write(prefix)

            for w, cat in sorted(self.d.items()):
                if '_' in w:
                    continue
                elif '[' in w or ']' in w:
                    continue
                elif '(' in w or ')' in w:
                    continue
                else:
                    dicfile.write(w + '\t')
                    dicfile.write('\t'.join(str(i) for i in sorted(list(cat))))
                    dicfile.write('\n')

    class Word():

        def __init__(self, token, categories, wildcard=""):
            self.token = token
            self.categories = categories
            self.wildcard = wildcard

            self.pos = [poscat[i] for i in self.categories if poscat[i] is not None]
            #print(self.token, self.categories, self.pos)

            if self.pos == []:
                pos = tagger(self.token)
                self.pos.append(possolve[pos])

            self.translations = []

def g_ngram(min_freq, path='corpora/ngrams/1gms/vocab_cs'):
    """
    Read google_ngrams corpus (unigram) and return wordlist based on minimum frequency.
    :param path:
    :return: wordlist
    """

    wordlist = []

    with open('corpora/ngrams/1gms/vocab_cs', encoding='utf-8') as wordsfile:

        while True:
            i = wordsfile.readline()
            try:
                word, freq = i.strip().split('\t')
                freq = int(freq)

                if freq >= min_freq:
                    wordlist.append(word.lower())
                else:
                    break
            except:
                continue

    return list(set(wordlist))

def solve_wildcard(token, wordlist):
    """
    Solve wildcard entries (such as approx*) into the full form to allow automatic translation.  
    :param token: token (string) that serves as prefix (without asterisk)
    :param wordlist: corpus (list)
    :return: A list of all the words from the corpus that start with the token. 
    """

    matchlist = []

    print(token)

    for word in wordlist:
        if word.startswith(token):
            matchlist.append(word)
    print('wildcard resolution:', matchlist)

    return list(set(matchlist))

class GoogleTranslator():
    """
    Initiate Translator object to translate from en2nl.
    """
    def __init__(self, jsonfilepath):

        self.filepath = jsonfilepath

        try:
            with open(jsonfilepath, encoding='utf-8') as jsonfile:
                self.d = json.load(jsonfile)
        except FileNotFoundError:
            self.d = dict()

    def translate(self, word):
        if word in self.d:
            return self.d[word]
        else:
            try:
                translation = gtranslate(word, 'en', 'nl')
            except:
                self.dump(self.filepath)
            print(word, '-', translation)

            translation = html.unescape(translation).lower() # Filter HTML apostrophe

            self.d[word] = translation

            return translation

    def dump(self, jsonfilepath):
        """
        Store translations for faster future translations.
        :param jsonfilepath:
        :return:
        """
        with open(jsonfilepath, 'w', encoding='utf-8') as jsonfile:
            json.dump(self.d, jsonfile)

def gtranslate(word, sl, tl):
    import requests

    r = requests.get("https://translate.googleapis.com/translate_a/single?client=gtx&sl=" + sl + "&tl=" + tl + "&dt=t&q=" + word)
    translation = json.loads(r.text)[0][0][0]
    # print('Translation of:', word, '=', translation)
    sleep(2)

    return translation

translator = GoogleTranslator('corpora/gvertalingen_en_nl.json')

if __name__ == '__main__':
    pass