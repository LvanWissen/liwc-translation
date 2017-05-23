import treetaggerwrapper
import csv
import json
import os
from collections import defaultdict
from LIWCtools.LIWCtools import LDict

tagger = treetaggerwrapper.TreeTagger(TAGLANG='nl')

catdict = {}
categories = csv.DictReader(open('corpora/tagset.csv'),
                            fieldnames=["tag", "description", "cat", "liwc_description"],
                            delimiter='\t')
for line in categories:
    catdict[line['tag']] = tuple(int(i) for i in line['cat'].split(',') if line['cat'] != "")

lemdict = defaultdict(list)
lemmas = csv.DictReader(open('corpora/dutch_lemmas.txt', encoding='utf-8'),
                            fieldnames=["lemma", "token"],
                            delimiter=';')
for line in lemmas:
    lemdict[line['lemma']].append(line['token'])

def tag(word):
    """
    Tag a word with POS information and retrieve lemma using TreeTagger. For now no MWE.
    :param word:
    :return: list of tuples: [(word, POS, lemma)]
    """

    tags = tagger.tag_text(word)
    tagstuple = treetaggerwrapper.make_tags(tags)
    tagslist = []

    for tp in tagstuple:
        try:
            word, pos, lemma = tp[0], tp[1], tp[2]
            tagslist.append((word, pos, lemma))
        except:
            print('Could not tag:', word, tp)

    return tagslist[0]

def get_category(token):
    """

    :param word:
    :return:
    """

    results = []

    #  First the word
    word, pos, lemma = tag(token)
    cat = catdict[pos]
    results.append((token, cat))

    #  Then the lemma
    if '|' not in lemma: # in case of ambiguous lemma by TreeTagger
        word, pos, lemma = tag(lemma)
        cat_lemma = catdict[pos]
        results.append((lemma, cat_lemma))

        #  And then for every word from the Dutch lemmalist
        for word in lemdict[lemma]:
            word, pos, lemma = tag(word)
            cat = catdict[pos]
            results.append((word, cat))

    return set(results)

def add_elex_categories(elexsetrules):

    with open('corpora/elex/e-lex.json', encoding='utf-8') as jsonfile:
        elex = json.load(jsonfile)

    with open(elexsetrules, encoding='utf-8') as rulesfile:

        rules = csv.DictReader(rulesfile, fieldnames=['dictcat', 'pos', 'cat'])

        elexcatdict = defaultdict(list)
        for r in rules:
            if r['cat']:
                dictcat, pos, cat = r['dictcat'], r['pos'], r['cat'].split(',')
            else:
                dictcat, pos = r['dictcat'], r['pos']
                cat = []

            dictcat = int(dictcat)

            words = find_elex_words(cat, [pos], elex)
            print(dictcat, words)

            elexcatdict[dictcat] += (words)

    # elexcatdict = {
    #     2: ['enigste', 'haarzelf', "z'n", "'k", 'dewelke', 'hetgene', 'eenieder', 'haar', 'degenen', 'onze', 'die', 'allebei', 'zichzelf', 'hulliejen', 'elkander', 'menigeen', 'hetwelke', 'alle', 'zelf', 'ditte', 'oe', 'me', 'elkaars', 'zulkdanig', 'andersgekleurde', "d'rin", 'meerderen', 'gij', 'zijn', 'jou', 'ul', 'meeste', 'veler', 'hij', 'sommige', 'enkele', 'wij', 'hiero', "m'n", 'sommig', 'meerdere', 'je', 'waar', 'al', 'mezelve', 'mekander', 'vaak', 'zovele', 'wien', 'mijne', 'jouwe', 'u', 'niet', 'degene', 'beide', 'halfelf', 'iemands', 'teveel', 'zijns', 'daar', 'ginds', 'elkanders', 'niets', 'geen', "d'raf", 'keiveel', 'jij', 'jouw', 'jezelf', 'superveel', 'alleman', 'hunzelf', 'eenieders', 'welk', 'wijzelf', 'onzes', 'ons', 'onszelf', "'t", 'uw', 'keiweinig', 'nop', 'iet', 'beidjes', 'hetwelk', 'minst', 'telken', 'eigen', 'daaro', 'dauw', 'mekaars', 'deze', "d'rbij", 'ernaast', 'datgene', 'niemands', 'iedereens', 'aller', 'wat', 'huns', 'andermans', 'kunnen', 'jouzelf', 'zoveel', 'erbij', 'waterdragen', 'henzelf', 'diegene', 'zoiet', 'zich', 'gaat', 'gaan', 'er', 'allerminst', 'we', 'alletwee', 'zulke', 'mijns', 'dies', 'der', 'weinigen', 'ie', 'mekaar', "'m", 'elkeen', 'menig', 'harer', 'noppes', 'ditgene', 'nergens', 'elkes', 'mekanders', 'ettelijke', 'allerhande', 'ieders', 'wie', 'niemand', 'jouwer', 'iets', 'vaker', 'mij', 'ikzelf', 'elkaar', 'meer', 'dezes', 'ieder', 'zulkdanige', 'mijzelf', 'das', 'allen', 'minder', "d'rnaast", 'dat', 'erin', 'hetgeen', 'zichzelve', 'zijzelf', 'enigen', 'dit', 'niemendal', 'gene', 'hen', 'genen', 'sommigte', 'zijne', 'eraf', 'watte', 'gijzelf', 'meest', 'uzelf', 'eht', 't', 'ertussenin', 'elke', 'diens', 'hem', 'hetzelve', 'dezer', 'jijzelf', 'iedereen', 'da', 'diezelfde', 'ergens', 'hare', 'andervrouws', 'datte', 'veel', 'hullie', 'alles', 'enig', 'zij', 'ik', 'ge', 'hemzelf', 'mijn', 'dezelfde', 'diegenen', 'allemans', 'menige', 'vier', 'overal', 'hijzelf', 'gindse', 'men', 'ze', "'tgeen", 'hun', 'sommigen', 'zulks', 'uws', 'enige', 'welke', 'wier', 'minste', 'meerder', 'hier', 'iemand', 'mindere', 'welks', 'evenveel', 'het', 'zulk', 'dag', 'weinig'],
    #     3: ['t', 'er', 'haarzelf', "'k", 'we', 'zijns', 'hetzelve', 'mijns', 'haar', 'ie', "'m", 'harer', 'jij', 'hunzelf', 'wijzelf', 'zij', 'ik', 'ge', 'hemzelf', 'oe', 'mijn', "'t", 'uw', 'ikzelf', 'gij', 'zijn', 'hijzelf', 'men', 'eigen', 'ze', 'hij', 'hun', 'uws', 'wij', 'zijzelf', 'huns', 'hen', 'je', 'kunnen', 'waterdragen', 'het', 'gijzelf', 'eht'],
    #     4: ['mij', 'ikzelf', "'k", 'mezelve', 'mijns', 'eigen', 'mijzelf', 'ik', 'me', 'mijn'],
    #     5: ['wij', 'we', 'onzes', 'henzelf', 'onze', 'ons', 'onszelf'],
    #     6: ['jij', 'jouzelf', 'oe', 'ge', 'jezelf', 'u', 'gij', 'jijzelf', 'gijzelf', 'uws', 'uzelf', 'uw'],
    #     7: ['zichzelf', "'t", 't', 'haarzelf', 'zichzelve', "'m", 'zelf', 'hem', 'kunnen', 'hijzelf', 'ie', 'ul', 'eht', 'zij', 'hetzelve', "'tgeen", 'ze', 'hemzelf', 'hij', 'zich', 'het'],
    #     8: ['hunzelf', 'huns', 'hen', 'zij', 'hun', 'ze'],
    #     9: ['enigste', 'eenieder', 'allebei', 'menigeen', 'alle', 'één', 'elkens', 'andersgekleurde', 'iederen', 'meerderen', 'velen', 'entwa', 'meeste', 'veler', 'sommige', 'enkele', 'sommig', 'meerdere', 'al', 'enen', 'vaak', 'zovele', 'enkelen', 'niet', 'zoiets', 'beide', 'halfelf', 'iemands', 'teveel', 'niets', 'geen', 'veels', 'enkel', 'keiveel', 'superveel', 'alleman', 'iemens', 'eenieders', 'nop', 'entwat', 'keiweinig', 'etwien', 'iet', 'beidjes', 'minst', 'telken', 'ten', 'niemands', 'iedereens', 'aller', 'elk', 'andermans', 'zoveel', 'zoiet', 'allerminst', 'weinigen', 'sommigeder', 'elkeen', 'menig', 'noppes', 'nergens', 'elkes', 'ettelijke', 'allerhande', 'ietske', 'ieders', 'niemand', 'iets', 'zoietske', 'vaker', 'meer', 'ieder', 'allen', 'minder', 'entwadden', 'enigen', 'niemendal', 'elken', 'genen', 'sommigte', 'ietekes', 'meest', 'iemes', 'elke', 'twat', 'entwadde', 'iedereen', 'nikske', 'ergens', 'andervrouws', 'veel', 'iederes', 'alles', 'enig', 'niks', 'allemans', 'menige', 'vier', 'overal', 'niemes', 'sommigen', 'enige', 'zoietsken', 'vele', 'minste', 'ene', 'meerder', 'iemand', 'mindere', 'evenveel', 'alletwee', 'weinig'],
    #     10: ['een', 'één', 'hetzelfde', "'n", 'ee', 'der', 'het', 'de', "'tzelfde", "'r", "'t"],
    #     15: ['zal', 'zult', 'zullen', 'zou', 'zouden'],
    #     17: ['neer', 'cq', "d'rover", 'volgens', 'luidens', 'voor', 'rondom', 'af', 'omstreeks', 'zijdens', 'ongeacht', 'per', 'naartoe', 'doorheen', 'daarbij', 'versus', 'inclusief', 'sedert', 'erop', 'daaraan', 'aan', 'inzake', 'behalve', 'spijts', 'behoudens', 'rechtover', 'errond', 'plus', 'erover', 'onder', 'ervoor', 'al', 'om', 'bij', 'onafgezien', 'buiten', 'namens', 'trots', 'getuige', 'over', 'open', 'rond', 'langs', 'terug', 'tegenaan', 'boven', 'teneinde', 'naast', 'bewesten', 'dankzij', 'linksom', 'met', 'ter', 'hierdoorheen', 'waardoor', 'beneden', 'langst', 'uitgenomen', 'toe', 'kralj', 'binnenuit', 'ten', 'dichtbij', 'qua', 'tijdens', 'daarin', 'betreffende', 'gegeven', 'weg', 'ingevolge', 'naar', 'binst', "t'", 'middenop', 'achter', 'tot', 'voren', 'van', 'bladzij', 'gezien', 'benoorden', 'een', 'halverwege', 'mee', 'ondanks', 'zo', 'daarnaar', 'in', 'zonder', 'anti', 'door', 'ga', 'via', 'vanuit', 'à', 'vanop', 'zoals', 'binnen', 'deure', 'daarbuiten', 'blijkens', 'bezijden', 'neffe', 'conform', 'waaronder', 'langsheen', 'voorbij', 'meer', 'mede', 'aal', 'annex', 'als', 'anno', 'lopende', 'op', 'beoosten', 'aangaande', 'te', 'krachtens', 'ultimo', 'sinds', 'eraf', 'hierop', 'vanaf', 'bovenop', 'jegens', 'uit', 'hene', 'benevens', 'gedurende', 'tegen', 'niettegenstaande', 'omtrent', 'heen', 'neffen', 'na', 'daartegenover', 'middels', 'daaronder', 'tegenover', 'wegens', 'vandaan', 'nevenst', 'contra', 'tegenop', 'eruit', 'on', 'tussen', 'vanwege', 'mits', 'voort', 'afgezien', 'bezuiden', 'omheen', 'nopens', 'pro', 'lastens'],
    #     18: ['ofdat', 'cq', 'ingeval', 'voor', 'vanals', 'maar', 'omdat', 'opdat', 'aangezien', 'behalve', 'ma', 'ofschoon', 'oftewel', 'zohaast', 'plus', 'alsmede', 'zodra', 'al', 'waar', 'om', 'lik', 'nu', 'bij', 'wijl', 'tenzij', 'daar', 'schoon', 'want', 'teneinde', 'en', 'wanneer', 'alsook', 'voordat', 'ja', 'dan', 'uitgenomen', 'noch', 'vooraleer', 'alst', 'zover', 'hoe', 'eerdat', 'wat', 'hetzij', 'binst', 'evenals', 'umdat', 'zo', 'terwijl', 'indien', 'tenware', 'doordat', 'zoals', 'ofwel', 'doch', 'ende', 'eer', 'ofte', 'dus', 'naargelang', 'annex', 'als', 'dat', 'alsof', 'a', 'ot', 'enne', 'bijaldien', 'lijk', 'vermits', 'of', 'wi', 'toen', 'gelijk', 'aleer', 'niettegenstaande', 'naarmate', 'nadat', 'alvorens', 'datte', 'voorzover', 'hoezeer', 'mits', 'as', 'zodat', 'alhoewel', 'hoewel', 'zolang', 'slash', 'totdat']
    #     }

    wordcatlist = []

    for cat, words in elexcatdict.items():
        for word in words:
            wordcatlist.append((word, [cat]))

    return wordcatlist


def find_elex_words(categories, pos, d):
    """
    Return a list of words from a elexdictionary
    :param categories:
    :param pos:
    :param d:
    :return:
    """

    total = []
    for lemma in d:
        for wf in d[lemma]:
            token = wf['token'].lower()

            if token.isnumeric():
                continue

            if set(categories).issubset(set(wf['categories'])) or categories == ['']:
                if pos:
                    for p in pos:
                        if p in wf['pos'] and 'dial' not in wf['categories']:
                            total.append(token)
                            total.append(lemma)
                else:
                    if 'dial' not in wf['categories']:
                        total.append(token)
                        total.append(lemma)

    return list(set(total))


def solve_hierarchies(dictpath, dict_EN):
    """
    Fix hierarchies in dictionary. Use English dict as model.
    :param dictpath:
    :param dict_EN:
    :return:
    """

    LD = LDict(dictpath)
    model = LDict(dict_EN)

    LD.LDictRestoreWS()
    LD.LDictComplete(model)

    os.rename(dictpath, dictpath + '.old')
    LD.LDictWrite(dictpath)






if __name__ == '__main__':

    # with open('corpora/e-lex.json', encoding='utf-8') as jsonfile:
    #     elex = json.load(jsonfile)
    #
    # # print(find_elex_words(['aanw'], ['VNW'], elex))
    #
    # add_elex_categories('corpora/elexset.csv')

    pass
