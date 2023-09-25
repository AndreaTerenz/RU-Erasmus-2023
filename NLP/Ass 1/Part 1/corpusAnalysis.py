"""
Write a Python program, corpusAnalysis.py, which prints out various statistics/information about a given text file, which is a part of the Gutenberg corpus (accessible using NLTK). The name of the text file is given as a parameter to the program, i.e.:

python corpusAnalysis.py carroll-alice.txt

The program should print out the following information for the given text file:

Text: carroll-alice.txt
Tokens: 34110
Types: 3016
Types excluding stop words: 2872
10 most common tokens: [(',', 1993), ("'", 1731), ('the', 1527), ('and', 802), ('.', 764), ('to', 725), ('a', 615), ('I', 543), ('it', 527), ('she', 509)]
Long types: ['affectionately', 'contemptuously', 'disappointment', 'Multiplication']
Nouns ending in 'ation' ['usurpation', 'station', 'accusation', 'invitation', 'consultation', 'sensation', 'explanation', 'Multiplication', 'conversation', 'Uglification', 'exclamation']

Note: Long types are those with more than 13 characters.
"""

import nltk
import sys
from nltk.corpus import gutenberg, stopwords

nltk.download('gutenberg', quiet=True)
nltk.download('stopwords', quiet=True)

def filter_text(text, condition):
    return [word for word in text if condition(word)]

def main():
    file = sys.argv[1]

    text = gutenberg.words(file)
    text = [word.lower() for word in text]
    text_set = set(text)
    en_stopwords = stopwords.words('english')

    print(f"Text: {file}")
    print(f"Tokens: {len(text)}")
    print(f"Types: {len(text_set)}")

    words_nostop = filter_text(text_set, lambda w: w not in en_stopwords)
    print(f"Types excluding stop words: {len(words_nostop)}")

    freq = nltk.FreqDist(text)
    print(f"10 most common tokens: {freq.most_common(10)}")

    long_type_limit = 13
    words_longtype = filter_text(text_set, lambda w: len(w) > long_type_limit)
    print(f"Long types: {words_longtype}")

    words_ation = filter_text(text_set, lambda w: w.endswith('ation'))
    print(f"Nouns ending in 'ation' {words_ation}")
    
if __name__ == "__main__":
    main()