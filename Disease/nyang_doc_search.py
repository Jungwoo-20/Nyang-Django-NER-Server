from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import numpy as np
import tensorflow_hub as hub
from board import views
import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_text
import os
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
secret_file = os.path.join(BASE_DIR, 'secrets.json')

with open(secret_file) as f:
    secrets = json.loads(f.read())
##### SEARCHING #####
index_name = "pet_disease"
client = Elasticsearch(secrets['DJANGO_ELASTICSEARCH_ADDRESS'], timeout=30, max_retries=10, retry_on_timeout=True)
print('elasticsearch load complete')
# sentence model load
model_url = "https://tfhub.dev/google/universal-sentence-encoder-multilingual/3"
embed = hub.load(model_url)
print('sentence model load complete')


def document_search(input_query):
    query_vector = embed([input_query])[0]
    input_query_vector = np.array(query_vector)
    script_query = {
        "script_score": {
            "query": {"match_all": {}},
            "script": {
                "source": "cosineSimilarity(params.query_vector, doc['title_vector']) + 1.0",
                "params": {"query_vector": input_query_vector}
            }
        }
    }
    response = client.search(
        index=index_name,
        body={
            "size": 3,
            "query": script_query,
            "_source": {"includes": ["title", "question", "answer", "answer_ner", "sentence_info", "url"]}
        }
    )
    result_list = []
    i = 1
    for hit in response["hits"]["hits"]:
        result = {
            "no": i,
            "title": hit["_source"]["title"],
            "question": hit["_source"]["question"],
            "answer": hit["_source"]["answer"],
            "answer_ner": hit["_source"]["answer_ner"],
            "url": hit["_source"]["url"],
            "sentence_info": hit["_source"]["sentence_info"]
        }
        i += 1
        result_list.append(result)
    return result_list
