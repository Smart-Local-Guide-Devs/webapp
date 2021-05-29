import celery
from pandas.core.frame import DataFrame

@periodic_task(run_every=(crontab(day='*/1')), name="update_dataframes", ignore_result=True)
def update_dataframes():
    pass 

