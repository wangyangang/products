# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import csv
import os
import MySQLdb
import MySQLdb.cursors
from twisted.enterprise import adbapi
import warnings
import json


class MySQLPipeline:
    @classmethod
    def from_settings(cls, settings):
        return cls(settings)

    def __init__(self, settings):
        self.settings = settings
        config = {
            'host': settings['MYSQL_HOST'],
            'port': settings['MYSQL_PORT'],
            'db': settings['MYSQL_DBNAME'],
            'user': settings['MYSQL_USER'],
            'passwd': settings['MYSQL_PASSWORD'],
            'charset': 'utf8mb4',
            'cursorclass': MySQLdb.cursors.DictCursor,
           'init_command': 'set foreign_key_checks=0'  # 异步容易冲突
        }
        self.dbpool = adbapi.ConnectionPool('MySQLdb', **config)

    def open_spider(self, spider):
        host = self.settings['MYSQL_HOST']
        user = self.settings['MYSQL_USER']
        passwd = self.settings['MYSQL_PASSWORD']
        port = self.settings['MYSQL_PORT']
        dbname = self.settings['MYSQL_DBNAME']
        try:
            self.init_database(host, user, passwd, port, dbname)
        except ImportError:
            spider.pymysql_error = True
        except MySQLdb.OperationalError:
            spider.mysql_error = True

    def init_database(self, host, user, passwd, port, dbname):
        warnings.filterwarnings('ignore', message=".*exists.*")
        warnings.filterwarnings('ignore', message=".*looks like a.*")
        db = MySQLdb.connect(host=host, user=user, passwd=passwd, port=port)
        tx = db.cursor()
        tx.execute('set names utf8mb4')
        sql = 'create database if not exists `%s` default charset utf8mb4 default collate utf8mb4_general_ci;' % MySQLdb.escape_string(dbname).decode("utf8")
        tx.execute(sql)
        # 要用斜引号不然报错
        # 万恶的MySQLdb会自动加上单引号 结果导致错误
        db.select_db(dbname)
        tx.execute("""create table if not exists products(
            id INT(11) NOT NULL AUTO_INCREMENT, 
            page VARCHAR(30), 
            _index VARCHAR(30), 
            catalogue_number VARCHAR(500),
            chemical_name VARCHAR(500),
            cas_number VARCHAR(500),
            synonyms TEXT,
            molecular_formula VARCHAR(500),
            molecular_weight VARCHAR(500),
            order_products VARCHAR(500),
            PRIMARY KEY (id)
            ) DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;""")

        db.commit()
        db.close()

    def process_item(self, item, spider):
        _conditional_insert = {
            'products': self.insert_products,
        }
        query = self.dbpool.runInteraction(_conditional_insert[item.name], item)
        query.addErrback(self._handle_error, item, spider)
        return item

    def insert_products(self, trans, item):
        sql = 'insert into products(page, _index, catalogue_number, chemical_name, cas_number, synonyms,' \
              'molecular_formula, molecular_weight, order_products) values (%s, %s, %s, %s, %s, %s, ' \
              '%s, %s, %s)'
        order_products = item['order_products']
        order_products = json.dumps(order_products) if order_products else ''
        params = (item['page'], item['index'], item['catalogue_number'], item['chemical_name'], item['cas_number'], item['synonyms'],
                  item['molecular_formula'], item['molecular_weight'], order_products)
        trans.execute(sql, params)

    def _handle_error(self, fail, item, spider):
        # spider.logger.error('Insert to database error: %s \
        #         when dealing with item: %s' % (fail, item))
        print('------------------insert error')
        print(fail)
        print(item)


class ProductsPipeline:
    def open_spider(self, spider):
        if not os.path.exists('output.csv'):
            with open('output.csv', 'a+', encoding='utf_8_sig', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['catalogue number', 'chemical name', 'cas number', 'synonyms', 'molecular formula',
                                 'molecular weight', 'order products'])
    def process_item(self, item, spider):
        with open('output.csv', 'a+', encoding='utf_8_sig', newline='') as f:
            writer = csv.writer(f)
            row = list()

            row.append(item['catalogue_number'])
            row.append(item['chemical_name'])
            row.append(item['cas_number'])
            row.append(item['synonyms'])
            row.append(item['molecular_formula'])
            row.append(item['molecular_weight'])
            order_products = item['order_products']
            for order_product in order_products:
                row.append(order_product[0])
                row.append(order_product[1])
            writer.writerow(row)
        return item
