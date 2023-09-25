# Assume counting from engTri.freq with non-normalized frequencies
BEGIN { total = 0 }
{ total += $1 }
END { 
    print "Unique trigrams:", NR, "| Total trigrams:", total;
}