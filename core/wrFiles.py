# coding=utf-8
# -*- coding: UTF-8 -*-
import json, MySQLdb, os

def readFile(file):
    with open(f"{file}.json", "r", encoding="utf8") as f:
        return json.load(f)

def writeFile(file, data):
    with open(f"{file}.json", "w", encoding="utf8") as f:
        json.dump(data, f, indent="\t")
    return

def conn():
  return MySQLdb.connect(host=os.environ['SQL_HOST'],
                        user=os.environ['SQL_USER'],
                        passwd=os.environ['SQL_PASSWD'],
                        db=os.environ['SQL_DB'],
                        charset='utf8', use_unicode=True)

db = conn()

def get_cursor():  #確認連線狀況並回傳cursor
  global db
  try:  db.cursor().execute("SELECT 1")
  except:
    db = conn()
  finally:  return db.cursor()

def SQL_modify(query):
  global db
  with get_cursor() as cursor:
    try:
      cursor.execute(query)
      db.commit()
    except Exception as e:
      db.rollback()
      raise e
  return
      
def SQL_inquiry(query, num:int=None):
  global db
  if num:  query += f" LIMIT {num}"  #有限制查詢筆數
  with get_cursor() as cursor:
    cursor.execute(query)
    result = cursor.fetchall()
    if result and num==1:  result = result[0]
  return result

def SQL_getData(table, column, data, num:int =None):
  return SQL_inquiry(f'SELECT * FROM {table} WHERE {column}="{data}"', num)