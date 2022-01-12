import psycopg2

class MyDatabase():
    def __init__(self, database = "aces", user = "postgres", password = "a@880126", host =  "127.0.0.1", port = "5432"):
        self.conn = psycopg2.connect(database = database, user = user, password = password , host = host, port = port)
        # # 設置自動提交
        self.conn.autocommit = True
        # 使用cursor()方法創建游標對象
        self.cursor = self.conn.cursor()

    def query(self, query):
        self.cursor.execute(query)

    def close(self):
        self.cursor.close()
        self.conn.close()