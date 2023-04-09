from takeQuery import findTopKUrl
import json
import sqlite3
import nltk
from flask import Flask, render_template, request

def get_db():
    """Returns a connection and cursor for the SQL database"""
    conn = sqlite3.connect('index.db')
    cursor = conn.cursor()
    return conn, cursor

file = open("D:\\UCI_documents\\2023_Winter_Quarter\\CS_121\\WEBPAGES_RAW\\bookkeeping.json", "r")
urlDict = json.load(file)
conn2 = sqlite3.connect("idf.db")
conn3 = sqlite3.connect("titles.db")
idfCursor = conn2.cursor()
titleCursor = conn3.cursor()
file.close()

titleDict = {}
titleCursor.execute("""
    SELECT *
    FROM titleTable
""")

titleResult = titleCursor.fetchall()
for row in titleResult:
    titleDict[row[0]] = row[1]

idfDict = {}
idfCursor.execute("""
    SELECT *
    FROM idfTable
""")

result = idfCursor.fetchall()
for row in result:
    idfDict[row[0]] = row[1]

app = Flask(__name__)

@app.route('/')
def home():
    """This function creates the home page by using the format in home.html."""
    return render_template('home.html')

@app.route('/search')
def search():
    conn, indexCursor = get_db()
    query = nltk.word_tokenize(request.args.get('wd'))
    docIDs, urls = findTopKUrl(query, urlDict, idfDict, indexCursor)
    conn.close()
    return render_template("searchWebsite.html", docIDs=docIDs, urls=urls, titles=titleDict, query=request.args.get('wd'))

if __name__ == '__main__':
    app.run()
