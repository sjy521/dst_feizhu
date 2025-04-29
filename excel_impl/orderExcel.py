import pandas as pd
import mysql.connector


def order_excel(check_in, check_out):

    # 数据库连接配置
    conn = mysql.connector.connect(
        host='pc-2ze1l4f34v5ql1rsu.rwlb.rds.aliyuncs.com',
        port= 3306,
        database= 'hotel_order',
        user='order_db_user',
        password='i7Nbreoq%vMJYbX0b'
    )

    # SQL 查询
    query = """
        SELECT
            CONCAT("'", CAST(dbo.bg_order_id AS CHAR)) AS '秉功订单号',
            CONCAT("'", CAST(dbo.d_order_id AS CHAR)) AS '分销商订单号',
            CONCAT("'", CAST(dso.s_order_id AS CHAR)) AS '供应商订单号',
            CONCAT("'", CAST(dso.supplier_id AS CHAR)) AS '供应商ID',
            CONCAT("'", CAST(ddo.distributor_id AS CHAR)) AS '分销商ID',
            dbo.business_type AS '业务类型',
            CONCAT("'", CAST(dbo.hotel_id AS CHAR)) AS '酒店ID',
            doi.hotel_name AS '酒店名称',
            doi.consumer_name AS '入住人',
            doi.room_count AS '间',
            DATEDIFF(dbo.check_out_time, dbo.check_in_time) AS '夜',
            dbo.create_time AS '预定日期',
            dbo.check_in_time AS '入住日期',
            dbo.check_out_time AS '离店日期',
            dpt.pay_price / 100.0 AS '供应商退款金额',
            dbo.deduction / 100.0 AS '分销商扣款',
            dpt.pay_time AS '退款时间',
            dso.brokerage / 100.0 AS '佣金',
            dbo.seller_price / 100.0 AS '售卖价',
            dbo.price / 100.0 AS '结算价',
            'CNY' AS '币种',
            doi.product_name AS '房型',
            '售卖渠道' AS '售卖渠道',
            dbo.order_status AS '订单状态',
            dbo.remark AS '备注',
            CASE WHEN dbo.tp_status = 0 THEN '否' ELSE '是' END AS '是否退赔',
            CASE WHEN dbo.pft_status = 0 THEN '否' ELSE '是' END AS '是否赔付退'
        FROM
            db_bg_order dbo
            INNER JOIN db_order_item doi ON dbo.d_order_id = doi.order_id
            INNER JOIN db_distributor_order ddo ON dbo.d_order_id = ddo.d_order_id AND ddo.distributor_id = dbo.distributor_id
            LEFT JOIN db_supplier_order dso ON dbo.s_order_id = dso.s_order_id AND dso.supplier_id = dbo.supplier_id
            LEFT JOIN db_payment_transaction dpt ON dpt.s_order_id = dso.s_order_id AND dpt.pay_type = 2
        WHERE
            dbo.create_time BETWEEN %s AND %s
        ORDER BY dbo.id
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

    # 导出到 Excel
    output_file = "订单导出.csv"
    df.to_csv(output_file, index=False)
    return output_file
