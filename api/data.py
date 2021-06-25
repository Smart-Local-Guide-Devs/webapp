import celery
import pandas as pd
from .models import App, Genre


class DataForAppSimilarity:

    # DataFrame for whole data
    df = pd.read_csv("./data.csv")

    # SimilarApps DataFrame --- used in WordWeight and SimilarDescriptions
    df_similar_apps = df[["APP_ID", "APP_NAME", "APP_DESCRIPTION"]]

    genres = [
        "Rides",
        "Food",
        "Delivery",
        "Fashion",
        "Weather",
        "Map",
        "Hotel",
        "Business",
        "Medicine",
        "News",
    ]

    @staticmethod
    def get_top_apps():
        top_apps = {}
        for genre in genres:
            top_apps[genre] = (
                df[df.GENRE_ID == genre]
                .sort_values(by="AVG_RATING", axis=0, ascending=False)
                .iloc[:4]["APP_NAME"]
                .tolist()
            )
        return top_apps


DataForAppSimilarity_instance = DataForAppSimilarity()


class DataSimilarByUserORLocation:
    pass
