import pymysql

conn = pymysql.connect(host="mysql", user="johnny", password="12345", db="epa", charset='utf8mb4')
cursor = conn.cursor()

sql = "select * from `device.iot.test` where event_area ='芳苑工業區';"

cursor.execute(sql)

result = cursor.fetchall()

print(result)
