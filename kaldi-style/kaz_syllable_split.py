# -*- coding: utf-8 -*-
#
# Author: Josh Meyer 2016
#
# INPUT: (1) a cleaned text corpus
#
# OUTPUT: (1) words broken up by syllable
#

#

import re

consonant = "п|б|д|т|к|г|х|ш|щ|ж|з|с|ц|ч|й|л|м|н|ң|ф|в|р|ъ|ь"
vowel = "и|е|э|ө|ү|а|о|у|ы"
glide = "ё|я|ю|е"

f = open("clean.txt", "r", encoding="utf-8")

# VCV --> V@ @CV
vcv = re.compile("("+vowel+"|"+glide+")("+consonant+")("+vowel+")")
# VCCV --> VC@ @CV
vccv = re.compile("("+vowel+"|"+glide+")("+consonant+")("+consonant+")("+vowel+")")
# VCCC --> VCC@ @C
vccc = re.compile("("+vowel+"|"+glide+")("+consonant+")("+consonant+")("+consonant+")")
# VGV --> V@ @GV
vgv = re.compile("("+vowel+"|"+glide+")("+glide+")")


for line in f:
    for word in line.split():
        lenWord = len(word)+1

        # VCV --> V@ @CV
        i=0
        j=3
        while j<lenWord:
            if re.match(vcv,word[i:j]):
                word = word[:i+1] + "@ @" + word[i+1:]
                i+=3
                j+=3
                lenWord+=3                
            else:
                i+=1
                j+=1

        # VCCV --> VC@ @CV
        i=0
        j=4
        while j<lenWord:
            if re.match(vccv,word[i:j]):
                word = word[:i+2] + "@ @" + word[i+2:]
                i+=3
                j+=3
                lenWord+=3                
            else:
                i+=1
                j+=1

        # VCCC --> VCC@ @C
        i=0
        j=4
        while j<lenWord:
            if re.match(vccc,word[i:j]):
                word = word[:i+3] + "@ @" + word[i+3:]
                i+=3
                j+=3
                lenWord+=3                
            else:
                i+=1
                j+=1

        # VGV --> V@ @GV
        i=0
        j=2
        while j<lenWord:
            if re.match(vgv,word[i:j]):
                word = word[:i+1] + "@ @" + word[i+1:]
                i+=3
                j+=3
                lenWord+=3                
            else:
                i+=1
                j+=1

        print(word)

