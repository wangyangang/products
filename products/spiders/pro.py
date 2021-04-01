import scrapy
from products.items import ProductsItem


class ProSpider(scrapy.Spider):
    name = 'pro'
    allowed_domains = ['trc-canada.com']
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'cookie': '__cfduid=d9e7ce66be6cb192cbe7cfbedba73d8ac1617237871; PHPSESSID=6ee6204a40b6d25b128960447a2a6b83; _ga=GA1.2.928918517.1617237874; _gid=GA1.2.1731342203.1617237874; _hjTLDTest=1; _hjid=4d932396-ffae-4078-bd43-2ace9026bf13',
        'referer': '',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'
    }
    def start_requests(self):

        base_url = 'https://www.trc-canada.com/products-listing/?pages={}'
        for page in range(1, 34585):  # 共7686页
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





