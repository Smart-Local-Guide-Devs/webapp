import re

from pandas.core.frame import DataFrame
from sklearn.metrics.pairwise import cosine_similarity
import operator
import pandas as pd
import numpy as np
from nltk.corpus import stopwords
import nltk

# nltk.download('stopwords')
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import euclidean_distances


class WordWeight:

    genre_keywords = {
        "Rides": [
            "cab",
            "taxi",
            "ride|rides|riding",
            "car",
            "trip",
            "vehicle",
            "travel",
        ],
        "Food": ["food", "meal|meals", "grocery", "shopping", "eat", "restraunt"],
        "Delivery": ["delivery", "order", "door|doorstep", "fast|quick"],
        "Fashion": [
            "fashion",
            "clothes|clothing",
            "shopping",
            "fashion",
            "trends",
            "lifestyle",
            "products",
            "popular",
            "brands",
            "deals",
        ],
        "Weather": ["weather", "temperature", "humidity"],
        "Map": ["map|maps", "navigation", "gps", "compass", "find"],
        "Hotel": ["hotel", "booking", "stay", "room|rooms", "cheap|luxurious"],
        "Business": [
            "business",
            "entrepreneurs",
            "professional",
            "earn",
            "money",
            "jobs",
            "finance",
        ],
        "Medicine": [
            "medicine",
            "health|healthcare",
            "hospital|hospitals",
            "ambulance",
        ],
        "News": ["news", "information", "latest", "headline"],
    }

    genre_weights = {
        "Rides": {
            "cab": 10,
            "taxi": 7,
            "ride|rides|riding": 9,
            "car": 4,
            "trip": 3,
            "vehicle": 5,
            "travel": 4,
        },
        "Food": {
            "food": 7,
            "meal|meals": 9,
            "grocery": 6,
            "shopping": 5,
            "eat": 6,
            "restraunt": 8,
        },
        "Delivery": {"delivery": 9, "order": 8, "door|doorstep": 4, "fast|quick": 6},
        "Fashion": {
            "fashion": 10,
            "clothes|clothing": 8,
            "shopping": 9,
            "fashion": 9,
            "trends": 6,
            "lifestyle": 5,
            "products": 5,
            "popular": 7,
            "brands": 8,
            "deals": 6,
        },
        "Weather": {"weather": 10, "temperature": 9, "humidity": 8},
        "Map": {
            "map|maps": 8,
            "explore": 6,
            "navigation": 9,
            "gps": 7,
            "compass": 10,
            "find": 6,
        },
        "Hotel": {
            "hotel": 10,
            "booking": 7,
            "stay": 5,
            "room|rooms": 6,
            "cheap|luxurious": 3,
        },
        "Business": {
            "business": 9,
            "entrepreneurs": 6,
            "professional": 7,
            "earn": 3,
            "money": 2,
            "jobs": 7,
            "finance": 6,
        },
        "Medicine": {
            "medicine": 8,
            "health|healthcare": 10,
            "hospital|hospitals": 7,
            "ambulance": 4,
        },
        "News": {"news": 6, "information": 7, "latest": 3, "headline": 4},
    }

    genre_queries = {
        "Fashion": [
            "How good is the refund process?",
            "How is the quality of products on the app?",
            "How good are the prices on the app?",
        ],
        "News": [
            "How useful was the information provided?",
            "How accurate is the customized experience?",
            "How frequently does the app update with recent events and happenings?",
        ],
        "Map": [
            "How good is the user experience of the service?",
            "How much information is provided about the locations?",
            "Accuracy of location detection?",
        ],
        "Rides": [
            "How accurate was the estimated time as said by the app?",
            "How would you rate the travel prices on the app?",
            "How good was the travel experience?",
        ],
        "Food": [
            "How would you rate the food quality?",
            "How good is the variety of products?",
            "How would you rate the food prices on the app?",
        ],
        "Delivery": [
            "How good is the cancelation process?",
            "How good was the condition of the package on arrival?",
            "How good was the estimated delivery time?",
        ],
        "Hotel": [
            "How would you rate the service by hotel staff?",
            "How good was hygiene in and around the place?",
            "How would you rate the staying charges on the app?",
        ],
        "Business": [
            "How good was the user interface of the app?",
            "How frequently was the app updated with new information?",
            "How much is the reliability of the service?",
        ],
        "Medicine": [
            "How much has the app affected your concern over your healthcare routine?",
            "How authentic are the services provided?",
            "How good is the variety of medical supplies?",
        ],
    }

    MAN_KEYWORDS = {
        "rides": ["ride|rides|riding"],
        "food": ["food"],
        "delivery": ["order"],
        "fashion": ["fashion", "clothes|clothing"],
        "weather": ["temperature"],
        "map": ["map|maps"],
        "hotel": ["hotel"],
        "business": ["business"],
        "medicine": ["health|healthcare"],
        "news": ["news"],
    }

    @staticmethod
    def score(genre: str, keywords_count: dict[str, int]) -> float:
        score = 0
        for word, word_count in keywords_count.items():
            score += (
                word_count * WordWeight.genre_weights[genre][word] / len(keywords_count)
            )
        return score

    @staticmethod
    def is_man_word_present(keywords_count: dict[str, int], genre: str) -> bool:
        mandatory_keywords = WordWeight.MAN_KEYWORDS[genre]  # mandatory keywords list
        for mandatory_keyword in mandatory_keywords:
            if mandatory_keyword not in keywords_count.keys():  # make regex check here
                return False
        return True

    @staticmethod
    def keyword_match(
        keywords_count_1: dict[str, int], keywords_count_2: dict[str, int]
    ):
        confidence_index = 0
        n_req_threshold = (
            4  # lower the value : closer to word count in original description
        )
        req_confidence = 0.5  # higher the value : closer to original description

        for keyword in keywords_count_1:
            if keywords_count_1[keyword] in range(
                keywords_count_2[keyword] - n_req_threshold,
                keywords_count_2[keyword] + n_req_threshold + 1,
            ):
                confidence_index += 1
        confidence = confidence_index / len(keywords_count_1)
        if confidence > req_confidence:
            return True
        return False

    @staticmethod
    def compare_apps(app_desc1: str, app_desc2: str) -> None:
        SIM_THRSHLD = 0.3

        for genre, keywords in WordWeight.genre_keywords.items():
            keywords_count_1 = {}
            keywords_count_2 = {}
            for keyword in keywords:
                keyword_count = len(re.findall(keyword, app_desc1, re.IGNORECASE))
                if keyword_count > 1:
                    keywords_count_1[keyword] = keyword_count
                keyword_count = len(re.findall(keyword, app_desc2, re.IGNORECASE))
                if keyword_count > 1:
                    keywords_count_2[keyword] = keyword_count
            score1 = WordWeight.score(genre, keywords_count_1)
            score2 = WordWeight.score(genre, keywords_count_2)

            print(score1, "----", score2)
            if (
                abs(score1 - score2) / max(score1, score2, 1) > SIM_THRSHLD
            ):  # relative difference kept below a threshold
                print("Apps are dis-similar on genre " + genre)
            else:
                print("Apps are similar on genre " + genre)

    @staticmethod
    def similar_apps(app_desc: str, data: DataFrame) -> list:
        apps = []
        app_genres = WordWeight.get_app_genres(app_desc)
        for app_genre in app_genres:
            word_count = {}
            keywords = WordWeight.genre_keywords[app_genre]
            for keyword in keywords:
                word_count[keyword] = len(re.findall(keyword, app_desc, re.IGNORECASE))

            REQ_KEY_C = 2  # minimum number of keywords that match and are required in the apps being searched
            for _, row in data.iterrows():
                app_desc = str(row["APP_DESCRIPTION"])
                keywords_count = {}
                for keyword in keywords:
                    keyword_count = len(re.findall(keyword, app_desc, re.IGNORECASE))
                    if keyword_count > 1:
                        keywords_count[keyword] = keyword_count

                if (
                    WordWeight.is_man_word_present(keywords_count, app_genre)
                    and len(keywords_count) >= REQ_KEY_C
                    and WordWeight.keyword_match(keywords_count, word_count)
                ):  # if more than n_req_keywords similar keywords are present in description && confidence greater than some threshold
                    apps.append(
                        (row["APP_ID"], WordWeight.score(app_genre, keywords_count))
                    )
        apps.sort(key=lambda x: x[1], reverse=True)
        return apps

    @staticmethod
    def get_app_genres(app_desc: str) -> list[str]:
        genres = []
        GENRE_THRSHLD = 0
        for genre, keywords in WordWeight.genre_keywords.items():
            keywords_count = {}

            for keyword in keywords:
                keyword_count = len(re.findall(keyword, app_desc, re.IGNORECASE))
                if keyword_count > 1:
                    keywords_count[keyword] = keyword_count
            score = WordWeight.score(genre, keywords_count)
            if score > GENRE_THRSHLD:
                genres.append(genre)

        return genres

    @staticmethod
    def recommend_item(user_name, similar_user_names, matrix, items=3):

        similar_users = matrix[matrix.index.isin(similar_user_names)]
        similar_users = similar_users.mean(axis=0)
        similar_users_df = pd.DataFrame(similar_users, columns=["mean"])
        user_df = matrix[matrix.index == user_name]
        user_df_transposed = user_df.transpose()
        user_df_transposed.columns = ["rating"]
        user_df_transposed = user_df_transposed[user_df_transposed["rating"] == 0]
        apps_unused = user_df_transposed.index.tolist()
        similar_users_df_filtered = similar_users_df[
            similar_users_df.index.isin(apps_unused)
        ]
        similar_users_df_ordered = similar_users_df.sort_values(
            by=["mean"], ascending=False
        )
        top_n_apps = similar_users_df_ordered.head(items)
        top_n_apps_names = top_n_apps.index.tolist()

        return top_n_apps_names

    @staticmethod
    def similar_users(user_name, matrix, k=3):
        user = matrix[matrix.index == user_name]
        other_users = matrix[matrix.index != user_name]
        similarities = cosine_similarity(user, other_users)[0].tolist()
        userlist = other_users.index.tolist()
        index_similarity = dict(zip(userlist, similarities))
        similarity_sorted = sorted(index_similarity.items(), key=operator.itemgetter(1))
        similarity_sorted.reverse()
        top_users_similarities = similarity_sorted[:k]
        users = [u[0] for u in top_users_similarities]

        return users

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
