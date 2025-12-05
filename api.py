# api.py
from flask import Flask, jsonify
import mysql.connector
from datetime import datetime, timedelta
import os # 导入 os 模块以获取环境变量

app = Flask(__name__)

# 从环境变量获取数据库配置，增强安全性
db_config = {
    "host": os.environ.get("DB_HOST"),
    "port": int(os.environ.get("DB_PORT")),
    "user": os.environ.get("DB_USER"),
    "password": os.environ.get("DB_PASSWORD"),
    "database": os.environ.get("DB_NAME")
}

@app.route("/")
def home():
    return "Weather API is running!"

@app.route("/weather/latest/<station_id>", methods=["GET"])
def get_latest_weather(station_id):
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor(dictionary=True) # 以字典形式返回结果

        # 计算查询的起始时间：当前时间减去 8 小时
        eight_hours_ago = datetime.now() - timedelta(hours=8)

        # 查询数据库中近8小时的温度湿度数据
        query = """
        SELECT UpdateTime, TEM, RHU
        FROM weather_data_m7263
        WHERE Station_ID_C = %s AND UpdateTime >= %s
        ORDER BY UpdateTime ASC;
        """
        cursor.execute(query, (station_id, eight_hours_ago))
        results = cursor.fetchall()

        processed_results = []
        for row in results:
            # 将UpdateTime从datetime对象转换为ISO格式的字符串
            if isinstance(row['UpdateTime'], datetime):
                row['UpdateTime'] = row['UpdateTime'].isoformat()
            processed_results.append(row)

        return jsonify(processed_results)

    except mysql.connector.Error as err:
        print(f"数据库查询失败: {err}")
        return jsonify({"error": "Database query failed", "details": str(err)}), 500
    except Exception as e:
        print(f"未知错误: {e}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'cnx' in locals() and cnx and cnx.is_connected():
            cnx.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
