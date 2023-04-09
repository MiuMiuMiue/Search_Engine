class Node:
    """This class records the tokens' information"""
    def __init__(self, docID, tf_idf=0, wordFreq=0, next=None):
        self.docID = docID
        self.tf_idf = tf_idf
        self.wordFreq = wordFreq
        self.next = next
        self.meta = False

    def setDocID(self, id):
        self.docID = id

    def setTFIDF(self, value):
        self.tf_idf = value

    def setWordFreq(self, freq):
        self.wordFreq = freq

    def incrementFreq(self):
        self.wordFreq += 1

    def getDocID(self):
        return self.docID

    def getTFIDF(self):
        return self.tf_idf

    def getWordFreq(self):
        return self.wordFreq

    def hasNext(self):
        return True if self.next else False

    def getNext(self):
        return self.next

    def getMeta(self):
        return self.meta
