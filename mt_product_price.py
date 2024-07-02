import os
import sys
import traceback
import pandas
import aiomysql
import time
import json
import logging
import aiohttp
import asyncio
from threading import Thread
import urllib
from aiohttp import TCPConnector


lock = asyncio.Lock()
completed_requests = 0
hotel_error_list = []
passlist = []

async def fetch(session, url, hotel_data):
    async with semaphore:
        try:
            for _ in range(3):
                async with session.request("post", url, json=hotel_data) as response:
                    res = await response.text()
                    return res
        except:
            print((traceback.format_exc()))
            return False


def start_thread_loop(loop):
    """
    启动一个loop线程
    :param loop:
    :return:
    """

    asyncio.set_event_loop(loop)
    loop.run_forever()


async def task(hotel_data, next_cursor=None):
    """
    更新个人橱窗详情
    :return:
    """
    #     print(name)
    url = "http://10.18.99.1:8081/client/spa/batchQueryPrice"


    conn = aiohttp.TCPConnector(ssl=True)
    async with aiohttp.ClientSession(connector=conn) as session:
        html = await fetch(session, url, hotel_data)
        if html is False:
            return None
        await parser(html, hotel_data)


async def parser(html, hotel_id):
    """
    解析个人橱窗详情信息
    :return:
    """
    global completed_requests
    try:
        pool = await aiomysql.create_pool(
            host='8.146.211.133',
            port=3306,
            user='bystest',
            password='bystest',
            db='bg_admin',
            loop=asyncio.get_event_loop()
        )
        async with lock:
            completed_requests += 1
            print(f'Progress: {completed_requests} completed')

        results = json.loads(html)
        formatted_data = []
        try:
            for res in results['result']:
                for result in res['productRespDTOList']:
                    if result['productId'] is None:
                        continue
                    formatted_data.append((result['hotelId'], result['productId'], result['totalPrice'],
                                           result['productInfo']['productLimitRule'],
                                           result['priceInfos'][0]['date'],
                                           time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        except Exception as f:
            #                 print(f)
            return None

        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                sql = "INSERT INTO mt_product_price (hotelId, productId, totalPrice, productLimitRule, date, createTime) VALUES (%s, %s, %s, %s, %s, %s)"

                await cursor.executemany(sql, formatted_data)
                await conn.commit()
                print(len(formatted_data))
    except Exception as f:
        print(f)



def run_windows_detail(res_data):
    global semaphore, new_loop
    new_loop = asyncio.new_event_loop()
    semaphore = asyncio.Semaphore(30)
    loop_thread = Thread(target=start_thread_loop, args=(new_loop,))
    # loop_thread.setDaemon(True)
    loop_thread.start()
    ids = pandas.read_csv("./9999999999999999.csv")
    for dat in [2, 3, 4]:
        for i in range(len(ids['supplier_hotel_id']) -10, -1, -10):

            data = {
                "checkIn": "2024-07-0{}".format(dat),
                "checkout": "2024-07-0{}".format(dat + 1),
                "roomNum": 1,
                "adultNum": 2,
                "childNum": 0,
                "childAges": [],
                "guestType": 0,
                "totalPrice":1000,

                "suppliers": [
                    {
                        "supplierId": 10001,
                        "shotelId": str(ids['supplier_hotel_id'][i])

                    },
                    {
                        "supplierId": 10001,
                        "shotelId": str(ids['supplier_hotel_id'][i+1])

                    },
                    {
                        "supplierId": 10001,
                        "shotelId": str(ids['supplier_hotel_id'][i+2])

                    },
                    {
                        "supplierId": 10001,
                        "shotelId": str(ids['supplier_hotel_id'][i+3])

                    },
                    {
                        "supplierId": 10001,
                        "shotelId": str(ids['supplier_hotel_id'][i+4])

                    },
                    {
                        "supplierId": 10001,
                        "shotelId": str(ids['supplier_hotel_id'][i+5])

                    },
                    {
                        "supplierId": 10001,
                        "shotelId": str(ids['supplier_hotel_id'][i+6])

                    },
                    {
                        "supplierId": 10001,
                        "shotelId": str(ids['supplier_hotel_id'][i+7])

                    },
                    {
                        "supplierId": 10001,
                        "shotelId": str(ids['supplier_hotel_id'][i+8])

                    },
                    {
                        "supplierId": 10001,
                        "shotelId": str(ids['supplier_hotel_id'][i+9])

                    }
                ]
            }

            asyncio.run_coroutine_threadsafe(task(data), new_loop)


if __name__ == '__main__':

    run_windows_detail('')


