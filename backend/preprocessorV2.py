import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from nltk.tag import CRFTagger
from gensim.models import Phrases

def clean_data(data):
    clean_data = []
    pattern = re.compile(r'[^a-zA-Z\s]')
    for sentence in data:
        sentence = sentence.lower()
        sentence = pattern.sub(' ', sentence)
        sentence = sentence.replace('\n', ' ')
        clean_data.append(sentence)
    return clean_data

def tokenizer(data):
    return [word_tokenize(sentence) for sentence in data]

def remove_stop_words(data):
    listStopWords = set(stopwords.words('indonesian') + ['yg'])
    return [[t for t in review if t not in listStopWords and len(t) > 3] for review in data]

def stem(data):
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()
    return [[stemmer.stem(t) for t in review] for review in data]

def categorize(data):
    ct = CRFTagger()
    ct.set_model_file('data\indo_man_tag_corpus_model.crf.tagger')
    filters = ['NN', 'NNP', 'NNS', 'NNPS', 'JJ']
    return [[posTag[0] for posTag in ct.tag_sents(data)[i] if posTag[1] in filters and len(posTag[0]) > 3] for i in range(len(data))]

def bigram(data):
    bigram_t = Phrases(data, min_count=4)
    for idx, d in enumerate(data):
        data[idx] = bigram_t[d]
    return data
