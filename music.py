import pandas as pd

# 定義三個分類字典
moods = {
    "Joyful": "0", "Melancholic": "1", "Mysterious": "2", "Nostalgic": "3",
    "Romantic": "4"
}

times = {
    "Morning": "0", "Afternoon": "1", "Evening": "2",
    "Night": "3"
}
events = {
    "Commuting": "0", "Cooking": "1", "Date": "2", "Exercising": "3", "Jornaling": "4",
    "Reflecting": "5", "Relaxing": "6"
}

# 讀取CSV文件（匯入"D:\Github\mood_play\music_1000_with_links_dict_modify.csv"）
df = pd.read_csv("D:/Github/mood_play/music_1000_with_links_dict_modify.csv")

# 將歌曲資料庫轉換為字典
songs_db = df.set_index('key')['titles-artist-youtube_link'].to_dict()

# 提示用戶輸入
def input_user():
    print("請從以下選項輸入對應的詞：")
    print("心情選項：", list(moods.keys()))
    n1 = input("請輸入現在的心情：")

    print("時段選項：", list(times.keys()))
    n2 = input("請輸入現在的時段：")

    print("活動選項：", list(events.keys()))
    n3 = input("請輸入現在正在進行的活動：")
    return n1,n2,n3

# 驗證輸入
def check_input(n1,n2,n3):
    if n1 not in moods or n2 not in times or n3 not in events:
        return False
    else:
        # 將輸入轉成代碼
        int_1 = int(str(moods[n1])+ str(times[n2])+ str(events[n3]))

        # 顯示推薦歌單
        if int_1 in songs_db:
            return True
        else:
            return False

def suggest_name(n1,n2,n3):
    int_1 = int(str(moods[n1])+ str(times[n2])+ str(events[n3]))
    list_1 = songs_db[int_1].split(";")
    list_inner_all = []
    for i in range(len(list_1)):
        list_inner  = list_1[i].split("-")
        list_inner_all.append(list_inner[0]+"-"+list_inner[1])
    return list_inner_all
    
def suggest_URL(n1,n2,n3):
    int_1 = int(str(moods[n1])+ str(times[n2])+ str(events[n3]))
    list_1 = songs_db[int_1].split(";")
    list_inner_all = []
    for i in range(len(list_1)):
        list_inner  = list_1[i].split("-")
        list_inner_all.append(list_inner[2])
    return list_inner_all

def is_valid_input(n1, n2, n3):
    """檢查三個輸入是否都在對應字典內"""
    return n1 in moods and n2 in times and n3 in events

def has_songs(n1, n2, n3):
    """檢查此組合是否有推薦歌單"""
    if not is_valid_input(n1, n2, n3):
        return False
    int_1 = int(str(moods[n1])+ str(times[n2])+ str(events[n3]))
    return int_1 in songs_db

# ========== Flask 應用區塊 ==========
from flask import Flask, request, jsonify, render_template
import threading
import os
import signal

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dicts')
def dicts():
    return jsonify({
        'moods': list(moods.keys()),
        'times': list(times.keys()),
        'events': list(events.keys())
    })

@app.route('/suggest', methods=['POST'])
def suggest_api():
    data = request.get_json()
    mood = data.get('mood')
    time = data.get('time')
    activity = data.get('activity')
    # 檢查輸入
    if not is_valid_input(mood, time, activity):
        return jsonify({'success': False, 'message': '輸入有誤,請重新選擇。'})
    if not has_songs(mood, time, activity):
        return jsonify({'success': False, 'message': '很抱歉,目前尚未有符合此組合的歌單,歡迎日後再來看看！'})
    # 取得所有歌名與網址
    names = suggest_name(mood, time, activity)
    urls = suggest_URL(mood, time, activity)
    # 統一轉為 https://www.youtube.com/watch?v= 的形式
    normal_urls = []
    for url in urls:
        if 'youtube.com' in url:
            video_id = url.split('v=')[-1]
            normal_url = f"https://www.youtube.com/watch?v={video_id}"
        else:
            normal_url = url
        normal_urls.append(normal_url)
    msg = "\n".join([f"{i+1}. {name}" for i, name in enumerate(names)])
    msg = f"根據你的選擇，為你推薦 {len(normal_urls)} 首歌：\n" + msg + "\n將自動依序開啟。"
    return jsonify({'success': True, 'urls': normal_urls, 'message': msg})

@app.route('/exit', methods=['POST'])
def exit_server():
    def shutdown():
        os.kill(os.getpid(), signal.SIGINT)
    threading.Thread(target=shutdown).start()
    return '', 200

@app.route('/popup_test1')
def popup_test1():
    return "<html><body><script>window.close();</script></body></html>"

@app.route('/popup_test2')
def popup_test2():
    return "<html><body><script>window.close();</script></body></html>"

if __name__ == '__main__':
    app.run(debug=True)
    
