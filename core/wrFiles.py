import json
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