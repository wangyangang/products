import scrapy
from products.items import ProductsItem


class ProSpider(scrapy.Spider):
    name = 'pro'
    allowed_domains = ['trc-canada.com']
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'cookie': '__cfduid=d1a7a88f6a416665107bd813946cf5f091617295400; PHPSESSID=b862e9f533d8ef6e3a278eee834cf0aa; _ga=GA1.2.1670005499.1617266607; _gid=GA1.2.920446026.1617266607; _gat=1; _gat_gtag_UA_67919503_1=1; _hjTLDTest=1; _hjid=8bb41c55-5489-48e8-90f4-97dc4f83a823; _hjFirstSeen=1',
        'referer': '',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.146 Safari/537.36'
    }
    def start_requests(self):

        base_url = 'https://www.trc-canada.com/products-listing/?pages={}'
        for page in range(22000, 34585):  # 共7686页
            print('正在抓取第 %d/%d 页' % (page, 34584))
            if page != 1:
                referer = 'https://www.trc-canada.com/products-listing/?pages={}'.format(page-1)
                self.headers.update(referer=referer)
            url = base_url.format(page)
            yield scrapy.Request(url, headers=self.headers, dont_filter=True, cb_kwargs={
                'page': page
            })

    def parse(self, response, **kwargs):
        page = kwargs.get('page')
        products = response.xpath('//div[@class="chemCard"]')
        for index, product in enumerate(products):
            href = product.xpath('./a[1]/@href').get()
            detail_url = 'https://www.trc-canada.com' + href
            referer = 'https://www.trc-canada.com/products-listing/?pages='.format(page)
            self.headers.update(referer=referer)
            yield scrapy.Request(detail_url, headers=self.headers, dont_filter=True,
                                 callback=self.parse_detail, cb_kwargs={
                    'page': page,
                    'index': index + 1
                })

    def parse_detail(self, response, **kwargs):
        page = kwargs.get('page')
        index = kwargs.get('index')
        rows = response.xpath('//table[@id="orderProductTable"]/tbody//tr')
        order_products = []
        for row in rows:
            pack_size = row.xpath('./td[1]/text()').get()
            price = row.xpath('./td[3]/text()').get()
            order_products.append([pack_size, price])
        catalogue_number = response.xpath(
            '//table[@id="productDes"]//td[text()="Catalogue Number"][1]/following-sibling::td[1]/text()').get()
        chemical_name = response.xpath(
            '//table[@id="productDes"]//td[text()="Chemical Name"][1]/following-sibling::td[1]/text()').get()
        cas_number = response.xpath(
            '//table[@id="productDes"]//td[text()="CAS Number"][1]/following-sibling::td[1]/text()').get()
        synonyms = response.xpath(
            '//table[@id="productDes"]//td[text()="Synonyms"][1]/following-sibling::td[1]/text()').get()
        molecular_formula = response.xpath(
            '//table[@id="productDes"]//td[text()="Molecular Formula"][1]/following-sibling::td[1]/text()').get()
        molecular_weight = response.xpath(
            '//table[@id="productDes"]//td[text()="Molecular Weight"][1]/following-sibling::td[1]/text()').get()
        print(page, index, catalogue_number, cas_number)
        item = ProductsItem()
        item['page'] = page
        item['index'] = index
        item['order_products'] = order_products
        item['catalogue_number'] = catalogue_number
        item['chemical_name'] = chemical_name
        item['cas_number'] = cas_number
        item['synonyms'] = synonyms
        item['molecular_formula'] = molecular_formula
        item['molecular_weight'] = molecular_weight
        yield item





