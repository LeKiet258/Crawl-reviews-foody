import json
import scrapy
import pandas as pd

file = pd.read_csv('Crawl-reviews-foody/data_merge.csv')

def merge_two_dicts(x, y):
    z = x.copy()   
    z.update(y)
    return z

class ReviewSpider(scrapy.Spider):
    name = 'menu'
    allowed_domains = ['www.foody.vn']

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.start_urls = file['RestaurantId'].values
        self.headers = {'x-foody-api-version': '1',
                        'x-foody-app-type': '1004',
                        'x-foody-client-language': 'vi',
                        'x-foody-client-type': '1',
                        'x-foody-client-version': '1',
                        'X-Foody-Client-Id': 'cookies.__ondemand_sessionid'}

    def start_requests(self):
        for i in range(len(self.start_urls)):
            yield scrapy.Request(f"https://gappapi.deliverynow.vn/api/dish/get_delivery_dishes?id_type=1&request_id={self.start_urls[i]}", 
            headers = self.headers, meta = {'Id': self.start_urls[i]}, callback = self.parse_menu)

    def parse_menu(self, response):
        jsonresponse = json.loads(response.body)

        columns = ['RestaurantId', 'dish_type_id','dish_type_name','dish_id','dish_name','dish_description','dish_price_value','dish_total_like','dish_is_available',
                   'dish_option_id','dish_option_name','option_min_select','option_max_select','item_id','item_name','item_price']

        menu_item = dict.fromkeys(columns, '')
        menu_item['RestaurantId'] = response.meta['Id']

        if jsonresponse['result'] == 'success':
            if not len(jsonresponse['reply']['menu_infos']):
                yield menu_item

            for menu_info in jsonresponse['reply']['menu_infos']:
                if not len(menu_info['dishes']):
                    yield merge_two_dicts(menu_item, {'dish_type_id': menu_info['dish_type_id'], 'dish_type_name': menu_info['dish_type_name']})
                            
                for dish in menu_info['dishes']:
                    if not len(dish['options']):
                        yield merge_two_dicts(menu_item, {'dish_type_id': menu_info['dish_type_id'], 'dish_type_name':  menu_info['dish_type_name'],
                                         'dish_id': dish['id'], 'dish_name':  dish['name'],
                                         'dish_description': dish['description'], 'dish_price_value':  dish['price']['value'],
                                         'dish_total_like': dish['total_like'], 'dish_is_available':  dish['is_available']})

                    for dish_option in dish['options']:                        
                        if not len(dish_option['option_items']['items']):
                            yield merge_two_dicts(menu_item, {'dish_type_id': menu_info['dish_type_id'], 'dish_type_name':  menu_info['dish_type_name'],
                                         'dish_id': dish['id'], 'dish_name':  dish['name'],
                                         'dish_description': dish['description'], 'dish_price_value':  dish['price']['value'],
                                         'dish_total_like': dish['total_like'], 'dish_is_available':  dish['is_available'],
                                         'dish_option_id': dish_option['id'], 'dish_option_name':  dish_option['name'],
                                         'option_min_select': dish_option['option_items']['min_select'], 'option_max_select':  dish_option['option_items']['max_select']})
                        
                        for item in dish_option['option_items']['items']:
                            yield merge_two_dicts(menu_item, {'dish_type_id': menu_info['dish_type_id'], 'dish_type_name':  menu_info['dish_type_name'],
                                         'dish_id': dish['id'], 'dish_name':  dish['name'],
                                         'dish_description': dish['description'], 'dish_price_value':  dish['price']['value'],
                                         'dish_total_like': dish['total_like'], 'dish_is_available':  dish['is_available'],
                                         'dish_option_id': dish_option['id'], 'dish_option_name':  dish_option['name'],
                                         'option_min_select': dish_option['option_items']['min_select'], 'option_max_select':  dish_option['option_items']['max_select'],
                                         'item_id': item['id'], 'item_name':  item['name'], 'item_price': item['price']['value']})