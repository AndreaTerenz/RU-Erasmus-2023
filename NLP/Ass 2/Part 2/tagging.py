import nltk
from nltk.corpus import treebank
from nltk.tag import AffixTagger, UnigramTagger, BigramTagger, TrigramTagger
from sklearn.model_selection import train_test_split

random_state = 42

nltk.download('treebank', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)

# Split the tagged sentences of the Penn Treebank into a training set (first 3500 sentences) and a test set (the
# remaining sentences), print out the total count of each set, and print the first sentence in the test set

tagged_sentences = treebank.tagged_sents()
print(f"Total sentences: {len(tagged_sentences)}")

train_set, test_set = train_test_split(tagged_sentences, train_size=3500, random_state=random_state)

print(f"Training set size: {len(train_set)}")
print(f"Test set size: {len(test_set)}")

s0 = [token for (token, _) in test_set[0]]
print(f"First sentence in test set:")
print(" ".join(s0))


# Construct four taggers trained on the training set: an instance of an AffixTagger, UnigramTagger, Bigram-
# Tagger and a TrigramTagger (without any “backoff” model). Evaluate them on the test set, and print out
# the evaluation results.

affix_tagger = AffixTagger(train_set, affix_length=2)
unigram_tagger = UnigramTagger(train_set)
bigram_tagger = BigramTagger(train_set)
trigram_tagger = TrigramTagger(train_set)

print("TAGGING ACCURACIES:")
print(f"\tAffix: {affix_tagger.accuracy(test_set):.2f}%")
print(f"\tUnigram: {unigram_tagger.accuracy(test_set):.2f}%")
print(f"\tBigram: {bigram_tagger.accuracy(test_set):.2f}%")
print(f"\tTrigram: {trigram_tagger.accuracy(test_set):.2f}%")

# Construct the latter three taggers again, but now with a backoff model, i.e. such that the trigram tagger
# uses a bigram tagger as backoff, which in turn uses a unigram tagger as backoff, which in turn uses the affix
# tagger as backoff. Print the evaluation results again.

affix_tagger = AffixTagger(train_set, affix_length=2)
unigram_tagger_bo = UnigramTagger(train_set, backoff=affix_tagger)
bigram_tagger_bo = BigramTagger(train_set, backoff=unigram_tagger_bo)
trigram_tagger_bo = TrigramTagger(train_set, backoff=bigram_tagger_bo)

print("BACKOFF TAGGING ACCURACIES:")
print(f"\tUnigram (with affix backoff): {unigram_tagger_bo.accuracy(test_set):.2f}%")
print(f"\tBigram (with unigram backoff): {bigram_tagger_bo.accuracy(test_set):.2f}%")
print(f"\tTrigram (with bigram backoff): {trigram_tagger_bo.accuracy(test_set):.2f}%")

# You will notice that the tagging accuracy for the individual taggers without a backoff model is (much) lower
# than the tagging accuracy for the corresponding taggers when using a backoff model. Explain why this is
# the case. In particular explain this for the case of the BigramTagger .
# 
# As n grows, an n-gram tagger captures more and more context to predict the tag for the current word, which,
# however, also makes its predictions dependent on increasingly specific data - this is why a bigram tagger
# may go from a training accuracy of around 90% to a testing accuracy below 20%. Using a simpler model as a
# backoff makes the tagger able to handle unseen contexts that, when reduced to less token or even to just an
# affix, become manageable for a simpler model.
# ---

# Tag the test set with the default (“off-the-shelf”) tagger in the NLTK, evaluate its accuracy and print out
# the result. Note that for this tagger you cannot simply call a built-in evaluation function, instead you have
# to write your own, which compares the results of the tagger to the gold standard

# tag the test set with pos_tag
pos_tagged_sentences = [nltk.pos_tag([token for (token, _) in sentence]) for sentence in test_set]
pos_tagged_sentences = [[tag for (_, tag) in sentence] for sentence in pos_tagged_sentences]

gold_tagged_sentences = [[tag for (_, tag) in sentence] for sentence in test_set]

# evaluate the accuracy of the tagger
correct = 0
total = 0
for i in range(len(pos_tagged_sentences)):
    sent_len = len(pos_tagged_sentences[i])
    total += sent_len
    
    for j in range(sent_len):
        if pos_tagged_sentences[i][j] == gold_tagged_sentences[i][j]:
            correct += 1

print(f"Default tagger accuracy: {correct / total:.2f}%")


