import requests
import math

from bs4 import BeautifulSoup as bs
from wordfreq import zipf_frequency


def get_data(url):
    #requests data from url and extracts the html/text object
    try:
        request = requests.get(url, timeout=15)
        if request.status_code == 200:
            response = request.text
            return response
        else:
            print(f'Request failed with status: {request.status_code}')
    except Exception as e:
        print(f'an exception occured while requesting data from {url}: {e}')
        exit()


def build_word_graphs(response, commonWords:list, stripCharacters:str) -> tuple:
    #extracts all text from the websites html content. The text from each html element is seperated into sections
    try:
        soup = bs(response, 'html.parser')
        text = soup.get_text(separator='\n', strip=True)
        sectionList = [w for w in text.split('\n')]
    except Exception as e:
        print(f'could not extract text: {e}')
    
    #iterates through each section building a dictionary containing the set of words and their count
    #also builds edge list/dict containing the average distance (in words) between two words, later used as edge weights in the force graph
    wordSet = {}
    wordGraph = {}
    for section in sectionList:
        words = [word.strip(stripCharacters).lower() for word in section.split(' ')]
        
        for i, word in enumerate(words):
            update_count_dict(wordSet, word)
            if i != len(words)-1:
                update_graph_dict(wordGraph, words, word, i)
        
    #exclude common words from wordSet.
    #networkx will remove all common words (nodes) in the wordGraph later
    for commonWord in commonWords + ['']:
        wordSet.pop(commonWord, None)
     
    #add frequency data for each word in wordSet
    for word in wordSet:
        wordSet[word]['frequency'] = get_frequency(word, wordSet[word]['count'], len(wordSet))
    
    return (wordSet, wordGraph)


def update_count_dict(wordSet, word):
    #initializing word-count pair or updating count
    try:
        if word not in wordSet:
            wordSet[word] = {'count': 1}
        else:
            wordSet[word]['count'] += 1
    except Exception as e:
        print(f'an exception occured while building the word-count dictionary: {e}')


def update_graph_dict(wordGraph, words, word, i):
    #looping over every unchecked word in the same section and updating the weight/distance of the edge
    for n, neighbourWord in enumerate(words[i+1:], start=i+1):
        distance = 1 / (n - i)
        key = tuple(sorted((word, neighbourWord)))
        wordGraph[key] = wordGraph.get(key, 0) + distance


def get_frequency(word:str, wordCount:int, totalCount:int) -> float:
    try:
        expectedFrequency = zipf_frequency(word, 'en')
        #zipf_frequency returns 0 for unknown words (often brand names etc.)
        if expectedFrequency == 0: 
            expectedFrequency = 2
    except Exception as e:
        print(f"an exception occured while getting zipf_frequencies for {word}: {e}")
        return 0

    #computes the observed frequency (per billion words) and matches it to the log 10 scale of the zipf frequency
    observedFrequency = round(math.log10(wordCount/totalCount * 1e9), 2)
    return round(observedFrequency/expectedFrequency, 2)