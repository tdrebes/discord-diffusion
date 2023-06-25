import json
import sqlite3

DATABASE = 'data.db'
class Database:
    def __init__(self):
        con = sqlite3.connect(DATABASE)
        cur = con.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS history(user_id INTEGER PRIMARY KEY, content TEXT)')
        cur.close()
        con.close()

    def __query_fetch_one(self, query, params):
        con = sqlite3.connect(DATABASE)
        cur = con.cursor()
        res = cur.execute(query, params).fetchone()
        cur.close()
        con.close()
        return res

    def __query_commit(self, query, params):
        con = sqlite3.connect(DATABASE)
        cur = con.cursor()
        res = cur.execute(query, params)
        con.commit()
        cur.close()
        con.close()
        return res

    def get_history(self, user_id):
        res = self.__query_fetch_one('SELECT * FROM history WHERE user_id = ?', (str(user_id),))

        if res is None: 
            return

        return res[1]
    
    def set_history(self, user_id, history):
        return self.__query_commit('INSERT OR REPLACE INTO history (user_id, content) VALUES (?, ?)', (user_id, json.dumps(history)))
