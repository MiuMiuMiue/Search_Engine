from collections import defaultdict
from TF_IDF import TfIdfCalculation
import numpy as np
import nltk
nltk.download("stopwords")
from nltk.corpus import stopwords

np.set_printoptions(threshold=np.inf)

def computeTfIdf(query, idfDict, stopWords):
    """This function calculates the tf-idf values of the query"""
    calculator = TfIdfCalculation()
    wordCounter = defaultdict(int)

    for word in query:
        if word.lower() not in stopWords:
            wordCounter[word.lower()] += 1

    tfDict = calculator.calculateTF(wordCounter)
    try:
        results = {key: tfDict[key] * idfDict[key] for key in tfDict.keys()}
    except KeyError:
        results = {}
    return results

def findTopKUrl(query, urlDict, idfDict, indexCursor):
    """This function finds the top K urls by using the vector space model by using numpy."""
    stopWords = set(stopwords.words("english"))
    queryValues = computeTfIdf(query, idfDict, stopWords)

    queryWords = list(queryValues.keys())
    wordIndex = []
    docs = []
    meta = []
    docCount = defaultdict(int)

    for word in queryWords:
        indexCursor.execute(f"""
            SELECT *
            FROM indexTable
            WHERE word = '{word}'
        """)
        tempList = []
        result = indexCursor.fetchall()
        if len(result) >= 1:
            result = result[0]
            tempList.append(result[0])
            tempList.append(result[1].split(","))
            tempList.append([float(value) for value in result[2].split(',')])

            for doc in result[4].split(","):
                if doc != "none":
                    meta.append(doc)

            for doc in tempList[1]:
                docs.append(doc)
                docCount[doc] += 1

            wordIndex.append(tempList)

    if wordIndex == []:
        return [], []

    if len(queryWords) > 2:
        docs = np.array([doc for doc in docCount if docCount[doc] >= 2])
    else:
        docs = np.unique(docs)

    docMatrix = np.zeros((len(docs), len(queryWords)))

    for i in range(len(docs)):
        for j in range(len(queryWords)):
            if docs[i] in wordIndex[j][1]:
                docMatrix[i, j] = wordIndex[j][2][wordIndex[j][1].index(docs[i])]

    queryVector = []
    for word in queryWords:
        queryVector.append(queryValues[word])

    queryVector = np.expand_dims(np.array(queryVector), axis=1)
    queryLength = np.sqrt(np.sum(queryVector ** 2, axis=0))
    queryVector = queryVector / queryLength

    vectorLengths = np.sqrt(np.sum(docMatrix ** 2, axis=1))
    docMatrix = docMatrix / vectorLengths[:, np.newaxis]

    dotResult = docMatrix.dot(queryVector).T[0]

    for doc in docs:
        if doc in meta:
            dotResult[np.where(docs == doc)] *= 2

    rank = np.argsort(dotResult)[::-1]
    sortedDocs = docs[rank]
    urls = []
    for doc in sortedDocs:
        urls.append(urlDict[doc])

    return sortedDocs, urls
