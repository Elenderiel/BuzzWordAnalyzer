import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def get_plot_size(length:int) -> tuple:
    #get dynamic plot size based on number of data entries
    colWidth = 0.5
    plotWidth = max(10, length * colWidth - 10)
    return (plotWidth, 6)


def get_data_frame(dict:dict, order:str, columnCount:int):
    try:
        df = pd.DataFrame.from_dict(dict, orient='index')
        df.reset_index(inplace=True)
        df.columns = ['words', 'count', 'frequency']
        df = df.sort_values(by=order, ascending=False)
        df = df.head(columnCount)
        return df
    except Exception as e:
        print(f"couldn't create dataframe for {order}: {e}")


def handle_plot_files(plot, name:str, savePlots:bool, showPlots:bool, fileType:str):
    plot.set_xticks(plot.get_xticks())
    plot.set_xticklabels(plot.get_xticklabels(), rotation=-90)
    plt.tight_layout()
    if savePlots:
        plt.savefig(f'{name}.{fileType}')
    if showPlots: 
        plt.show()
    plt.close()


def plot_word_count(wordSet:dict, savePlots:bool, showPlots:bool, fileType:str, columnCount:int):
    #creates bar plot showing words and their word count, order descending
    df = get_data_frame(wordSet, 'count', columnCount)

    fig, ax = plt.subplots(figsize=get_plot_size(len(df)))
    plot = sns.barplot(df, x='words', y='count', width=0.7, ax=ax)
    handle_plot_files(plot, 'word-counts', savePlots, showPlots, fileType)


def plot_word_frequency(wordSet:dict, savePlots:bool, showPlots:bool, fileType:str, columnCount:int):
    #creates bar plot showing words and their relative frequency values (observed / expected frequency), order descending
    df = get_data_frame(wordSet, 'frequency', columnCount)

    fig, ax = plt.subplots(figsize=get_plot_size(len(df)))
    plot = sns.barplot(df, x='words', y='frequency', width=0.7, ax=ax)
    handle_plot_files(plot, 'word-frequencies', savePlots, showPlots, fileType)