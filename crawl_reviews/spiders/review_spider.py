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
        # get audience type (Ex: Sinh viên, cặp đôi, hội nhóm,...) if any
        audience_type = response.css('div.audiences::text').get().strip()

        # get extra shop's details
        info_area = response.css('div.new-detail-info-area')
        res_info = response.css('div.microsite-res-info-properties li:not([class])')

        #get title in detail info 
        titles = [info_label.css('div.new-detail-info-label::text').get().strip() for info_label in info_area]
        microsite_info = [micro_info.css('a::text').get().strip() for micro_info in res_info]

        info = dict()

        for i in range(len(titles)):
            span_tag_info = info_area[i].css('span:not([class])::text').get()
            a_tag_info = info_area[i].css('a[href]::text').getall()
            
            if len(a_tag_info) == 0:
                info[titles[i]] = span_tag_info.strip()
            else:
                info[titles[i]] = ','.join(a_tag_info)
                info[titles[i]] = info[titles[i]].strip()

        info['Extra Info'] = ','.join(microsite_info)
        #yield info

        # get score
        scores = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "micro-home-static", " " ))]//b/text()').extract()
        score_by_standards = {"Vị trí": float(scores[0]), 
                              "Giá cả": float(scores[1]), 
                              "Chất lượng": float(scores[2]), 
                              "Phục vụ": float(scores[3]), 
                              "Không gian": float(scores[4])}
        
        # get type of comment (excellent, good, average, bad?)
        comment_clf = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "rating-levels", " " ))]//b/text()').extract() 
        comment_types = {"Excellent": int(comment_clf[0].strip()), 
                        "Good": int(comment_clf[1].strip()), 
                        "Average": int(comment_clf[2].strip()), 
                        "Bad": int(comment_clf[3].strip())}
        
        # get fb views
        n_views_fb = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "total-views", " " ))]//span/text()').get()

        # get user's info
        all_users = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "review-item", " " ))]').getall()
        for user in all_users: # 10 user/pass
            user_selector = Selector(text=user)

            # get username
            username = user_selector.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "ru-username", " " ))]').get()
            try:
                clean_username = Selector(text=username).xpath('//span/text()').getall()[1]
            except: # no more reviews 
                break 

            # get comment date
            date = user_selector.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "ru-time", " " ))]').get()
            clean_date = Selector(text=date).xpath('//span/text()').get()

            # get comment's title
            clean_title = user_selector.css('a.rd-title span::text').get()

            # get comment
            clean_comment = user_selector.css('div.rd-des span::text').get()

            # get user's 5 score

        yield scores