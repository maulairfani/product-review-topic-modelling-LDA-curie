import time
import re
import requests
import warnings
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from urllib.parse import urlparse, urlunparse
warnings.filterwarnings("ignore", category=FutureWarning)
from selenium.webdriver.chrome.options import Options


def scrape_tokped_reviews(url):
    start = time.time()
    def getComments(productID, totalReviews):
        url_2 = 'https://gql.tokopedia.com/graphql/productReviewList'
        payload = [{"operationName":"productReviewList","variables":{"productID":"","page":1,"limit":"","sortBy":"create_time desc","filterBy":""},"query":"query productReviewList($productID: String!, $page: Int!, $limit: Int!, $sortBy: String, $filterBy: String) {\n  productrevGetProductReviewList(productID: $productID, page: $page, limit: $limit, sortBy: $sortBy, filterBy: $filterBy) {\n    productID\n    list {\n      id: feedbackID\n      variantName\n      message\n      productRating\n      reviewCreateTime\n      reviewCreateTimestamp\n      isReportable\n      isAnonymous\n      imageAttachments {\n        attachmentID\n        imageThumbnailUrl\n        imageUrl\n        __typename\n      }\n      videoAttachments {\n        attachmentID\n        videoUrl\n        __typename\n      }\n      reviewResponse {\n        message\n        createTime\n        __typename\n      }\n      user {\n        userID\n        fullName\n        image\n        url\n        __typename\n      }\n      likeDislike {\n        totalLike\n        likeStatus\n        __typename\n      }\n      stats {\n        key\n        formatted\n        count\n        __typename\n      }\n      badRatingReasonFmt\n      __typename\n    }\n    shop {\n      shopID\n      name\n      url\n      image\n      __typename\n    }\n    hasNext\n    totalReviews\n    __typename\n  }\n}\n"}]
        payload[0]["variables"]["productID"] = productID
        payload[0]["variables"]["limit"] = totalReviews
        req = requests.post(url_2, json=payload).json()

        return req

    def getTotalReview(productID):
        url_2 = 'https://gql.tokopedia.com/graphql/productReviewList'
        payload = [{"operationName":"productReviewList","variables":{"productID":"","page":1,"limit":10,"sortBy":"create_time desc","filterBy":""},"query":"query productReviewList($productID: String!, $page: Int!, $limit: Int!, $sortBy: String, $filterBy: String) {\n  productrevGetProductReviewList(productID: $productID, page: $page, limit: $limit, sortBy: $sortBy, filterBy: $filterBy) {\n    productID\n    list {\n      id: feedbackID\n      variantName\n      message\n      productRating\n      reviewCreateTime\n      reviewCreateTimestamp\n      isReportable\n      isAnonymous\n      imageAttachments {\n        attachmentID\n        imageThumbnailUrl\n        imageUrl\n        __typename\n      }\n      videoAttachments {\n        attachmentID\n        videoUrl\n        __typename\n      }\n      reviewResponse {\n        message\n        createTime\n        __typename\n      }\n      user {\n        userID\n        fullName\n        image\n        url\n        __typename\n      }\n      likeDislike {\n        totalLike\n        likeStatus\n        __typename\n      }\n      stats {\n        key\n        formatted\n        count\n        __typename\n      }\n      badRatingReasonFmt\n      __typename\n    }\n    shop {\n      shopID\n      name\n      url\n      image\n      __typename\n    }\n    hasNext\n    totalReviews\n    __typename\n  }\n}\n"}]
        payload[0]["variables"]["productID"] = productID
        req = requests.post(url_2, json=payload).json()

        totalReviews = req[0]["data"]["productrevGetProductReviewList"]["totalReviews"]

        return totalReviews

    url_1 = url
    chrome_options = Options()
    WINDOW_SIZE = "1920,1080"
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
    chrome_options.add_argument('--log-level=3')
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
    chrome_options.add_argument(f'user-agent={user_agent}')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url_1)
    driver.implicitly_wait(10)
    curr_url = driver.current_url
    # print(curr_url)

    parsed_url = urlparse(curr_url)
    cleaned_url = urlunparse(parsed_url._replace(query=""))

    if cleaned_url[-7:] != '/review':
        driver.get(cleaned_url + '/review')

    try:
        driver.implicitly_wait(10)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()
        productID = re.search('productID\\\\":\\\\"\d+', str(soup)).group()
        productID = re.search('\d+', productID).group()
        nama_produk = soup.find('title').text
        nama_produk = re.sub('Review Produk - ', '', nama_produk)
        nama_produk = re.sub('| Tokopedia', '', nama_produk)[:-2]
        # print(nama_produk)
        # print('productID:', productID)
    except Exception as e:
        error = e

    for i in range(50):
        try:
            totalReviews = getTotalReview(productID)
            break
        except ConnectionError:
            error = e
        except Exception as e:
            error = e

    for i in range(50):
        try:
            req = getComments(productID, totalReviews)
            rows = req[0]["data"]["productrevGetProductReviewList"]["list"]
            # print('Success', end='\r')
            break
        except ConnectionError as e:
            error = e
        except Exception as e:
            error = e
    data = pd.DataFrame(columns=['review', 'rating'])
    for i in range(len(rows)):
        review = req[0]["data"]["productrevGetProductReviewList"]["list"][i]["message"]
        rating = req[0]["data"]["productrevGetProductReviewList"]["list"][i]["productRating"]
        data.loc[i] = [review, rating]
        progress = int(len(data)/len(rows)*100)
        # print(f'Progress: {progress}%', end='\r')
    data.to_csv('data/data.csv')
    # print('Jumlah data:', len(data))
    # print(f'Lama running: {round(time.time()-start, 1)}s')

    return data, nama_produk

def scrape_shopee_reviews(url):
    url = urlparse(url)
    url = urlunparse(url._replace(query=""))

    # Compile regex pattern:
    pattern = re.compile(r"\d+")

    # Cari product ID dan shop ID:
    ids = pattern.findall(url)
    product_id = int(ids[-1])
    shop_id = int(ids[-2])

    print("Product ID:", product_id)
    print("Shop ID:", shop_id)

    for i in range(50):
        try:
            r = requests.get(f'https://shopee.co.id/api/v2/item/get_ratings?filter=1&flag=1&itemid={product_id}&limit=6&offset=0&shopid={shop_id}&type=0')
            if r.json()['data']['ratings'] != None:
                # print('success', end='\r')
                break
        except:
            pass
    rw_context = r.json()['data']['item_rating_summary']['rcount_with_context']
    product_name = r.json()['data']["ratings"][0]["product_items"][0]["name"]
    print("Nama produk:", product_name)
    print("Total review: ", rw_context)

    data = pd.DataFrame()

    n_iter = rw_context - (rw_context % 6)
    offset = 0
    limit = 54
    while offset <= n_iter:
        for i in range(30):
            try:
                url = f'https://shopee.co.id/api/v2/item/get_ratings?filter=1&flag=1&itemid={product_id}&limit={limit}&offset={offset}&shopid={shop_id}&type=0'
                r = requests.get(url)
                persen = int((offset/limit+1)/int(rw_context/limit+1)*100)
                print(f'Progress: {persen}%', end='\r')
                r_count = len(r.json()['data']['ratings'])
                for i in range(r_count):
                    rev = r.json()['data']['ratings'][i]['comment']
                    rat = r.json()['data']['ratings'][i]['detailed_rating']['product_quality']
                    data = data.append({'review' : rev, 'rating': rat}, ignore_index=True)
                break
            except Exception as e:
                pass
        offset += limit
    data.to_csv('data/data.csv')
    print(f'Data terkumpul: {round(len(data)/rw_context*100, 2)}%')
    return data, product_name

def getReview(Url):
    if 'tokopedia' in Url:
        return scrape_tokped_reviews(Url)
    elif 'shopee' in Url:
        return scrape_shopee_reviews(Url)
    else:
        return {'status' : 'failed', 'data' : None, 'error' : 'Coba periksa URL'}