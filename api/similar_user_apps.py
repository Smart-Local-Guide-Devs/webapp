from sklearn.metrics.pairwise import cosine_similarity
import operator
from pandas.core.frame import DataFrame 

class SimilarUserApps:

    @staticmethod
    def create_matrix(reviews: DataFrame, criteria: str) -> DataFrame:
        matrix=reviews.pivot_table(index='USER_NAME', columns='APP_ID', values=criteria)
        matrix=matrix.fillna(0)

        return matrix

    @staticmethod
    def similar_users(user_name: str, matrix: DataFrame, k=3) -> list:

        # create a df of just the current user
        user = matrix[matrix.index == user_name]
        
        # # and a df of all other users
        other_users = matrix[matrix.index != user_name]

        # calc cosine similarity between user and each other user
        
        similarities = cosine_similarity(user,other_users)[0].tolist()
    
        # create list  of these users
        userlist = other_users.index.tolist()
        
        # create key/values pairs of user  and their similarity
        index_similarity = dict(zip(userlist, similarities))
        
        # sort by similarity
        similarity_sorted = sorted(index_similarity.items(), key=operator.itemgetter(1))
        similarity_sorted.reverse()
        
        # grab k users off the top
        top_users_similarities = similarity_sorted[:k]
        users = [u[0] for u in top_users_similarities]
        
        return users

    @staticmethod
    def recommend_item(user_name : str, reviews: DataFrame, criteria: str, items=3) -> list:
        
        matrix = SimilarUserApps.create_matrix(reviews, criteria)

        similar_user_names = SimilarUserApps.similar_users(user_name, matrix)
        # load vectors for similar users
        similar_users = matrix[matrix.index.isin(similar_user_names)]
        # calc avg ratings across the 3 similar users
        similar_users = similar_users.mean(axis=0)
        # convert to dataframe so its easy to sort and filter
        similar_users_df = pd.DataFrame(similar_users, columns=['mean'])
        
        # load vector for the current user
        user_df = matrix[matrix.index == user_name]
        # transpose it so its easier to filter
        user_df_transposed = user_df.transpose()
        # rename the column as 'rating'
        user_df_transposed.columns = ['rating']
        # remove any rows without a 0 value. 
        user_df_transposed = user_df_transposed[user_df_transposed['rating']==0]
        # generate a list of apps the user has not used
        apps_unused = user_df_transposed.index.tolist()
        
        # filter avg ratings of similar users for only apps the current user has not used
        similar_users_df_filtered = similar_users_df[similar_users_df.index.isin(apps_unused)]
        # order the dataframe
        similar_users_df_ordered = similar_users_df.sort_values(by=['mean'], ascending=False)
        # grab the top n apps  
        top_n_apps = similar_users_df_ordered.head(items)
        top_n_apps_names = top_n_apps.index.tolist()
    
        return top_n_apps_names