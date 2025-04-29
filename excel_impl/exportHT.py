import pandas as pd
import mysql.connector
import os


def order_csv(check_in, check_out):
    # 数据库连接配置
    conn = mysql.connector.connect(
        host='pc-2ze1l4f34v5ql1rsu.rwlb.rds.aliyuncs.com',
        port=3306,
        database='hotel_order',
        user='order_db_user',
        password='i7Nbreoq%vMJYbX0b'
    )

    # SQL 查询
    query = """
        SELECT
            CONCAT("'", CAST(bg.bg_order_id AS CHAR)) AS '秉功订单号',
            CONCAT("'", CAST(bg.d_order_id AS CHAR)) AS '分销商订单号',
            CONCAT("'", CAST(bg.s_order_id AS CHAR)) AS '供应商订单号',
            bg.distributor_id as '分销商ID',
            bg.supplier_id as '供应商ID',
            CONCAT("'", CAST(bg.hotel_id AS CHAR)) AS '酒店ID',
            bg.check_in_time AS '入住日期',
            bg.check_out_time AS '离店日期',
            bg.order_status AS '订单状态',
            bg.price /100 as '结算金额',
            bg.seller_price /100 as '售卖金额',
            bg.profit /100 as '利润',
            bg.create_time as '创建时间',
            bg.update_time as '更新时间' 
        FROM
            db_bg_order bg
            JOIN db_order_snapshoot sn ON bg.bg_order_id = sn.order_id 
        WHERE
            sn.order_type = 2 
            AND sn.remark LIKE '混投订单%' 
            AND bg.create_time BETWEEN %s AND %s 
        ORDER BY bg.id DESC
    """

    # 参数示例
    params = (check_in, check_out)

    # 执行查询
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params)
    rows = cursor.fetchall()

    # 转换为 DataFrame
    df = pd.DataFrame(rows)

    # 订单状态映射
    order_status_mapping = {
        10: "待确认",
        11: "已确认",
        12: "已完成",
        13: "待支付",
        14: "已支付",
        15: "待处理",
        20: "已退款",
        21: "部分退款",
        22: "已拒单",
        23: "已取消",
        24: "下单失败",
        25: "取消失败",
        26: "取消成功",
        27: "支付失败",
        30: "特殊订单",
        99: "异常订单"
    }

    df['订单状态'] = df['订单状态'].map(order_status_mapping)

    # 分销商映射
    distribute_id_mapping = {
        20001: "去哪",
        20002: "美团",
        20007: "同程艺龙",
        20009: "抖音"
    }

    # 供应商映射
    supplier_id_mapping = {
        10004: "四海通",
        90001: "携程外采"
    }

   # df['分销商ID'] = df['分销商ID'].map(distribute_id_mapping)
   # df['供应商ID'] = df['供应商ID'].map(supplier_id_mapping)
    # 映射过程中填充缺失值
    df['分销商ID'] = df['分销商ID'].map(distribute_id_mapping).fillna(df['分销商ID'])
    df['供应商ID'] = df['供应商ID'].map(supplier_id_mapping).fillna(df['供应商ID'])


    # 创建输出文件夹路径
    output_directory = "./"
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # 完整的文件路径（保存为 .csv 格式）
    output_file = os.path.join(output_directory, "混投订单明细.csv")

    # 使用 utf-8 编码导出 CSV
    df.to_csv(output_file, index=False, encoding='utf-8-sig')

    return output_file
