
# 定義三個分類字典
moods = {
    "快樂": "0", "難過": "1", "憤怒": "2", "放鬆": "3",
    "焦慮": "4", "愛戀": "5", "無聊": "6", "興奮": "7"
}

times = {
    "上午": "0", "中午": "1", "下午": "2",
    "傍晚": "3", "夜晚": "4", "凌晨": "5"
}

events = {
    "跑步": "0", "派對": "1", "讀書": "2", "放空": "3", "工作": "4",
    "約會": "5", "冥想": "6", "旅行": "7", "開車": "8", "運動": "9"
}

# 模擬歌曲資料庫（編號為「心情時段活動」的代碼）
songs_db = {
    "011": ["Dancing Queen - ABBA", "Uptown Funk - Bruno Mars"],
    "345": ["Lovely - Billie Eilish", "Someone You Loved - Lewis Capaldi"],
    "712": ["Blinding Lights - The Weeknd"],
    "004": ["Happy - Pharrell Williams"],
    "132": ["Shivers - Ed Sheeran"],
    "123": ["Stay - The Kid LAROI, Justin Bieber"],
    # ...可以持續擴充
}

# 提示用戶輸入
print("請從以下選項輸入對應的詞：")
print("心情選項：", list(moods.keys()))
n1 = input("請輸入現在的心情：")

print("時段選項：", list(times.keys()))
n2 = input("請輸入現在的時段：")

print("活動選項：", list(events.keys()))
n3 = input("請輸入現在正在進行的活動：")

# 驗證輸入
if n1 not in moods or n2 not in times or n3 not in events:
    print("輸入有誤,請重新啟動程式並確認拼字正確。")
else:
    # 將輸入轉成代碼
    list_1 = [moods[n1], times[n2], events[n3]]
    code = "".join(list_1)

    # 顯示推薦歌單
    if code in songs_db:
        print("\n根據你的選擇,為你推薦以下歌單：")
        for song in songs_db[code]:
            print(song)
    else:
        print("\n很抱歉,目前尚未有符合此組合的歌單,歡迎日後再來看看！")