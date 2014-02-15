###############################################################################
# waffle.py
###############################################################################
# A program to increase the length of a piece of text by substituting each
# word for its longest synonym.
###############################################################################
# 05/10 Flembobs
###############################################################################

import urllib2
import sys
import getopt
import re

###############################################################################
# GLOBAL DATA
###############################################################################

#key to the big huge thesaurus, please don't abuse!
API_KEY = "5c4d0c2dfb2dbab70a98f2938d9505bf"

#this dictionary stores the longest synonym of any word that is looked up so
#that it won't be processed twice
word_cache = dict()

#Tuple of characters that are treated as punctuation when converting a
#word.
PUNCTUATION = (".","!",",","?","-","'","\"",";",":")

###############################################################################
# FUNCTIONS
###############################################################################

def query_word(word):
    """
    Queries a word in the thesaurus and returns the raw text from big huge.
    
    Returns the word itself if we get a 404.
    """
    
    #Construct the url to be queried for the word
    BHurl =  "http://words.bighugelabs.com/api/2/"
    BHurl += API_KEY+"/"
    BHurl += word+"/"
    
    #open the url
    try:
        f = urllib2.urlopen(BHurl)
    except:
        return word
    
    #return the raw data
    return f.read()
    
#------------------------------------------------------------------------------
    
def longest_syn(text):
    """
    Scans the raw output from a queried word, returning the longest synonyn.
    """
    
    #the string value of the longest word
    longest = ""
    
    #the number of words that the longest word has
    longest_words = 0
    
    #each line of text is a tuple (type,syn/ant,word)
    for tup in text.split("\n"):
        tup = tup.split("|")
        
        if len(tup) != 3:
            continue
        
        if tup[1]=="ant":
            continue

        #extract the word from the tuple
        cur_word = tup[2]

        #count the no of words in the syn
        spaces = cur_word.count(" ")

        #if it has fewer spaces, continue
        if spaces < longest_words:
            continue

        #if it has more spaces, set it as new longest
        if spaces > longest_words:
            longest = cur_word
            longest_words = spaces
            continue
            
        #if it is longer, but same amount of spaces - new longest word
        if len(cur_word) > len(longest):
            longest = cur_word
            longest_words = spaces


    return longest
    
#------------------------------------------------------------------------------

def convert_word(word):
    """
    Takes a word and converts it to its longest synonym, preserving
    punctuation and capitalization.
    """
    
    #flag set to true if the first letter of the word is capitalized
    cap = False
    
    #appended at the end of a word
    punc = ""
    
    #check for empty strings
    if len(word) < 1:
        return word
        
    #check if the word doesn't contain any letters
    if re.search("[a-zA-Z]",word) is None:
        return word
    
    #strip off all punctuation and save it in the punc var
    while word[-1] in PUNCTUATION:
        punc = word[-1]+punc
        word = word[0:-1]

    #if word is hyphenated, seperate into component parts and solve recursively
    split_word = word.split("-",1)
    if len(split_word) > 1:
    
        if len(split_word[1])>0:
            return convert_word(split_word[0])+ \
                   "-"+convert_word(split_word[1])+punc

    #save capitals
    if word.istitle():
        cap = True
        word = word.lower()
        
    #see if the word is in the cache
    try:
        word = word_cache[word]
        
    #word is not in the cache, look it up
    except KeyError:
        raw = query_word(word)
        
        #if there are no synonyms
        if raw == word:
            word_cache[word] = word
            
        #save the longest syn
        else:
            LS = longest_syn(raw)
            word_cache[word] = LS
            word = LS
            
    if cap:
        word = word.capitalize()
        
    return word+punc
    
#------------------------------------------------------------------------------

def process_file(input_file,output_file):

    try:
        input_file = open(input_file)
    except:
        print "Error:  Cannot open input file for reading."
        return
        
    try:
        output_file = open(output_file,"w")
    except:
        print "Error:  Cannot open output file for writing."
        return
        
    text = input_file.read()
    input_file.close()
    
    to_write = ""
    
    for line in text.split("\n"):
        for word in line.split(" "):
            to_write+= convert_word(word)+" "
        to_write+="\n"
        
    output_file.write(to_write)
    output_file.close()

    
###############################################################################
# MAIN EXECUTION
###############################################################################

#print convert_word("love!-love!")
#print word_cache

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "", [])
        except getopt.error, msg:
             raise Usage(msg)

        if len(args) != 2:
            print "Usage: waffle [input_file] [output_file]"
            return 2

        process_file(args[0],args[1])
        
        print "Wafflization complete!"

    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "Usage: waffle [input_file] [output_file]"
        return 2

if __name__ == "__main__":
    sys.exit(main())