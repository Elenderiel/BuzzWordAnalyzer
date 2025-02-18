import requests, math, pandas
from bs4 import BeautifulSoup as bs
import matplotlib.pyplot as plt
import seaborn as sns
from wordfreq import zipf_frequency, top_n_list


commonWords = top_n_list('en', 30)
#'you' and 'we' could be interesting to include
commonWords.pop(10)                                 
commonWords.pop(28)

url = 'https://www.vaarhaft.com/'


def getData(url):
    try:
        request = requests.get(url, timeout=15)
        if request.status_code == 200:
            response = request.text
            getWordData(response)
        else:
            print(f'Request failed with status: {request.status_code}')
    except Exception as e:
        print(f'an exception occured while requesting data from {url}: {e}')
        exit()

def getWordData(response):
    try:
        soup = bs(response, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        wordList = [w.strip('.:,|?!').lower() for w in text.split(' ')]

        #iterate over words, create dict of unique words and their word count
        wordSet = {}
        for word in wordList:
            if word not in wordSet:
                wordSet[word] = {'count' : 1, 'frequencyDiff' : 0}
            else:
                wordSet[word]['count'] += 1
        
        #exclude common words
        for commonWord in commonWords:
            wordSet.pop(commonWord, None)
        for word in wordSet:
            wordSet[word]['frequencyDiff'] = getFrequency(word, wordSet[word]['count'], len(wordList))
        
        plotWordCount(wordSet)
        plotWordFrequency(wordSet)
    except Exception as e:
        print(f'could not extract text: {e}')

def getFrequency(word:str, wordCount:int, totalCount:int):
    try:
        expectedFrequency = zipf_frequency(word, 'en')
        if expectedFrequency == 0: expectedFrequency = 1

        #computes the observed frequency (per billion words) and matches it to the log 10 scale of the zipf frequency
        observedFrequency = round(math.log10(wordCount/totalCount * 1e9), 2)
        return round(observedFrequency/expectedFrequency, 2)
    except Exception as e:
        print(f"couldn't compute frequencies for {word}: {e}")
        return (1)

def getPlotSize(length):
    minWidth = 0.5
    plotWidth = max(10, length * minWidth - 10)
    return (plotWidth, 6)

def getDataFrame(dict, order):
    try:
        df = pandas.DataFrame.from_dict(dict, orient='index')
        df.reset_index(inplace=True)
        df.columns = ['words', 'count', 'frequency']
        df = df.sort_values(by=order, ascending=False)
        df = df.head(50)
        return df
    except Exception as e:
        print(f"couldn't create dataframe, sorted by {order}: {e}")

def plotWordCount(wordSet):
    df = getDataFrame(wordSet, 'count')

    fig, ax = plt.subplots(figsize=getPlotSize(len(df)))
    plot = sns.barplot(df, x='words', y='count', width=0.7, ax=ax)
    plot.set_xticks(plot.get_xticks())
    plot.set_xticklabels(plot.get_xticklabels(), rotation=-90)
    plt.tight_layout()
    plt.show()

def plotWordFrequency(wordSet):
    df = getDataFrame(wordSet, 'frequency')

    fig, ax = plt.subplots(figsize=getPlotSize(len(df)))
    plot = sns.barplot(df, x='words', y='frequency', width=0.7, ax=ax)
    plot.set_xticks(plot.get_xticks())
    plot.set_xticklabels(plot.get_xticklabels(), rotation=-90)
    plt.tight_layout()
    plt.show()

getData(url)