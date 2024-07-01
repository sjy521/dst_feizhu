import nest_asyncio
import asyncio
import aiohttp
import pandas
import aiomysql
import time
from aiohttp import ClientSession
from asyncio import Semaphore

# 允许嵌套的事件循环
nest_asyncio.apply()

total_requests = 200000
completed_requests = 0
lock = asyncio.Lock()


# 异步函数，用于发送 POST 请求并存储结果
async def fetch_and_save_data(session, pool, url, data, sem):
    global completed_requests
    async with sem:
        async with session.post(url, json=data) as response:
            results = await response.json()
            print(results)
            async with lock:
                completed_requests += 1
                print(f'Progress: {completed_requests}/{total_requests} completed')

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
                return None
            print('通过')
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    sql = "INSERT INTO mt_product_price (hotelId, productId, totalPrice, productLimitRule, date, createTime) VALUES (%s, %s, %s, %s, %s, %s)"
                    await cursor.executemany(sql, formatted_data)
                    await conn.commit()


# 主函数，负责发送请求并存储结果
async def main():
    global total_requests
    url = "http://10.18.99.1:8081/client/spa/batchQueryPrice"
    ids = pandas.read_csv("./9999999999999999.csv")

    sem = Semaphore(10)  # 限制并发数量为200

    # 创建 MySQL 连接池
    pool = await aiomysql.create_pool(
        host='8.146.211.133',
        port=3306,
        user='bystest',
        password='bystest',
        db='bg_admin',
        loop=asyncio.get_event_loop()
    )

    async with ClientSession() as session:
        tasks = []
        for dat in [2, 3, 4]:
            for i in range(0, len(ids['supplier_hotel_id']), 10):
                data = {
                    "checkIn": "2024-07-0{}".format(dat),
                    "checkout": "2024-07-0{}".format(dat + 1),
                    "roomNum": 1,
                    "adultNum": 2,
                    "childNum": 0,
                    "childAges": [],
                    "guestType": 0,
                    "totalPrice": 1000,
                    "suppliers": [
                        {
                            "supplierId": 10001,
                            "shotelId": str(ids['supplier_hotel_id'][i])

                        },
                        {
                            "supplierId": 10001,
                            "shotelId": str(ids['supplier_hotel_id'][i + 1])

                        },
                        {
                            "supplierId": 10001,
                            "shotelId": str(ids['supplier_hotel_id'][i + 2])

                        },
                        {
                            "supplierId": 10001,
                            "shotelId": str(ids['supplier_hotel_id'][i + 3])

                        },
                        {
                            "supplierId": 10001,
                            "shotelId": str(ids['supplier_hotel_id'][i + 4])

                        }
                    ]
                }
                print(data)
                task = asyncio.ensure_future(fetch_and_save_data(session, pool, url, data, sem))
                tasks.append(task)

        await asyncio.gather(*tasks)


    async with ClientSession() as session:
        tasks = []
        for dat in [2, 3, 4]:
            for i in range(0, len(ids['supplier_hotel_id']), 10):
                data = {
                    "checkIn": "2024-07-0{}".format(dat),
                    "checkout": "2024-07-0{}".format(dat + 1),
                    "roomNum": 1,
                    "adultNum": 2,
                    "childNum": 0,
                    "childAges": [],
                    "guestType": 0,
                    "totalPrice": 1000,
                    "suppliers": [
                        {
                            "supplierId": 10001,
                            "shotelId": str(ids['supplier_hotel_id'][i + 5])

                        },
                        {
                            "supplierId": 10001,
                            "shotelId": str(ids['supplier_hotel_id'][i + 6])

                        },
                        {
                            "supplierId": 10001,
                            "shotelId": str(ids['supplier_hotel_id'][i + 7])

                        },
                        {
                            "supplierId": 10001,
                            "shotelId": str(ids['supplier_hotel_id'][i + 8])

                        },
                        {
                            "supplierId": 10001,
                            "shotelId": str(ids['supplier_hotel_id'][i + 9])

                        }
                    ]
                }
                print(data)
                task = asyncio.ensure_future(fetch_and_save_data(session, pool, url, data, sem))
                tasks.append(task)

        await asyncio.gather(*tasks)

    pool.close()
    await pool.wait_closed()


# 检查当前是否在运行事件循环，并选择适当的启动方式
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError:  # 在已有事件循环中运行
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
