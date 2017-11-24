import SPIMI as spimi
import os
import nltk
import json
from math import log

DOCUMENT_COUNT = 21578   
AVERAGE_DOC_LENGTH = 307.854206213
mappedURL = {}

def loadAfinn():
    dictionary = json.load(open('afinn_dictionary.json'))
    return dictionary

def loadDocSentiment():
    dictionary = json.load(open('sentiment_index.json'))
    return dictionary

def loadMapping():
    mapping = json.load(open('docID_URL_mapping.json'))
    return mapping

def sentimentSearch(matching_docs,query_sentiment_value,doc_sentiment):
    dictionary = dict()
    for doc_ID in matching_docs:
        dictionary[doc_ID] = doc_sentiment.get(str(doc_ID));

    print "\nSentiment of query: " + str(query_sentiment_value)
    print "The length of results list:{}".format(len(dictionary.keys()))

    # sorted the matching_docs from highest to lowest
    if query_sentiment_value >= 0:
        for doc, sent in sorted(dictionary.items(), key=lambda dictionary: dictionary[1], reverse=True):
            print mappedURL[str(doc)] + " (Sentiment: " + str(sent) + ")"
    else: # sorted the matching_docs from lowest to highest
        for doc, sent in sorted(dictionary.items(), key=lambda dictionary: dictionary[1], reverse=False):
            print mappedURL[str(doc)] + " (Sentiment: " + str(sent) + ")"

    print "\n"

# Should this handle long query BM25? 
def BM25(matching_docs, index, query, doc_lengths):
    k1 = 1.5
    k3 = 1.5
    b  = 0.75
    doc_scores = {}
    for doc in matching_docs:
        doc_scores[doc] = 0.0
        for term in query: 
            # Filter parentheses and bad OR terms
            try: 
                index[term]
                index[term][doc]
            except:
                continue 

            # Get doc length, with fallback 
            try: 
                doc_lengths[doc]
                doc_length = doc_lengths[doc]
            except: 
                doc_length = AVERAGE_DOC_LENGTH

            idf = log(DOCUMENT_COUNT/len(index[term]))
            tf = index[term][doc]

            top_term = (k1 + 1.0) * tf 
            bottom_term = k1 * ((1-b) + b * (doc_length/AVERAGE_DOC_LENGTH)) + tf
           
            doc_scores[doc] += (idf * (top_term/bottom_term))

    print str(len(doc_scores)) + " results:"
    for doc in sorted(doc_scores, key=doc_scores.get, reverse=True):
        print mappedURL[str(doc)] + " (Score: " + str(doc_scores[doc]) + ")"
    print "\n"


def displayWelcomePrompt():
    print "\n==================================================="
    print "Welcome to Tim's Reuters Search Engine"
    print "===================================================\n"
    print "\n==================================================="
    print "Queries are ANDed by default. To use OR queries,"
    print "put terms in parenthesis, for example:"
    print "'(one two) (three four)' will search for:"
    print "'(one OR two) AND (three OR four)'"
    print "\n"
    print "Note: nested queries are not supported, for example:"
    print "(one (two three)) ((four five) six)"
    print "===================================================\n\n"

def checkIfIndex():
    if 'index.dat' not in os.listdir(os.getcwd()):
        print "No index found. Creating one, please wait."
        spimi.main()
        print "Index successfully created."
        print "==================================================="

def loadIndexToMemory():
    disk_index = open('index.dat', 'r')
    memory_index = {}
    for line in disk_index:
        term = line.split()[0]
        docFreqs = "".join(line.split()[1:]).translate(None, "[](){}'").replace(":",",").split(",")
        memory_index[term] = {}
        doc = 0 
        while doc < len(docFreqs)-1:
            try: # docIDs
                memory_index[term][int(docFreqs[doc])] = int(docFreqs[doc+1])
            except: # sentiment 
                 memory_index[term][str(docFreqs[doc])] = int(docFreqs[doc+1])
            doc += 2 
    return memory_index

def preprocessQuery(query):
    query = nltk.word_tokenize(query)

    # Remove numbers
    query_no_numbers = []
    for term in query:
        try:
            float(query)
        except:
            query_no_numbers.append(term)

    # Case Folding
    query_lowercase = []
    for term in query_no_numbers:
        query_lowercase.append(term.lower())

    processed_query = query_lowercase

    return processed_query

def addToResults(results, terms):
    if results == []:
        results = set(results) | set(terms)
    else:
        results = set(results) & set(terms)
    if "sentiment" in results:
        results.remove("sentiment")
    return results

def orderByNumberOfMatchingTerms(terms, matching_docs, index):
    term_count = {}
    for doc in matching_docs:
        term_count[doc] = 0

        for term in terms:
            if str(doc) in index[term]:
                term_count[doc] += 1

    doc_term_count_sorted = sorted(term_count.items(), key=lambda x: x[1], reverse=True)

    sorted_matching_docs = []
    for doc in doc_term_count_sorted:
        # Uncomment this to see that OR documents are indeed ordered by nubmer of terms present
        # if doc[1] > 1:
        #     print doc 
        sorted_matching_docs.append(doc[0])

    return sorted_matching_docs

def loadDocLengthsToMemory():
    docs = {}
    with open('doc_lengths.txt', 'r') as doc_file:
        for line in doc_file:
            doc_lengths = line.split(" ")
            docs[int(doc_lengths[0])] = int(doc_lengths[1])
    return docs 

def searchForDocuments(index,doc_sentiment):
    doc_lengths = loadDocLengthsToMemory()
    while(True):
        flag = True
        query = raw_input("Please input 0 or 1, 0 represents results are sorted according to TF-IDF, 1 represents results are sorted according to sentiment values\n")
        if int(query) == 1:
            flag = False
        query =  raw_input("ENTER QUERY OR TYPE 'EXIT' TO QUIT: ")

        if query == "EXIT":
            break
            
        processed_query = preprocessQuery(query)

        # calculate the sentiment values of query
        if not flag:
            query_sentiment_value = 0
            if not flag:
                for query_term in processed_query:
                   for key in index.keys():
                       if query_term == key:
                           query_sentiment_value += index.get(key).get("sentiment")
                           break


        # Get matching docIDs
        matching_docs = []
        or_subquery = False 
        or_postings = []
        or_query = False
        or_terms = []

        for term in processed_query:
            if term == "(": 
                or_subquery = True
                or_query = True
            elif term == ")": # Close and merge OR subquery
                or_subquery = False
                matching_docs = addToResults(matching_docs, or_postings)
                or_postings = []
            elif term not in index:
                continue
            elif or_subquery: # Process interior of OR subquery
                or_postings = set(or_postings) | set(index[term])
                or_terms.append(term)
            else: # Process AND query
                matching_docs = addToResults(matching_docs, index[term])
        
        matching_docs = sorted(map(int,matching_docs))

        if or_query:
            matching_docs = orderByNumberOfMatchingTerms(or_terms, matching_docs, index)
        
        if matching_docs == []:
            print "No results.\n"
        else:
            if flag:
                BM25(matching_docs, index, processed_query, doc_lengths)
            else:
                sentimentSearch(matching_docs,query_sentiment_value,doc_sentiment)

def main():
    global mappedURL
    displayWelcomePrompt()
    checkIfIndex()
    index = loadIndexToMemory()
    doc_sentiment = loadDocSentiment()
    mappedURL = loadMapping()
    searchForDocuments(index,doc_sentiment)
    print "\n==================================================="
    print "Thank you for using Tim's Reuters Search Engine"
    print "==================================================="

if __name__ == '__main__':
    main()