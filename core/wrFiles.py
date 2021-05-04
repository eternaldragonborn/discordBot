# coding=utf-8
# -*- coding: UTF-8 -*-
import json, MySQLdb, os
from redis import Redis, ConnectionPool

def readFile(file):
    with open(f"{file}.json", "r", encoding="utf8") as f:
        return json.load(f)

def writeFile(file, data):
    with open(f"{file}.json", "w", encoding="utf8") as f:
        json.dump(data, f, indent="\t")
    return

setting = readFile("setting")["redis"]
host = setting["host"]
port = setting["port"]
password = setting["password"]
pool = ConnectionPool(host=host, port=port, password=password, decode_responses = True)

def get_data():
  r = Redis(connection_pool=pool)
  subscribers = json.loads(r.get("subscribers"))
  artists = json.loads(r.get("artists"))
  pool.disconnect()
  return {"subscribers":subscribers, "artists":artists}

def set_data(data):
  r = Redis(connection_pool=pool)
  for key, value in data.items():
    r.set(key, json.dumps(value))
  pool.disconnect()
  return

def conn():  
  return MySQLdb.connect(host=os.environ['SQL_host'],
                        user=os.environ['SQL_user'],
                        passwd=os.environ['SQL_passwd'],
                        db=os.environ['SQL_db'],
                        charset='utf8', use_unicode=True)

db = conn()

def get_cursor():  #確認連線狀況並回傳cursor
  global db
  try:  cursor = db.cursor()
  except:
    db = conn()
    cursor = db.cursor()
  finally:  return cursor

def SQL_modify(query):
  global db
  with get_cursor() as cursor:
    try:
      cursor.execute(query)
      db.commit()
    except Exception as e:
      db.rollback()
      raise e
    else:  return
      
def SQL_inquiry(query):
  with get_cursor() as cursor:
    cursor.execute(query)
    return cursor.fetchall()

def SQL_getData(table, column, data, num:int =None):
  if num:
    result = SQL_inquiry(f'SELECT * FROM {table} WHERE {column}="{data}" LIMIT {num}')
    if result and num == 1:  return result[0]
    elif result:  return result
  else:  return SQL_inquiry(f'SELECT * FROM {table} WHERE {column}="{data}"')