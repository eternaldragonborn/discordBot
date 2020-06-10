import json

def readFile(file):
    with open(f"{file}.json", "r", encoding="utf8") as f:
        return json.load(f)

def writeFile(file, data):
    with open(f"{file}.json", "w", encoding="utf8") as f:
        json.dump(data, f, indent="\t")
    return