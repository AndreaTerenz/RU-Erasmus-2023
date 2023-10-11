import nltk
from nltk.corpus.reader import TaggedCorpusReader

# Read in MIM-GOLD using the class TaggedCorpusReader, display the number of sentences, and display the individual tokens of sentence no. 100
corpus_root = "."
corpus_file = "MIM-GOLD.sent"

mim_gold = TaggedCorpusReader(corpus_root, corpus_file) 

sentences = mim_gold.sents()
tokens = mim_gold.words()
tags = [tag for (_, tag) in mim_gold.tagged_words()]

print(f"Number of sentences: {len(sentences)}")
print("Sentence no. 100:")
print(" ".join(sentences[99]))

# Display the number of tokens and the number of types in MIM-GOLD.
print(f"Number of tokens: {len(tokens)}")
print(f"Number of unique tokens: {len(set(tokens))}")
print(f"Number of tags: {len(set(tags))}")

# Display the 10 most frequent tokens in MIM-GOLD using the class FreqDist.
freqDist_tokens = nltk.FreqDist(tokens)
print(f"10 most common tokens: \n")
print(*freqDist_tokens.most_common(n=10), sep="\n")

# Display the 20 most frequent POS tags in MIM-GOLD using the class FreqDist
freqDist_tags = nltk.FreqDist(tags)
print(f"20 most common POS tags: \n")
print(*freqDist_tags.most_common(n=20), sep="\n")

# Generate tag bigrams and use the class ConditionalFreqDist to print out the 10 most frequent tags that can follow the tag 'af' (this tag denotes a preposition)
bigrams = nltk.bigrams(tags)
cfd = nltk.ConditionalFreqDist(bigrams)
target = "AF"

print(f"10 most frequent tags that can follow the tag '{target}': \n")
print(*cfd[target].most_common(n=10), sep="\n")


