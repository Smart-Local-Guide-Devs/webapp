import re

from pandas.core.frame import DataFrame


class WordWeight:

    genre_keywords = {
        "rides": [
            "cab",
            "taxi",
            "ride|rides|riding",
            "car",
            "trip",
            "vehicle",
            "travel",
        ],
        "food": ["food", "meal|meals", "grocery", "shopping", "eat", "restraunt"],
        "delivery": ["delivery", "order", "door|doorstep", "fast|quick"],
        "fashion": [
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
        "weather": ["weather", "temperature", "humidity"],
        "map": ["map|maps", "navigation", "gps", "compass", "find"],
        "hotel": ["hotel", "booking", "stay", "room|rooms", "cheap|luxurious"],
        "business": [
            "business",
            "entrepreneurs",
            "professional",
            "earn",
            "money",
            "jobs",
            "finance",
        ],
        "medicine": [
            "medicine",
            "health|healthcare",
            "hospital|hospitals",
            "ambulance",
        ],
        "news": ["news", "information", "latest", "headline"],
    }

    genre_weights = {
        "rides": {
            "cab": 10,
            "taxi": 7,
            "ride|rides|riding": 9,
            "car": 4,
            "trip": 3,
            "vehicle": 5,
            "travel": 4,
        },
        "food": {
            "food": 7,
            "meal|meals": 9,
            "grocery": 6,
            "shopping": 5,
            "eat": 6,
            "restraunt": 8,
        },
        "delivery": {"delivery": 9, "order": 8, "door|doorstep": 4, "fast|quick": 6},
        "fashion": {
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
        "weather": {"weather": 10, "temperature": 9, "humidity": 8},
        "map": {
            "map|maps": 8,
            "explore": 6,
            "navigation": 9,
            "gps": 7,
            "compass": 10,
            "find": 6,
        },
        "hotel": {
            "hotel": 10,
            "booking": 7,
            "stay": 5,
            "room|rooms": 6,
            "cheap|luxurious": 3,
        },
        "business": {
            "business": 9,
            "entrepreneurs": 6,
            "professional": 7,
            "earn": 3,
            "money": 2,
            "jobs": 7,
            "finance": 6,
        },
        "medicine": {
            "medicine": 8,
            "health|healthcare": 10,
            "hospital|hospitals": 7,
            "ambulance": 4,
        },
        "news": {"news": 6, "information": 7, "latest": 3, "headline": 4},
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
    def similar_apps(app_desc: str, app_genres: str, data: DataFrame) -> list:
        apps = []
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
                        (row["APP_NAME"], WordWeight.score(app_genre, keywords_count))
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
