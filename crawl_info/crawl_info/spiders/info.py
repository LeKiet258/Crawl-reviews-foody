import json
import re
import scrapy
import urllib
import pandas as pd


file = pd.read_csv("data_merge.csv")
file['Url'] = file['ReviewUrl'].apply(lambda x:  urllib.parse.urljoin('https://www.foody.vn',x))

class ReviewSpider(scrapy.Spider):
    name = 'info'
    allowed_domains = ['www.foody.vn', 'gappapi.deliverynow.vn']

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.start_urls = file['Url'].values
        self.headers = {'x-foody-api-version': '1',
                        'x-foody-app-type': '1004',
                        'x-foody-client-language': 'vi',
                        'x-foody-client-type': '1',
                        'x-foody-client-version': '1',
                        'X-Foody-Client-Id': 'cookies.__ondemand_sessionid'}


    def start_requests(self):
        for i in range(len(self.start_urls)):
            yield scrapy.Request(self.start_urls[i], callback = self.parse_review_page)

    def parse_review_page(self, response):
        active = response.css('div.microsite-point-avg span::text').get()
        url = response.css('a[data-item-type=home]').xpath('@href').get()
        info_area = response.css('div.new-detail-info-area')   
        titles = [info_label.css('div.new-detail-info-label::text').get().strip() for info_label in info_area]
        initdata = response.css('div.micro-left-content script::text').getall()[2]
        ratings_info = response.css('div.ratings-boxes div b::text').getall()
        rating_txt = ['TotalReviews', 'nExcellentReviews', 'nGoodReviews', 'nAverageReviews', 'nBadReviews', 
                      'LocationScore', 'PriceScore', 'QualityScore', 'ServingScore', 'SpaceScore', 'AvgScore']
        res_info = response.css('div.microsite-res-info-properties li:not([class])')
        microsite_info = [micro_info.css('a::text').get().strip() for micro_info in res_info]
        opentime = response.css('div.micro-timesopen > span:nth-child(3)::text').get()

        if response.css("img.pic-place ::attr(src)").get() is not None:
            picplace = response.css("img.pic-place ::attr(src)").get()

        elif response.css("img[itemprop=image] ::attr(src)").get() is not None:
            picplace = response.css("img[itemprop=image] ::attr(src)").get()
        else :
            picplace = "https://t3.ftcdn.net/jpg/04/34/72/82/360_F_434728286_OWQQvAFoXZLdGHlObozsolNeuSxhpr84.jpg"

        if opentime is not None:
            opentime = opentime.strip()

        data = re.search(r'var initData = (\{.*?\});', initdata).group(1)
        datajson = json.loads(data)
        
        info = {'Thời gian chuẩn bị': '', 'Sức chứa': '', 'Giờ nhận khách cuối': ''}


        info['ReviewUrl'] = url
        info['OpenTime'] = opentime
        info['Pic-place'] = picplace


        for i in range(len(rating_txt)):
            info[rating_txt[i]] = ''
        
        for i in range(len(ratings_info)):
            info[rating_txt[i]] = ratings_info[i].strip()

        info['RestaurentId'] = datajson['RestaurantID']
        info['TotalSaves'] = datajson['TotalLists']
        info['Name'] = datajson['Name']
        info['Address'] = datajson['Address']
        info['District'] = datajson['District']
        info['City'] = datajson['City']
        info['RestaurantStatus'] = datajson['RestaurantStatus']
        info['Latitude'] = datajson['Latitude']
        info['Longitude'] = datajson['Longtitude']
        info['TotalPictures'] = datajson['TotalPictures']
        info['TotalViews'] =  datajson['TotalView']
        info['TotalFavourites'] = datajson['TotalFavourite']
        info['TotalCheckedIns'] =  datajson['TotalCheckedIn']
        info['IsBooking'] = datajson['IsBooking']
        info['IsDelivery'] = datajson['IsDeliveryNow']


        for i in range(len(titles)):
            if titles[i] in ['Thời gian chuẩn bị', 'Sức chứa', 'Giờ nhận khách cuối']:
                span_tag_info = info_area[i].css('span:not([class])::text').get()
                div_tag_info = info_area[i].css('div:not([class])::text').get()
                info[titles[i]] +=  div_tag_info if span_tag_info is None else span_tag_info
                info[titles[i]] = info[titles[i]].strip()

        info['ExtraInfo'] = ', '.join(microsite_info) if microsite_info else ''
        info['Active'] = 'False' if active == '_._' else 'True'

        yield scrapy.Request(f"https://gappapi.deliverynow.vn/api/delivery/get_detail?request_id={info['RestaurentId']}&id_type=1", 
        headers = self.headers, meta = {'info': info}, callback = self.parse_detail)
    
    def parse_detail(self, response):
        jsonresponse = json.loads(response.body)
        info = response.meta['info']

        if jsonresponse['result'] == 'success':
            info['categories'] = jsonresponse['reply']['delivery_detail']['categories']
            info['cuisines'] = jsonresponse['reply']['delivery_detail']['cuisines']
            info['service_fee'] = jsonresponse['reply']['delivery_detail']['delivery']['service_fee']['value']
            info['avg_price'] = jsonresponse['reply']['delivery_detail']['delivery']['avg_price']['value']
            info['min_order_value'] = jsonresponse['reply']['delivery_detail']['delivery']['min_order_value']['value']
            info['min_charge'] = jsonresponse['reply']['delivery_detail']['delivery']['min_charge']
            info['minimun_shiping_fee'] = jsonresponse['reply']['delivery_detail']['delivery']['shipping_fee']['minimum_fee']
            info['min_price'] = jsonresponse['reply']['delivery_detail']['price_range']['min_price']
            info['max_price'] = jsonresponse['reply']['delivery_detail']['price_range']['max_price']
            info['promotions'] = jsonresponse['reply']['delivery_detail']['delivery']['promotions']
            yield info