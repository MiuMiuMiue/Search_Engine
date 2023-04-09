from indexConstructor import IndexConstructor
from TF_IDF import TfIdfCalculation
from pathlib import Path
from readTitles import ReadTitles
import sqlite3
import sys
import atexit
import time
import math

startProgram = time.time()

def emergentExit():
    global conn1, conn2, conn3, conn4
    conn1.commit()
    conn2.commit()
    conn3.commit()
    conn4.commit()
    conn1.close()
    conn2.close()
    conn3.close()
    conn4.close()

path = Path(sys.argv[1])
calculator = TfIdfCalculation()

conn1 = sqlite3.connect("init_index.db")
conn2 = sqlite3.connect("word_collection.db")
conn3 = sqlite3.connect("index.db")
conn4 = sqlite3.connect("idf.db")

indexCursor1 = conn1.cursor()
wordCursor = conn2.cursor()
indexCursor2 = conn3.cursor()
idfCursor = conn4.cursor()

indexCursor1.execute("""
CREATE TABLE IF NOT EXISTS init_index (
    word TEXT,
    doc_id TEXT,
    tf_idf TEXT,
    word_freq TEXT,
    meta TEXT
)
""")

wordCursor.execute("""
CREATE TABLE IF NOT EXISTS word_collection (
    word TEXT,
    doc_freq INTEGER
)
""")

indexCursor2.execute("""
CREATE TABLE indexTable (
    word TEXT PRIMARY KEY,
    doc_id TEXT,
    tf_idf TEXT,
    word_freq TEXT, 
    meta TEXT
)
""")

idfCursor.execute("""
CREATE TABLE idfTable (
    word TEXT PRIMARY KEY,
    idf INTEGER
)
""")

atexit.register(emergentExit)

totalDoc = 0
for dir in path.iterdir():
    print("Current directory: ", dir.name)
    start = time.time()
    if dir.is_dir():
        constructor = IndexConstructor(dir, dir.name)
        constructor.setCursor(indexCursor1, wordCursor)
        print("\tStart iterating files")
        count = constructor.iterDirectory()
        print("\tStart adding info into databases")
        constructor.addToDataBase()
        totalDoc += count
    totalSec = time.time() - start
    print(f"\tTotal time: {totalSec // 60} min {totalSec % 60:.2f} sec")
    print("End of directory", dir.name)

wordCursor.execute("""
SELECT *
FROM word_collection
ORDER BY word
""")

result = wordCursor.fetchall()
total1 = len(result)
wordResult = []
prevWord = ""
freq = 0

count1 = 0
for row in result:
    count1 += 1
    if prevWord == "":
        prevWord = row[0]
        freq += row[1]
    elif prevWord == row[0]:
        freq += row[1]
    elif prevWord != row[1]:
        wordResult.append([prevWord, freq])
        prevWord = row[0]
        freq = row[1]

wordResult.append([prevWord, freq])
idfDict = calculator.calculateIDF(wordResult, totalDoc)

for key in idfDict.keys():
    idfCursor.execute(f"""
        INSERT INTO idfTable (word, idf)
        VALUES ('{key}', {idfDict[key]})
    """)

print("totalDoc is: ", totalDoc)
indexCursor1.execute("""
SELECT * 
FROM init_index
ORDER BY word
""")

indexResult = indexCursor1.fetchall()
total2 = len(indexResult)
prevWord = ""
docIDs = ""
tfIdfs = []
wordFreq = ""
meta = ""

count2 = 0
for row in indexResult:
    count2 += 1
    if prevWord == "":
        prevWord = row[0]
        docIDs += row[1]
        wordFreq += row[3]
        meta += row[4]
        init_tfIdfs = [float(x) for x in row[2].strip(',').split(',')]
        for num in init_tfIdfs:
            tfIdfs.append(str(num * idfDict[row[0]]))
    elif row[0] != prevWord:
        newTfIdfs = ",".join(tfIdfs)
        try:
            indexCursor2.execute(f"""
            INSERT INTO indexTable (word, doc_id, tf_idf, word_freq, meta)
            VALUES ('{prevWord}', '{docIDs.strip(",")}', '{newTfIdfs}', '{wordFreq.strip(',')}', '{meta.strip(',')}')
            """)
        except sqlite3.OperationalError:
            pass
        prevWord = row[0]
        docIDs = ""
        tfIdfs.clear()
        wordFreq = ""
        meta = ""
        docIDs += row[1]
        wordFreq += row[3]
        meta += row[4]
        init_tfIdfs = [float(x) for x in row[2].strip(',').split(',')]
        for num in init_tfIdfs:
            tfIdfs.append(str(num * idfDict[row[0]]))
    elif row[0] == prevWord:
        docIDs += row[1]
        wordFreq += row[3]
        meta += row[4]
        init_tfIdfs = [float(x) for x in row[2].strip(',').split(',')]
        for num in init_tfIdfs:
            tfIdfs.append(str(num * idfDict[row[0]]))

newTfIdfs = ",".join(tfIdfs)
indexCursor2.execute(f"""
        INSERT INTO indexTable (word, doc_id, tf_idf, word_freq, meta)
        VALUES ('{prevWord}', '{docIDs.strip(",")}', '{newTfIdfs}', '{wordFreq.strip(',')}', '{meta.strip(',')}')
        """)

ReadTitles()

print(f"Used {math.ceil((time.time() - startProgram) // 60)} min to run this program.")