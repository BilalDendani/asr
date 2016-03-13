#!/usr/bin/env perl
#
# Author: Josh Meyer 2016
#
# INPUT: (1) a cleaned text corpus
#
# OUTPUT: (1) a file of word:pronunciation pairs (a phonetic dict)
#         (2) a list of the phones used in the lookuptable
#
# FUNCTION:
#   The script tokenizes a corpus and returns a file of word:pronunciation pairs
#
#   This script requires a completely cleaned corpus, i.e. the text must have
#   *no* puncutation and *no* numbers.
#
#   HOWEVER, it won't break if you give it utterancess with <s>'s.
#

use warnings;
use strict;

my $clean_corpus = $ARGV[0];
my $phoneticDict = $ARGV[1];
my $phoneticDict_NOSIL = $ARGV[2];

my $phones = $ARGV[3];
my $silence_word = $ARGV[4];
my $silence_phone = $ARGV[5];
my $unknown_word = $ARGV[6];
my $unknown_phone = $ARGV[7];


open CLEAN_CORPUS, $clean_corpus, or die "Could not open $clean_corpus: $!";
open PHONETICDICT, ">>", $phoneticDict, or die "Could not open $phoneticDict: $!";
open PHONETICDICT_NOSIL, ">>", $phoneticDict_NOSIL, or die "Could not open $phoneticDict_NOSIL: $!";
open PHONELIST, ">>", $phones, or die "Could not open $phones: $!";

# the default lookup table - if our context dependent rules don't make a
# character, it gets replaced according to the table
my %phoneTable = ("а"=>"a ", # back vowels
                  "о"=>"o ",
                  "у"=>"u ",
                  "ы"=>"ih ",
                  "и"=>"i ", # front vowels
                  "е"=>"e ",
                  "э"=>"e ",
                  "ө"=>"oe ",
                  "ү"=>"y ",
                  "ю"=>"j u ", # glide vowels
                  "я"=>"j a ",
                  "ё"=>"j o ",
                  "п"=>"p ", # bilabials
                  "б"=>"b ",
                  "д"=>"d ", # coronals
                  "т"=>"t ",
                  "к"=>"k ", # velars
                  "г"=>"g ",
                  "х"=>"h ",
                  "ш"=>"sh ", # (alveo)(palatals)
                  "щ"=>"sh ",
                  "ж"=>"zh ",
                  "з"=>"z ", 
                  "с"=>"s ",
                  "ц"=>"ts ", # affricates
                  "ч"=>"ch ",
                  "й"=>"j ", # glides
                  "л"=>"l ",
                  "м"=>"m ", # nasals
                  "н"=>"n ",
                  "ң"=>"ng ",
                  "ф"=>"f ", # labiodentals
                  "в"=>"v ",
                  "р"=>"r ", # trill
                  "ъ"=>"",
                  "ь"=>"");

# Idk why, but the [abc] notation doesnt work here
my $consonant = "п|б|д|т|к|г|х|ш|щ|ж|з|с|ц|ч|й|л|м|н|ң|ф|в|р|ъ|ь";
my $frontVowel = "и|е|э|ө|ү";
my $backVowel = "а|о|у|ы";


###
## MAKE pronunciations and store in dict
#


# make a hash dictionary of token:pronunciation pairs
my %hash;

# add our entries for unknown words and silence to the dictionary
$hash{$silence_word} = $silence_phone;
$hash{$unknown_word} = $unknown_phone;

while (my $line = <CLEAN_CORPUS>) {
    my @tokens = split(' ', $line);
    foreach my $token (@tokens) {
        if (exists $hash{$token}) {
            # we've seen this token already
            # so we just pass it
            next;
        } else {
            my $phones = $token;
            for($phones) {
                # syllable onset plosives followed by front/back vowels
                s/к($backVowel)/kh $1/g;
                s/к($frontVowel)/k $1/g;
                s/г($backVowel)/gh $1/g;
                s/г($frontVowel)/g $1/g;
                # syllable final plosives preceded by front/back vowels
                s/($backVowel)к($consonant)/$1kh $2/g;
                s/($frontVowel)к($consonant)/$1k $2/g;
                s/($backVowel)г($consonant)/$1gh $2/g;
                s/($frontVowel)г($consonant)/$1g $2/g;
                # word final plosives preceded by front/back vowels
                s/($backVowel)к$/$1kh/g;
                s/($frontVowel)к$/$1k/g;
                s/($backVowel)г$/$1gh/g;
                s/($frontVowel)г$/$1g/g;
            }
            $phones =~ s/(@{[join "|", keys %phoneTable]})/$phoneTable{$1}/g;
            $phones =~ s/^\s+//g;
            $phones =~ s/\s+$//g;
            $hash{$token} = $phones;
        }
    }
}

###
##  PRINT word:pronunciation pairs to text files
##    lexicon.txt and nosil_lexicon.txt
#      and also save phones to char string

# get phones from lookup table
my $phoneList = "";

foreach my $key (keys %hash) {
    if ($key eq "<s>" || $key eq "</s>") {
        next;
    } else {
        print PHONETICDICT "$key $hash{$key}\n";
        $phoneList .= " $hash{$key} ";
        if ($key ne $silence_word && $key ne $unknown_word) {
            print PHONETICDICT_NOSIL "$key $hash{$key}\n";
        }
    }
}




###
## PRINT UNIQUE PHONES TO FILE
#

# clean up phoneList
for ($phoneList) {
    # remove trailing whitespace
    s/^\s+//;
    s/\s+$//;
    # remove any newlines anywhere
    s/\n+/ /g;
    # replace multiple spaces with just one
    s/ +/ /g;
}

my @phones = split / /, $phoneList;
my %seen = ();
foreach my $item (@phones) {
    if ($seen{$item}) {
        next;
    } else {
        $seen{$item} = 1;
        print PHONELIST "$item\n"
    }
}

