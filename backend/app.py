from flask import Flask, jsonify, request 
from flask_cors import CORS
from scraperV2 import getReview
from preprocessorV2 import clean_data, tokenizer, remove_stop_words, stem, categorize, bigram
from topic_modelling_LDA import fit_lda
from topic_description_generator import generate_text

app = Flask(__name__)
CORS(app)

@app.route('/scrape', methods=['POST', 'GET'])
def scrape_():
    r = request.get_json()
    url = r['url']
    starRating = r['starRating']

    data = getReview(url, starRating)

    return jsonify(data)

@app.route('/clean_data', methods=['POST', 'GET'])
def clean_data_():
    r = request.get_json()
    data = r['data']

    preprocessed = clean_data(data)

    return jsonify({'data': preprocessed, 'status': 'success', 'produk' : r['produk']})

@app.route('/tokenizer', methods=['POST', 'GET'])
def tokenizer_():
    r = request.get_json()
    data = r['data']

    preprocessed = tokenizer(data)

    return jsonify({'data': preprocessed, 'status': 'success', 'produk' : r['produk']})

@app.route('/remove_stop_words', methods=['POST', 'GET'])
def remove_stop_words_():
    r = request.get_json()
    data = r['data']

    preprocessed = remove_stop_words(data)

    return jsonify({'data': preprocessed, 'status': 'success', 'produk' : r['produk']})

@app.route('/stem', methods=['POST', 'GET'])
def stem_():
    r = request.get_json()
    data = r['data']

    preprocessed = stem(data)

    return jsonify({'data': preprocessed, 'status': 'success', 'produk' : r['produk']})

@app.route('/categorize', methods=['POST', 'GET'])
def categorize_():
    r = request.get_json()
    data = r['data']

    preprocessed = categorize(data)

    return jsonify({'data': preprocessed, 'status': 'success', 'produk' : r['produk']})

@app.route('/bigram', methods=['POST', 'GET'])
def bigram_():
    r = request.get_json()
    data = r['data']

    preprocessed = bigram(data)

    return jsonify({'data': preprocessed, 'status': 'success', 'produk' : r['produk']})

@app.route('/create_model', methods=['POST', 'GET'])
def create_model_():
    r = request.get_json()
    data = r['data']
    lda, topic = fit_lda(data)

    return jsonify({'topic' : topic, 'status': 'success', 'produk' : r['produk']})

@app.route('/desc', methods=['POST', 'GET'])
def desc_():
    r = request.get_json()
    nama_produk = r['produk']
    topic = r['topic']
    api_key = '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'

    try:
        completion = generate_text(nama_produk, topic, api_key)
        text = completion['choices'][0]["text"][1:]
    except:
        return jsonify({r})

    return jsonify({'completion' : completion, 'text' : text})


if __name__ == '__main__':
    app.run()
