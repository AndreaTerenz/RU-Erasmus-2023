{ RS="" }
{
    for(i=1;i<=NF-2;i++){
        bigram = $i " " $(i+1);
        bigrams[bigram]++;
    }
}
{
    for(i=1;i<=NF-2;i++){
        trigram = $i " " $(i+1) " " $(i+2);
        bigram = $i " " $(i+1);

        trigrams[trigram] += 1.0; # / bigrams[bigram];
    }
}
{
    for(trigram in trigrams){
        print trigrams[trigram], trigram;
    }
}