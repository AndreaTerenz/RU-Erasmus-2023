import os

"""
eng.sent is pre-tokenised even though the <token,tag> pairs do not appear on a separate line. However, in order to construct the language model you need a file with one token (word) per line without any empty lines. Use awk for this purpose. Show the awk command that you use for constructing this file, eng.tok
"""
os.system(f"awk -f tokens.awk eng.sent > eng.tok")
os.system("less eng.tok")

"""
Show the sequence of commands you use to construct a trigram frequency file engTri.freq (from eng.tok ), sorted in descended order of frequency and containing four columns:
- frequency
- word1
- word2
- word3

Note that you can specify the flag -k1,1 to sort, for specifying sorting only on the first column
"""
os.system(f"awk -f frequency.awk eng.tok | sort -k1 -nr > engTri.freq")
os.system("less engTri.freq")

"""
How many trigrams and distinct trigrams exists in eng.sent? Use awk and wc and engTri.freq to figure this out (show your commands and the output)
"""
os.system("awk -f trigramCount.awk engTri.freq")

"""
Use the data from engTri.freq to estimate (using Maximum Likelihood Estimation):
P(Monday | said on)

Show which lines from engTri.freq you use to estimate this probability and your calculations
"""
os.system("awk -v bigram='said on' -v word='monday' -f mle.awk engTri.freq")
