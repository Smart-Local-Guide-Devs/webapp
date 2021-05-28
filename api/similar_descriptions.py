import re

from pandas.core.frame import DataFrame
import operator
import pandas as pd
import numpy as np

from nltk.corpus import stopwords
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import euclidean_distances

class SimilarDescriptions:

    genres = ['Rides', 'Food', 'Delivery', 'Fashion', 'Weather', 'Map', 'Hotel', 'Business', 'Medicine', 'News']

    @staticmethod
    def get_top_apps():
        top_apps = {}

        for genre in genres:
            top_apps[genre] = data[data.GENRE_ID==genre].sort_values( by='AVG_RATING',axis=0, ascending=False).iloc[:4]['APP_NAME'].tolist()

        return top_apps


    @staticmethod
    def similar_apps_nltk(app_obj, data: DataFrame):

        matrix = "Cosine Similarity"

        apps = data["APP_NAME"].values.tolist()
        descriptions = data["APP_DESCRIPTION"].values.tolist()
        descriptions_df = pd.DataFrame(descriptions, columns=["Descriptions"])
        descriptions_df["Apps"] = data["APP_NAME"].values.tolist()
        stop_words_l = stopwords.words("english")
        descriptions_df["descriptions_cleaned"] = descriptions_df.Descriptions.apply(
            lambda x: " ".join(
                re.sub(r"[^a-zA-Z]", " ", w).lower()
                for w in x.split()
                if re.sub(r"[^a-zA-Z]", " ", w).lower() not in stop_words_l
            )
        )

        tfidfvectoriser = TfidfVectorizer()
        tfidfvectoriser.fit(descriptions_df.descriptions_cleaned)
        tfidf_vectors = tfidfvectoriser.transform(descriptions_df.descriptions_cleaned)

        pairwise_similarities = np.dot(tfidf_vectors, tfidf_vectors.T).toarray()
        similarity_matrix = pairwise_similarities

        doc_id = data.loc[data["APP_NAME"] == app_obj.APP_NAME].index[0]

        print(f'App: {descriptions_df.iloc[doc_id]["Descriptions"]}')
        print("\n")
        print("Similar Apps:")
        if matrix == "Cosine Similarity":
            similar_ix = np.argsort(similarity_matrix[doc_id])[::-1]

        for ix in similar_ix:
            if ix == doc_id:
                continue
            print("\n")
            print(f'App: {descriptions_df.iloc[ix]["Apps"]}')
            print(f"{matrix} : {similarity_matrix[doc_id][ix]}")
