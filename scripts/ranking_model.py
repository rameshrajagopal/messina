
class RankingModel:
    def __init__(self):
        pass

    def process(self, products):
        search_score  = [1000000000, -100000000]
        ranking_count = -100000000
        sale_price    = [-1000000000, -100000000]
        for product in products:
            sc = product['searchScore']
            rc = product['aggregatedRatings']['ratingCount']
            min_sp = product['priceRange'][0]['salePrice']
            max_sp = product['priceRange'][1]['salePrice']
            #print sc, " ", rc, " ", min_sp, " ", max_sp
            if search_score[0] > sc:
                search_score[0] = sc
            if search_score[1] < sc:
                search_score[1] = sc
            if ranking_count < rc:
                ranking_count = rc
            if sale_price[0] < min_sp:
                sale_price[0] = min_sp
            if sale_price[1] < max_sp:
                sale_price[1] = max_sp
        search_score_normalizer = (1. * 100)/(search_score[1])
        ranking_count_normalizer = (1. * 100)/(ranking_count)
        sale_price_normalizer = (1. * 100)/ (sale_price[0])
        #print search_score_normalizer, " ", ranking_count_normalizer, " ", sale_price_normalizer
        sorted_products = sorted(products,
                key=lambda k: ((k['searchScore'] * search_score_normalizer) * 0.3) +
                ((k['aggregatedRatings']['ratingCount'] * ranking_count_normalizer) * 0.5) +
                ((k['priceRange'][0]['salePrice'] * sale_price_normalizer) * 0.2),
                reverse=True)
        return sorted_products

