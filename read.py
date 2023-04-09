from bs4 import BeautifulSoup
import nltk
nltk.download("punkt")
nltk.download("wordnet")
nltk.download('omw-1.4')
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer


class TextProcessor:
    """This class has the methods that are needed to read files."""
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()

    def readText(self, file) -> BeautifulSoup:
        """This method parses each file using BeautifulSoup"""
        with open(file, "r", encoding="ascii", errors='ignore') as fileObj:
            content = fileObj.read()
            parsedContent = BeautifulSoup(content, "html.parser")

            return parsedContent

    def wordTokenizer(self, parsedContent) -> list[str]:
        """This method tokenizes the given parsed content using nltk.regexTokenizer"""
        text = parsedContent.get_text()
        text2 = ' '

        for tag in parsedContent.find_all(True):
            if tag.get('title'):
                text2 += tag['title'].strip() + ' '

        tokenizer = RegexpTokenizer(r'[^\W_]+')
        words = tokenizer.tokenize(text + text2)

        alphanumeric_words = [self.lemmatizer.lemmatize(word.lower()) for word in words]
        return alphanumeric_words

    def importantTokens(self, parsedContent) -> list[str]:
        """This method detects the tokens in titles."""
        headings = parsedContent.find_all(["h1", "h2", "h3", "title"])
        words = []

        for heading in headings:
            tokenizer = RegexpTokenizer(r'[^\W_]+')
            tokens = tokenizer.tokenize(heading.text)
            for token in tokens:
                words.append(token)

        result = [self.lemmatizer.lemmatize(word.lower()) for word in words]
        return result
