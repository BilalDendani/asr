'''
Author: Joshua Meyer

USAGE:$ python3 ngrams.py -i INFILE -s SMOOTHING -b BACKOFF

DESCRIPTION: Given a cleaned corpus (text file), output a model of n-grams 
in ARPA format


#####################
The MIT License (MIT)

Copyright (c) 2016 

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
#####################
'''

from corpus_stats import *
from backoff import get_brants_bow_dict
import argparse
import operator
import numpy as np
from collections import Counter
import re
import time
import sys

def parse_user_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i','--infile', type=str, help='the input text file')
    parser.add_argument('-s','--smoothing',type=str, help='flavor of smoothing',
                        choices = ['none','laplace','turing'], default='none')
    parser.add_argument('-bo','--backoff', action='store_true',
                        help='add backoff weights')
    args = parser.parse_args()
    return args


def get_ngram_tuples(lines,startTime,lenSentenceCutoff):
    unigrams=[]
    bigrams=[]
    trigrams=[]
    for line in lines.split('\n'):
        line = line.split(' ')
        if len(line) >lenSentenceCutoff:
            unigrams+=get_ngrams_from_line(line,1)
            bigrams+=get_ngrams_from_line(line,2)
            trigrams+=get_ngrams_from_line(line,3)
    print('[  '+ str("%.2f" % (time.time()-startTime)) +'  \t]'+
          ' A total of ' +str(len(unigrams))+
          ' unigrams found')
    print('[  '+ str("%.2f" % (time.time()-startTime)) +'  \t]'+ ' A total of '+
          str(len(bigrams)) + ' bigrams found')
    print('[  '+ str("%.2f" % (time.time()-startTime)) +'  \t]'+ ' A total of '+
          str(len(trigrams)) + ' trigrams found')
    return unigrams, bigrams, trigrams


def get_ngrams_from_line(tokens, n):
    '''
    Given a list of tokens, return a list of tuple ngrams
    '''
    ngrams=[]
    # special case for unigrams
    if n==1:
        for token in tokens:
            # we need parentheses and a comma to make a tuple
            ngrams.append((token,))
    # general n-gram case
    else:
        for i in range(len(tokens)-(n-1)):
            ngrams.append(tuple(tokens[i:i+n]))
    return ngrams


def print_to_file(uniBowDict,biBowDict,triMLEdict,
                  backoff,smoothing,startTime):
    if backoff:
        backedOff = 'yes'
    else:
        backedOff = 'no'
        
    with open(('lm_smoothing-' + smoothing +
               '_backoff-' + backedOff +
               '.txt'),
              'w', encoding = 'utf-8') as outFile:
        # Print ARPA preamble
        outFile.write('\n\data\\\n')
        outFile.write('ngram 1=' + str(len(uniBowDict)) +'\n')
        outFile.write('ngram 2=' + str(len(biBowDict)) +'\n')
        outFile.write('ngram 3=' + str(len(triMLEdict)) +'\n')

        ## print unigrams
        outFile.write('\n\\1-grams:\n')
        sortedUni = sorted(uniBowDict.items(), key=operator.itemgetter(1),
                          reverse=True)
        for key,value in sortedUni:
            if backoff:
                entry = (str(value[0]) +' '+ key[0] +' '+
                         str(value[1]))
            else:
                entry = (str(value[0]) +' '+ key[0])
            outFile.write(entry+'\n')
            
        ## print bigrams
        outFile.write('\n\\2-grams:\n')
        sortedBi = sorted(biBowDict.items(), key=operator.itemgetter(1),
                           reverse=True)
        for key,value in sortedBi:
            if backoff:
                entry = (str(value[0]) +' '+ key[0] +' '+ key[1] +' '+
                         str(value[1]))
            else:
                entry = (str(value[0]) +' '+ key[0] +' '+ key[1])
            outFile.write(entry+'\n')

        ## print trigrams
        outFile.write('\n\\3-grams:\n')
        sortedTri = sorted(triMLEdict.items(), key=operator.itemgetter(1),
                           reverse=True)
        for key,value in sortedTri:
            entry = (str(value) +' '+ key[0] +' '+ key[1] +' '+ key[2])
            outFile.write(entry+'\n')
        outFile.write('\n\end\\')
    print('[  '+ str("%.2f" % (time.time()-startTime)) +'  \t]'+
          ' successfully printed model to file!')


def main():
    # get user input
    args = parse_user_args()
    fileName = args.infile
    smoothing = args.smoothing
    backoff = args.backoff
    
    startTime = time.time()
    print('[  '+ str("%.2f" % (time.time()-startTime)) +'  \t]'+ ' running')

    # open previously cleaned file
    f = open(fileName)
    lines = ''
    for line in f:
        lines += line
        
    # get lists of tuples of ngrams
    unigrams, bigrams, trigrams = get_ngram_tuples(lines,startTime,
                                                   lenSentenceCutoff=4)

    # get raw count dictionaries
    uniCountDict = get_count_dict(unigrams)
    biCountDict = get_count_dict(bigrams)
    triCountDict = get_count_dict(trigrams)

    # divide unigram counts by number of unigrams to get probability
    N = sum(uniCountDict.values())
    uniProbDict = {}
    for key,value in uniCountDict.items():
        uniProbDict[key] = np.log(value/N)

    # get conditional probabilities (maximum likelihood) for all ngrams that 
    # are not unigrams
    biMLEdict = get_MLE_dict(uniCountDict,biCountDict,2)
    triMLEdict = get_MLE_dict(biCountDict,triCountDict,3)

    # get backoff weighting
    uniBowDict = get_brants_bow_dict(uniProbDict)
    biBowDict = get_brants_bow_dict(biMLEdict)
    
    print_to_file(uniBowDict,biBowDict,triMLEdict,backoff,smoothing,startTime)


if __name__ == "__main__":
    main()
