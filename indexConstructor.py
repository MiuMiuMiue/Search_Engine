import sqlite3
from read import TextProcessor
from TF_IDF import TfIdfCalculation
from collections import defaultdict
from node import Node
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="bs4")

class IndexConstructor:
    """This class has the methods that needed to build index."""
    def __init__(self, path, dir):
        self.reader = TextProcessor()
        self.calculator = TfIdfCalculation()

        self.word_dict = {}
        self.total_word_dict = defaultdict(int)

        self.dirPath = path
        self.currentDir = dir

    def iterDirectory(self) -> int:
        """This method iterates current directory and returned the number of files"""
        count = 0
        countProgress = 0
        for file in self.dirPath.iterdir():
            countProgress += 1
            count += 1

            fileDict = defaultdict(int)

            parsed = self.reader.readText(file)
            tokens = self.reader.wordTokenizer(parsed)
            self.metaTokens = self.reader.importantTokens(parsed)

            fileID = self.currentDir + '/' + file.name

            self.parse(tokens, fileID, fileDict)
            tfDict = self.calculator.calculateTF(fileDict)

            for key in tfDict.keys():
                self.total_word_dict[key] += 1
                currentNode = self.word_dict[key]

                while currentNode.hasNext():
                    if currentNode.getDocID() == fileID:
                        break
                    currentNode = currentNode.getNext()

                currentNode.setTFIDF(tfDict[key])

        return count

    def parse(self, tokens, fileID, fileDict) -> None:
        """This method manages the tokens in the current file."""
        for token in tokens:
            meta = False
            if token in self.metaTokens:
                meta = True

            token = token.replace("\x00", "")
            fileDict[token] += 1

            if token not in self.word_dict.keys():
                node = Node(fileID, wordFreq=1)
                self.word_dict[token] = node

                if meta:
                    node.meta = True
            else:
                currentNode = self.word_dict[token]

                while currentNode.hasNext():
                    if currentNode.getDocID() == fileID:
                        break
                    currentNode = currentNode.getNext()

                if currentNode.getDocID() == fileID:
                    currentNode.incrementFreq()

                    if meta:
                        currentNode.meta = True
                else:
                    node = Node(fileID, wordFreq=1)
                    currentNode.next = node

                    if meta:
                        node.meta = True

    def addToDataBase(self) -> None:
        """This method insert values into the corresponding sql database"""
        count = 0
        for key in self.word_dict.keys():
            try:
                count += 1
                currentNode = self.word_dict[key]
                docIDs = ""
                tfIdfs = ""
                wordFreq = ""
                meta = ""
                while currentNode != None:
                    docIDs += (currentNode.getDocID() + ",")
                    tfIdfs += str(currentNode.getTFIDF()) + ","
                    wordFreq += str(currentNode.getWordFreq()) + ","
                    if currentNode.getMeta():
                        meta += (currentNode.getDocID() + ",")
                    else:
                        meta += "none,"
                    currentNode = currentNode.getNext()
                self.indexCursor.execute(f"""
                INSERT INTO init_index (word, doc_id, tf_idf, word_freq, meta)
                VALUES ('{key}', '{docIDs}', '{tfIdfs}', '{wordFreq}', '{meta}')
                """)
            except sqlite3.OperationalError as e:
                pass

        count = 0
        keys = list(self.total_word_dict.keys())

        for key in keys:
            count += 1
            try:
                self.wordCursor.execute(f"""
                INSERT INTO word_collection (word, doc_freq)
                VALUES ('{key}', {self.total_word_dict[key]})
                """)
            except sqlite3.OperationalError as e:
                pass

    def setCursor(self, indexCursor, wordCursor) -> None:
        """This method sets the cursors."""
        self.indexCursor = indexCursor
        self.wordCursor = wordCursor
