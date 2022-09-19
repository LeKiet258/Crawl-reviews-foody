import scrapy
from scrapy.selector import Selector

class ReviewSpider(scrapy.Spider):
    name = "review_spider"
    allowed_domains = ['www.foody.vn']
    # robots.txt = False
    start_urls = [
        'https://www.foody.vn/ho-chi-minh/steak-zone/binh-luan'
    ]

    def parse(self, response):
        # get score
        scores = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "micro-home-static", " " ))]//b/text()').extract()
        score_by_standards = {"Vị trí": float(scores[0]), 
                              "Giá cả": float(scores[1]), 
                              "Chất lượng": float(scores[2]), 
                              "Phục vụ": float(scores[3]), 
                              "Không gian": float(scores[4])}
        
        # get type of comment (excellent, good, average, bad?)
        comment_clf = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "rating-levels", " " ))]//b/text()').extract() 
        comment_type = {"Excellent": int(comment_clf[0].strip()), 
                        "Good": int(comment_clf[1].strip()), 
                        "Average": int(comment_clf[2].strip()), 
                        "Bad": int(comment_clf[3].strip())}
        
        # get user's info
        all_users = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "review-item", " " ))]').getall()
        for user in all_users: # 10 user/pass
            user_selector = Selector(text=user)

            # get username
            username = user_selector.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "ru-username", " " ))]').get()
            clean_username = Selector(text=username).xpath('//span/text()').getall()[1]

            # get comment date
            date = user_selector.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "ru-time", " " ))]').get()
            clean_date = Selector(text=date).xpath('//span/text()').get()

            # get title
            //*[contains(concat( " ", @class, " " ), concat( " ", "ng-binding", " " )) and contains(concat( " ", @class, " " ), concat( " ", "ng-scope", " " ))]

            # get comment

        print(comment_type)
        yield scores