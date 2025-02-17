import requests
from bs4 import BeautifulSoup as bs
import pandas
import matplotlib.pyplot as plt
import seaborn as sns

url = 'https://www.vaarhaft.com/'

try:
    request = requests.get(url)
    if request.status_code == 200:
        response = request.text
    else:
        print(f'Request failed with status: {request.status_code}')
except Exception as e:
    print(f'an exception occured while requesting html data from {url}: {e}')
    exit()

soup = bs(response, 'html.parser')
text = soup.get_text(separator=' ', strip=True)
wordList = [w.strip('.:,|?!').lower() for w in text.split(' ')]
totalCount = len(wordList)
wordSet = {}
for word in wordList:
    wordSet[word] = wordSet.get(word, 0) + 1
for commonWord in ['and', 'the', 'in', 'for', 'of', 'a', 'an', 'to', 'or', 'is', 'are', 'am', 'on', 'as']:
    wordSet.pop(commonWord, None)
wordSet = dict(sorted(wordSet.items(), key=lambda kv: kv[1], reverse=True)[:100])

df = pandas.DataFrame(wordSet.items(), columns=['words', 'count'])
minWidth = 1
plotWidth = max(10, len(df) * minWidth - 4)
fig, ax = plt.subplots(figsize=(plotWidth, 6))
plot = sns.barplot(df, x='words', y='count', width=0.7, ax=ax)
plot.set_xticklabels(plot.get_xticklabels(), rotation=-90)
plt.tight_layout()
plt.show()