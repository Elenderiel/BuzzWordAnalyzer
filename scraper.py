import requests, math, pandas
from bs4 import BeautifulSoup as bs

import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from pyvis.network import Network

from wordfreq import zipf_frequency, top_n_list


url = 'https://vaarhaft.com/'

stripCharacters = """(.,:;?!&*|_-–"'„“”«»<>)"""
commonWords = top_n_list('en', 30) + ['']
columnCount = 50
savePlots = False
plotFileType = 'svg' #valid file types: svg, png, jpg, pdf, tiff


def main():
    response = getData(url)
    (wordSet, wordGraph) = buildWordGraphs(response)

    #comment out visualization functions you don't need
    plotWordCount(wordSet)
    plotWordFrequency(wordSet)

    visualizeGraph(wordSet, wordGraph)

def getData(url):
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


def buildWordGraphs(response) -> tuple:
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
            updateCountDict(wordSet, word)
            if i != len(words)-1:
                updateGraphDict(wordGraph, words, word, i)
        
    #exclude common words from wordSet.
    #networkx will remove all common words (nodes) in the wordGraph later
    for commonWord in commonWords:
        wordSet.pop(commonWord, None)
     
    #add frequency data for each word in wordSet
    for word in wordSet:
        wordSet[word]['frequency'] = getFrequency(word, wordSet[word]['count'], len(wordSet))
    
    return (wordSet, wordGraph)


def updateCountDict(wordSet, word):
    #initializing word-count pair or updating count
    try:
        if word not in wordSet:
            wordSet[word] = {'count': 1}
        else:
            wordSet[word]['count'] += 1
    except Exception as e:
        print(f'an exception occured while building the word-count dictionary: {e}')


def updateGraphDict(wordGraph, words, word, i):
    #looping over every unchecked word in the same section and updating the weight/distance of the edge
    for n, neighbourWord in enumerate(words[i+1:], start=i+1):
        distance = 1 / (n - i)
        key = tuple(sorted((word, neighbourWord)))
        wordGraph[key] = wordGraph.get(key, 0) + distance


def getFrequency(word:str, wordCount:int, totalCount:int) -> float:
    try:
        expectedFrequency = zipf_frequency(word, 'en')
        #zipf_frequency returns 0 for unknown words (often brand names etc.)
        if expectedFrequency == 0: expectedFrequency = 1
    except Exception as e:
        print(f"an exception occured while getting zipf_frequencies for {word}: {e}")
        return 0

    #computes the observed frequency (per billion words) and matches it to the log 10 scale of the zipf frequency
    observedFrequency = round(math.log10(wordCount/totalCount * 1e9), 2)
    return round(observedFrequency/expectedFrequency, 2)


def getPlotSize(length:int) -> tuple:
    #get dynamic plot size based on number of data entries
    colWidth = 0.5
    plotWidth = max(10, length * colWidth - 10)
    return (plotWidth, 6)


def getDataFrame(dict:dict, order:str):
    try:
        df = pandas.DataFrame.from_dict(dict, orient='index')
        df.reset_index(inplace=True)
        df.columns = ['words', 'count', 'frequency']
        df = df.sort_values(by=order, ascending=False)
        df = df.head(columnCount)
        return df
    except Exception as e:
        print(f"couldn't create dataframe for {order}: {e}")


def plotWordCount(wordSet:dict):
    #creates bar plot showing words and their word count, order descending
    df = getDataFrame(wordSet, 'count')

    fig, ax = plt.subplots(figsize=getPlotSize(len(df)))
    plot = sns.barplot(df, x='words', y='count', width=0.7, ax=ax)
    plot.set_xticks(plot.get_xticks())
    plot.set_xticklabels(plot.get_xticklabels(), rotation=-90)
    plt.tight_layout()
    if savePlots == True:
        plt.savefig(f'word-count.{plotFileType}')
    plt.show()
    plt.close()


def plotWordFrequency(wordSet:dict):
    #creates bar plot showing words and their showing their relative frequency values (observed / expected frequency), order descending
    df = getDataFrame(wordSet, 'frequency')

    fig, ax = plt.subplots(figsize=getPlotSize(len(df)))
    plot = sns.barplot(df, x='words', y='frequency', width=0.7, ax=ax)
    plot.set_xticks(plot.get_xticks())
    plot.set_xticklabels(plot.get_xticklabels(), rotation=-90)
    plt.tight_layout()
    if savePlots == True:
        plt.savefig(f'word-frequency.{plotFileType}')
    plt.show()
    plt.close()


def getNormalizedColor(cmap, minFreq:float, maxFreq:float, frequency:float) -> tuple:
    #converts the frequency values to a rgba color between blue and red
    normalizedFreq = (frequency - minFreq) / (maxFreq - minFreq)
    rgba = cmap(normalizedFreq)
    color  = f'rgba({int(rgba[0]*255)}, {int(rgba[1]*255)}, {int(rgba[2]*255)}, 0.7)'
    return color


def visualizeGraph(nodes:dict, edges:dict):
    try:
        #adds node data and edge weights to nx graph
        G = nx.Graph()
        G.add_nodes_from([(node, values) for node, values in nodes.items()])
        G.add_weighted_edges_from([(x, y, weight) for (x, y), weight in edges.items()])
        G.remove_nodes_from(commonWords)

        #precomputes the node positions for pyvis
        positions = nx.spring_layout(G, seed=1, iterations=100, threshold=0.7e-3, k=5/len(nodes)**0.5)
        nt = Network(height='100vh', width='100%', notebook=False, filter_menu=True, bgcolor='rgb(20, 20, 20)')

        minFreq = min((word['frequency'] for word in nodes.values()))
        maxFreq = max((word['frequency'] for word in nodes.values()))
        cmap = plt.colormaps['coolwarm']

        #adds node to pyvis at precomputed positions
        for node, (x, y) in positions.items():
            color = 'rgba(50, 50, 50, 0.7)'
            size = 5
            #dynamic size of node and lable based on word count. node color from colormap based on frequency value
            if node in nodes: 
                size = nodes[node]['count']**0.5
                color = getNormalizedColor(cmap, minFreq, maxFreq, (nodes[node]['frequency']))
            font = {'size': size*2, 'vadjust': -8, 'color': 'rgba(200, 200, 200, 0.7)'}
            nt.add_node(node, x=x * 1500, y=y * 1500, size=size*3, color=color, title=node, font=font)
         
        nt.toggle_drag_nodes(False)
        nt.toggle_physics(False)
        nt.show('word_graph.html', notebook=False)
    except Exception as e:
        print(f'an error occured while trying to create word graph: {e}')


main()