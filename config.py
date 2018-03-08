import json
import shutil

def init():
    global settings
    try:
        with open("config.json") as jsonConfig:
            settings = json.load(jsonConfig)
    except Exception:
        print("Configuration file not found. Creating new one from template.")
        shutil.copyfile("config.template.json", "config.json")
        with open("config.template.json") as jsonConfig:
            settings = json.load(jsonConfig)