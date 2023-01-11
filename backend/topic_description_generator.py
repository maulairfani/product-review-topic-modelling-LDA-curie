import openai

def generate_text(nama_produk, topic, key='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'):
    openai.api_key = key

    prompt = f"""nama produk : {nama_produk}
    topik : {topic}

    buatkan 1 paragraf yang menggambarkan produk tersebut berdasarkan hasil topik dari model LDA. Topik tersebut dihasilkan dari analisis review-review yang diberikan oleh pelanggan di sebuah marketplace. Anggap bahwa yang membaca paragraf ini adalah orang awam, dan berikan informasi yang relevan dan sesuai dengan topik tersebut. Tulislah dengan gaya yang kreatif dan mudah dipahami. 
    """
    completions = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=500,
        n=1,
        stop=None,
        temperature=0,
    )
    return completions