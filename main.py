# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 00:17:09 2022

@author: public
"""

import requests
import json
import datetime
import sqlite3

from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

origins = [
    "http://localhost:3000",
    "https://bot-interactive-app.vercel.app",
] # クライアントのurl

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
    )
    
# bot返信に関する処理
class Response:
    def response(user_input):
        # ユーザ入力に対する、botの返信
        if user_input == "おはようございます":
            bot_response = "おはようございます。"
        
        elif user_input == "こんにちは":
            bot_response = "こんにちは。"
        
        elif user_input == "こんばんは":
            bot_response = "こんばんは。"
        
        elif user_input == "ゆちすき":
            bot_response = "しおちすき"
        
        elif user_input == "今何時？":
            dt = datetime.datetime.now()
            bot_response = f'{dt.hour}時{dt.minute}分です。'
        
        elif user_input == "今日の札幌の天気は？":
            # 気象庁データから札幌の天気を取得
            CITY_ID = "016000"
            weather = Response._whether_weather(CITY_ID)
            bot_response = f'{weather} です。'
        
        elif user_input == "今日の東京の天気は？":
            # 気象庁データから東京の天気を取得
            CITY_ID = "130000"
            weather = Response._whether_weather(CITY_ID)
            bot_response = f'{weather} です。'
        
        elif user_input == "今日の大阪の天気は？":
            #気象庁データから大阪の天気を取得
            CITY_ID = "270000"
            weather = Response._whether_weather(CITY_ID)
            bot_response = f'{weather} です。'
        
        elif user_input == "今日の福岡の天気は？":
            #気象庁データから福岡の天気を取得
            CITY_ID = "400000"
            weather = Response._whether_weather(CITY_ID)
            bot_response = f'{weather} です。'
        
        else:
            bot_response = "質問を理解できませんでした"
            
        return bot_response
    
    def _whether_weather(city_id):
        # 天気apiから天気を取得する
        jma_url = "https://www.jma.go.jp/bosai/forecast/data/forecast/" + city_id + ".json"
        jma_json = requests.get(jma_url).json()

        #取得したいデータを選ぶ
        jma_weather = jma_json[0]["timeSeries"][0]["areas"][0]["weathers"][0]
        # 全角スペースの削除
        jma_weather = jma_weather.replace('　', ' ')
        #リスト化
        jma_weather = jma_weather.split()
        
        #現在の天気を示す最初の文言を出力
        return jma_weather[0]

# データベースに関する処理
class Database:
    _DBNAME = 'HISTORY.db'
    
    def register(user_input, bot_response, response_timestamp):
        #データベースに会話記録を保存する
        
        conn = sqlite3.connect(Database._DBNAME)
        cur = conn.cursor()
        
        cur.execute('CREATE TABLE IF NOT EXISTS history(user_input STRING, bot_response STRING, response_timestamp STRING)')
        cur.execute('INSERT INTO history(user_input, bot_response, response_timestamp) values(?, ?, ?)',
                    [user_input, bot_response, response_timestamp])
        
        conn.commit()
        
        cur.close()
        conn.close()
    
    def retrival(reference_number):
        # データベースから会話履歴を取得する
        conn = sqlite3.connect(Database._DBNAME)
        cur = conn.cursor()
        
        cur.execute('CREATE TABLE IF NOT EXISTS history(user_input STRING, bot_response STRING, response_timestamp STRING)')
        
        db_col = [ "user_input", "bot_response", "response_timestamp" ]
        cur.execute('select * from history')
        select_history = cur.fetchall()
        talking_history = []
        for item in select_history:
            d_history = dict(zip(db_col, item))
            talking_history.append(d_history)
        
        conn.close()
        talking_history.reverse()
        
        return talking_history[0:reference_number]

class Item(BaseModel):
    user_input: str

@app.post("/chat")
def post_request(item: Item):
    user_input = item.user_input
    # 時刻を記録する
    dt = datetime.datetime.now()
    response_timestamp = dt.replace(microsecond = 0)
    
    # ユーザ入力からデータベースに登録まで
    bot_response = Response.response(user_input)
    
    Database.register(user_input, bot_response, response_timestamp)

    return {"user_input":user_input, "bot_response":bot_response, "response_timestamp":response_timestamp}

#getリクエストが来たときに実行
@app.get("/history/list")
def get_request():
    #　データベースから過去の会話記録を取得してreactに返信
    REFERENCE_NUMBER = 10
    talking_history = Database.retrival(REFERENCE_NUMBER)
        
    return talking_history

