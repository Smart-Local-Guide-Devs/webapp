import celery
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from .data import DataForAppSimilarity, DataForAppSimilarity_instance

# Executes every Monday morning at 7:00 p.m.
@periodic_task(
    run_every=(crontab(hour=19, minute=00, day_of_week=1)),
    name="update_data",
    ignore_result=True,
)
def update_csv():
    pass


# Executes every Monday morning at 7:00 p.m.
@periodic_task(
    run_every=(crontab(hour=19, minute=00, day_of_week=1)),
    name="update_dataframes",
    ignore_result=True,
)
def update_dataframes():
    DataForAppSimilarity_instance = DataForAppSimilarity()
    pass
