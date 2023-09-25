1. How many times does the word ‘Macbeth’ appear in Shakespeare's works?

`cat shakes.txt | tr -sc "A-Za-z" "\n" | sort | uniq -c | grep "Macbeth | tr -sc "0-9" " "`

83 times

2. Normalize all contractions in the following string: *it's true that he doesn't know I've arrived*

*It is true that he does not know that I have arrived*

3. Stem all words in Shakespeare ending in -ed

Boh