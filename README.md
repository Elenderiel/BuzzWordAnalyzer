# BuzzWordAnalyzer

A fun little script, that analyzes and visualizes the word usage of a website

## Settings

![image placeholder](./resources/settings.png)

|          |             |
| -------- | ----------- |
| url      | url of website you want to analyze |
| savePlots | Boolean, True if you want to save the created plots as files |
| showPlots | Boolean, True if you want to show the plots in an extra matplotlib window |
| fileType | if savePlots is set to True, this controls the file type of the saved plots |
| stripCharacters | a set of characters that get removed from the beginning and end of each found word |
| commonWords | list of common english words, that are excluded from the analyzis of the found words |
| columnCount | Integer, number collumns that are shown on the plots (for example top 50 words with highest count) |

## Plots

### Word Count Plot

![image placeholder](./resources/countplot.png)

the word count plot shows the top most counted words on the website

![image placeholder](./resources/wordfrequency.png)

the word frequency plot shows the top words with the hightest relative frequency score on the website

## Word Graph

![image placeholder](./resources/graph.png)

The size of the nodes represent the count value of the word. The bigger the node, the more it was used on the side.

The color of a node represents its relative frequency value (observed frequency / expected frequency). Red means, that a normaly uncommon word was used unusually often. Blue means the exact opposite