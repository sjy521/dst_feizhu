import requests
import mysql.connector


def offhotel(hotel_id):
    config = {
        'host': 'pc-2ze1l4f34v5ql1rsu.rwlb.rds.aliyuncs.com',
        'port': 3306,
        'database': 'hotel_admin',
        'user': 'admin_db_user',
        'password': 'VvTUbbEp$D6uGiLDb'
    }

    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()

        # 执行 SQL 查询
        query = f"""
        DELETE FROM db_up_hotel WHERE distribute_id = '20009' and hotel_id = {hotel_id}
        """
        cursor.execute(query)
        connection.commit()

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        # 清理资源
        if cursor:
            cursor.close()
        if connection:
            connection.close()


    # 刷新白名单缓存
    initurl = ["http://10.18.70.1:8080/hotel/map/init",
               "http://10.18.70.2:8080/hotel/map/init",
               "http://10.18.136.38:8080/hotel/map/init"
               "http://10.18.30.1:8080/douyin/v1.0/offhotel/" + hotel_id]

    for url in initurl:
        requests.get(url)
    return "{}下线成功".format(hotel_id)
