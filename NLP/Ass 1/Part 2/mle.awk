BEGIN{ 
    total_bigram = 0;
    total_trigram = 0;
} 
{
    prefix = $2 " " $3;
    if (prefix == bigram) {       
        total_bigram += $1;
        if ($NF == word) {
            total_trigram += $1;
        }
    }
}
END {
    probability = total_trigram / total_bigram;
    printf "%d / %d %.2f%%\n", total_trigram, total_bigram, 100*probability;
}