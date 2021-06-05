from google_play_scraper import app, exceptions, reviews, Sort
import pandas as pd
from pandas.core.frame import DataFrame

def print_progress_bar (iteration: int, total: int, prefix: str) -> None:
    percent = '{0:.2f}'.format(100 * iteration / total)
    filled_length = int(69 * iteration // total)
    bar = '█' * filled_length + ' ' * (69 - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% ', end='')
    if iteration == total: 
        print()

def add_app_info(app_info: dict, app_infos: list) -> None:
	app_infos.append({
		'APP_ID': app_info['appId'],
		'APP_NAME': app_info['title'],
		'PLAY_STORE_LINK': app_info['url'],
		'APP_DESCRIPTION': app_info['description'],
		'APP_SUMMARY': app_info['summary'],
		'GENRE_ID': app_info['genre'],
		'MIN_INSTALLS': app_info['minInstalls'],
		'AVG_RATING': app_info['score'],
		'RATINGS_COUNT': app_info['ratings'],
		'REVIEWS_COUNT': app_info['reviews'],
		'RATINGS_HIST': app_info['histogram'],
		'FREE': app_info['free'],
		'ICON_LINK': app_info['icon'],
		'HEADER_LINK': app_info['headerImage'],
	})

def add_app_review_list(app_id, app_review_list: list, app_reviews: list) -> None:
	for app_review in app_review_list:
		app_reviews.append({
			'APP_ID': app_id,
			'USER_NAME': app_review['userName'],
			'USER_IMG_LINK': app_review['userImage'],
			'CONTENT': app_review['content'],
			'RATING': app_review['score'],
			'UP_VOTE_COUNT': app_review['thumbsUpCount'],
		})

def index_of_user(last_review_user_name: str, app_review_list: list) -> int:
	for i, app_review in enumerate(app_review_list):
		if (app_review['userName'] == last_review_user_name):
			return i
	return -1

def save_files(app_not_responded_count: int, app_infos: list, app_infos_df: pd.DataFrame, app_reviews: list, app_reviews_df: DataFrame) -> None:
	print(f'{app_not_responded_count} apps did not respond')
	print('Saving details to file please wait...', end='')
	app_infos_df.append(app_infos).to_csv('AppDescriptions.csv', index=False)
	app_reviews_df.append(app_reviews).to_csv('AppReviews.csv', index=False)
	print('\rApp descriptions stored in AppDescriptions.csv\nApp reviews stored in AppReviews.csv')

def main(apps_ids_file_name: str) -> None:
	print(f'Reading App Ids from {apps_ids_file_name}', end='')
	app_ids = open(apps_ids_file_name, mode="r").read().strip().split(sep='\n')
	print(f'\rApp Ids read from {apps_ids_file_name}    ')

	try:
		app_infos_df = pd.read_csv('AppDescriptions.csv')
		app_reviews_df = pd.read_csv('AppReviews.csv')
		last_app_id = app_infos_df.tail(1)['APP_ID'].tolist()[0]
		start_app_id_index = app_ids.index(last_app_id) + 1
		last_review_user_name = app_reviews_df.tail(1)['USER_NAME'].tolist()[0]
		last_review_app_id = app_reviews_df.tail(1)['APP_ID'].tolist()[0]
		print(f'Previous files found resuming from {start_app_id_index}')

	except FileNotFoundError:
		app_infos_df = pd.DataFrame(columns=['APP_ID', 'APP_NAME', 'PLAY_STORE_LINK', 'APP_DESCRIPTION', 'APP_SUMMARY', 'GENRE_ID', 'MIN_INSTALLS', 'AVG_RATING', 'RATINGS_COUNT', 'REVIEWS_COUNT', 'RATINGS_HIST', 'FREE', 'ICON_LINK', 'HEADER_LINK'])
		app_reviews_df = pd.DataFrame(columns=['APP_ID', 'USER_NAME', 'USER_IMG_LINK', 'CONTENT', 'RATING', 'UP_VOTE_COUNT'])
		start_app_id_index = 0
		last_review_user_name = ''
		last_review_app_id = ''

	app_ids = app_ids[start_app_id_index:]
	app_ids_count = len(app_ids)
	app_not_responded_count = 0
	app_infos = []
	app_reviews = []

	try:

		for i, app_id in enumerate(app_ids):
			try:
				app_review_list, _ = reviews(app_id, 'en', 'in', Sort.NEWEST, 200)
				if (i == 0 and last_review_app_id == app_id):
					start_review_idx = index_of_user(last_review_user_name, app_review_list) + 1
					app_review_list = app_review_list[start_review_idx:]
				add_app_review_list(app_id, app_review_list, app_reviews)

				app_info = app(app_id, 'en', 'in')
				add_app_info(app_info, app_infos)

			except exceptions.NotFoundError:
				app_not_responded_count += 1
			
			print_progress_bar(i+1, app_ids_count, f'{i + 1} Apps done of {app_ids_count}')

	except KeyboardInterrupt:
		pass

	finally:
		save_files(app_not_responded_count, app_infos, app_infos_df, app_reviews, app_reviews_df)

if __name__ == "__main__":
	apps_ids_file_name = input('Enter the file containing app ids: ').strip()
	main(apps_ids_file_name)