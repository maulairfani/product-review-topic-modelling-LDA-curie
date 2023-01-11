from gensim import corpora
from gensim.models import LdaModel

def get_topic(lda):
    topic = ''
    for i in range(10):
        key = lda.show_topic(0, 15)[i][0]
        topic += key + ' '
    return topic.strip()

def fit_lda(data):
    # membuat object dictionary
    dictionary = corpora.Dictionary(data)

    # memuat data ke dalam object corpus
    corpus = [dictionary.doc2bow(text) for text in data]

    # membuat object LDA
    lda = LdaModel(corpus=corpus, id2word=dictionary, num_topics=1)

    topic = get_topic(lda)

    return lda, topic