import requests
import time
# from app import db, Results


class BaseSearcher(object):
    query = ''
    tag = ''
    page_num = 0
    page_size = 20
    offset = 0.08  # 经纬度的偏移值
    ak = '0Da09129a81fd709030b0b34995f1e74'  # 百度地图key
    lat = ''
    lng = ''

    # API 搜索
    # 文档 http://lbsyun.baidu.com/index.php?title=webapi/guide/webservice-placeapi
    api_search_v2 = 'http://api.map.baidu.com/place/v2/search'

    def __init__(self, query, lat, lng):
        self.query = query
        self.lat = lat
        self.lng = lng

        self.create_params()

    def create_params(self):
        self.params = {
            'query': self.query,
            'tag': self.tag,
            'page_num': self.page_num,
            'page_size': self.page_size,
            'ak': self.ak,
            'bounds': self.get_bounds(),
            'output': 'json'}

    def get_bounds(self):
        return str(self.lat) + ',' + str(self.lng) + ',' + str(self.lat+self.offset) + ',' + str(self.lng+self.offset)

    def get_data(self):
        self.create_params()
        return requests.get(self.api_search_v2, params=self.params)


class Searcher(BaseSearcher):
    end_lat = ''
    end_lng = ''
    total_num = ''
    total_page = ''
    old_request_data = ''   # 上一次获取的数据

    def __init__(self, query, lat, lng, end_lat, end_lng):
        self.query = query
        self.lat = lat
        self.lng = lng
        self.end_lat = end_lat
        self.end_lng = end_lng

        self.create_params()

    # 获取所有范围内的信息
    def get_all_data(self):
        times = 0
        while self.lat < self.end_lat:
            while self.lng < self.end_lng:
                r = self.get_data()
                data = r.json()
                print(data)
                time.sleep(0.5)
                if data["status"] == 401:
                    time.sleep(5)
                    r = self.get_data()
                    data = r.json()
                    print(data)

                # 记录上次请求到的数组，避免过多重复请求
                if data['results'] == self.old_request_data:
                    continue
                self.old_request_data = data['results']

                print(data)
                if data['status'] == 1 or data['total'] == 0:
                    items = data['results']
                    self.save_data(items)

                    times += 1
                    self.page_num = 0
                    print('get failure    ' + 'times:' + str(times))
                    print(self.params)
                else:
                    self.total_num = data['total']
                    self.total_page = int(self.total_num/self.page_size)

                    for page_now in range(0, self.total_page):
                        self.page_num = page_now
                        response = self.get_data()
                        json = response.json()
                        try:
                            items = json['results']
                            self.save_data(items)

                            times += 1
                            print("times: " + str(times))
                        except Exception as e:
                            print(e)

            self.lng = self.lng + self.offset
        self.lat = self.lat + self.offset

    def save_data(self, items):
        for item in items:
            name = item['name']
            address = item['address']
            telephone = ''
            try:
                telephone = item['telephone']
                print(name, address, telephone)
            except:
                pass
            # print(address)

            # q = Results.query.filter(Results.address == address).first()
            # if q is None:
            #     result = Results(name=name, address=address, telephone=telephone)
            #     db.session.add(result)
            #     db.session.commit()


# searcher = Searcher('手机$数码$通信$通讯', 23.0525730000,
#                     113.1989640000, 23.2904550000, 113.5010820000)
# searcher.get_all_data()


searcher = Searcher('咖啡', 23.0525730000,
                    113.1989640000, 23.2904550000, 113.5010820000)
searcher.get_all_data()
