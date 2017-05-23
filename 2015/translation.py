import csv, json, html
from nltk import pos_tag
import pickle
from categories import get_category, add_elex_categories
import re
from time import sleep

prefix = """%
1\tfunction (Function Words)
\t2\tpronoun (Pronouns)
\t\t3\tppron (Personal Pronouns)
\t\t\t4\ti (I)
\t\t\t5\twe (We)
\t\t\t6\tyou (You)
\t\t\t7\tshehe (SheHe)
\t\t\t8\tthey (They)
\t\t9\tipron (Impersonal Pronouns)
\t10\tarticle (Articles)
\t11\tprep (Prepositions)
\t12\tauxverb (Auxiliary Verbs)
\t13\tadverb (Adverbs)
\t14\tconj (Conjunctions)
\t15\tnegate (Negations)
othergram (Other Grammar)
\t20\tverb (Verbs)
\t21\tadj (Adjectives)
\t22\tcompare (Comparisons)
\t23\tinterrog (Interrogatives)
\t24\tnumber (Numbers)
\t25\tquant (Quantifiers)
30\taffect (Affect)
\t31\tposemo (Positive Emotions)
\t32\tnegemo (Negative Emotions)
\t\t33\tanx (Anx)
\t\t34\tanger (Anger)
\t\t35\tsad (Sad)
40\tsocial (Social)
\t41\tfamily (Family)
\t42\tfriend (Friends)
\t43\tfemale (Female)
\t44\tmale (Male)
50\tcogproc (Cognitive Processes)
\t51\tinsight (Insight)
\t52\tcause (Causal)
\t53\tdiscrep (Discrepancies)
\t54\ttentat (Tentative)
\t55\tcertain (Certainty)
\t56\tdiffer (Differentiation)
60\tpercept (Perceptual Processes)
\t61\tsee (See)
\t62\thear (Hear)
\t63\tfeel (Feel)
70\tbio (Biological Processes)
\t71\tbody (Body)
\t72\thealth (Health)
\t73\tsexual (Sexual)
\t74\tingest (Ingest)
80\tdrives (Drives)
\t81\taffiliation (Affiliation)
\t82\tachieve (Achievement)
\t83\tpower (Power)
\t84\treward (Reward)
\t85\trisk (Risk)
timeorient (Time Orientation)
\t90\tfocuspast (Past Focus)
\t91\tfocuspresent (Present Focus)
\t92\tfocusfuture (Future Focus)
100\trelativ (Relativity)
\t101\tmotion (Motion)
\t102\tspace (Space)
\t103\ttime (Time)
persconc (Personal Concerns)
\t110\twork (Work)
\t111\tleisure (Leisure)
\t112\thome (Home)
\t113\tmoney (Money)
\t114\trelig (Religion)
\t115\tdeath (Death)
120\tinformal (Informal Language)
\t121\tswear (Swear)
\t122\tnetspeak (Netspeak)
\t123\tassent (Assent)
\t124\tnonflu (Nonfluencies)
\t125\tfiller (Filler Words)
%
"""

from collections import defaultdict
poscat = defaultdict(lambda: None, {
        '2': 'pron',
        '10': 'det',
        '20': 'v',
        '13': 'r',
        '11': 'prep',
        '14': 'conj',
        '21': 'a'
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

def remove_categories(categories, stoplist=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 14, 17, 18, 24]):
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

        translator.dump('corpora/gvertalingen_en_nl_2015.json')

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
    print(gtranslate('continuously', 'en', 'nl'))
