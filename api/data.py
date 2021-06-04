import celery
import pandas as pd
from .models.py import App, Genre

@periodic_task(run_every=(crontab(day='*/1')), name="update_dataframes", ignore_result=True)
def update_dataframes():
    pass 

class VeryBigData:

    df_similar_apps =  pd.DataFrame(
        {
            "APP_ID":[App.app_id],
            "APP_NAME":[App.app_name],
            "APP_DESCRIPTION":[App.app_summary]
        })

    top_apps = 