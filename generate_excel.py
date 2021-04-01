"""
@author:  wangyangang
@contact: wangyangang@wangyangang.com
@site:    https://wangyangang.com
@time:   3/21/21 - 3:17 PM
"""
import pymysql
import json
import csv
import os


def run():
    host = '127.0.0.1'
    port = 3306
    user = 'root'
    passwd = '456wyg31'
    db = 'trc_canada_products'
    conn = pymysql.connect(host=host, user=user, passwd=passwd, port=port, db=db)
    cursor = conn.cursor()
    # cursor.execute('set names utf8mb4')
    products_sql = 'select page, _index, catalogue_number, chemical_name, cas_number, synonyms, molecular_formula, ' \
                   'molecular_weight, order_products from products order by CAST(page as DECIMAL), ' \
                   'CAST(_index as DECIMAL)'
    cursor.execute(products_sql)
    products = cursor.fetchall()
    num = len(products)

    if not os.path.exists('output.csv'):
        with open('output.csv', 'a+', encoding='utf_8_sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['页码', '序号', 'catalogue_number', 'chemical_name', 'cas_number', 'synonyms',
                             'molecular_formula', 'molecular_weight', 'order_products'])

    for product_index, pro in enumerate(products):
        print('%d/%d' % (product_index + 1, num))
        row = list()
        row.extend([pro[0], pro[1], pro[2], pro[3], pro[4], pro[5], pro[6], pro[7]])
        order_products = json.loads(pro[8]) if pro[8] else []
        for order_product in order_products:
            row.append(order_product[0])
            row.append(order_product[1])

        with open('output.csv', 'a+', encoding='utf_8_sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(row)


if __name__ == '__main__':
    run()