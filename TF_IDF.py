import math

class TfIdfCalculation():
    def calculateTF(self, wordDict: dict) -> dict:
        tfDict = {}
        for word in wordDict:
            tfDict[word] = 1 + math.log10(wordDict[word])
        return tfDict

    def calculateIDF(self, data: list, total: int) -> dict:
        docDict = {}
        for row in data:
            docDict[row[0]] = math.log10((total / row[1]))
        return docDict
