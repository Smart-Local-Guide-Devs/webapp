from pandas.core.frame import DataFrame

class RecommendByLocation:

    def weighted_rating(x, m=m ,C=C) :
        v = x['R1']+x['R2']+x['R3']+x['R4']+x['R5']+x['R6']+x['R7']*2
        R =( x['R1']+x['R2']+x['R3']+x['R4']+x['R5']+x['R6']+x['R7']*2)/8
        return (v/(v+m) * R) + (m/(m+v) * C)

    @staticmethod
    def apps_by_loc(user_loc: str, data: DataFrame) -> list:
        reviews_loc = data[data.location == user_loc]
        top_res_loc = reviews_loc.sort_values(by=['R7'], ascending=False)

        C = (top_res_loc['R1']+top_res_loc['R2']+top_res_loc['R3']+top_res_loc['R4']+top_res_loc['R5']+top_res_loc['R6']+top_res_loc['R7']*2)/8
        C = C.mean()

        QUANTILE_VAL = 0.80
        m = top_res_loc['R7'].quantile(QUANTILE_VAL)

        app_filt = top_res_loc.copy().loc[data['R7'] >= m]
        app_filt['score'] = app_filt.apply(weighted_rating, axis=1)
        app_filt = app_filt.sort_values('score' , ascending = False)
        app_filt.values.tolist()
        
        return app_filt