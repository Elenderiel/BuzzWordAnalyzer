from wordfreq import top_n_list

from services import graph, plots, scraper


url = 'https://vaarhaft.com/'

savePlots = False
showPlots = True
fileType = 'svg' #valid file types: svg, png, jpg, pdf, tiff

stripCharacters = """(.,:;?!&*|_-–"'„“”«»<>)"""
commonWords = top_n_list('en', 30)
columnCount = 50


def main():
    response = scraper.get_data(url)
    (wordSet, wordGraph) = scraper.build_word_graphs(response, commonWords, stripCharacters)

    #comment out visualization functions you don't need
    plots.plot_word_count(wordSet, savePlots, showPlots, fileType, columnCount)
    plots.plot_word_frequency(wordSet, savePlots, showPlots, fileType, columnCount)

    graph.visualize_graph(wordSet, wordGraph, commonWords)


main()