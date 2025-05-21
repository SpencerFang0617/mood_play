import pandas as pd
from flask import Flask, request, jsonify, render_template
import threading
import time
import os

# --- 核心數據字典 ---
# 這些字典的鍵 (keys) 必須與前端下拉選單的選項一致。
# 這些字典的值 (values) 必須與 `轉檔用.py` 中 mood_map, time_map, activity_map 的數字編碼一致，
# 以便正確生成用於查詢 CSV 的整數 key。

# 心情字典 (對應 mood_map from 轉檔用.py)
# Keys: 前端選項 (CamelCase)
# Values: 對應的數字字串 (用於生成 key)
moods = {
    'Calm': '0',        # 平靜
    'Cathartic': '1',   # 宣洩
    'Comforting': '2',  # 安慰
    'Empowering': '3',  # 賦予力量
    'Excited': '4',     # 興奮
    'Joyful': '5',      # 快樂
    'Melancholic': '6', # 憂鬱
    'Mysterious': '7',  # 神秘
    'Nostalgic': '8',   # 懷舊
    'Romantic': '9'     # 浪漫
}

# 時段字典 (對應 time_map from 轉檔用.py)
# Keys: 前端選項 (CamelCase)
# Values: 對應的數字字串
times = {
    'Morning': '0',     # 早上 (對應 'morning': 0)
    'Afternoon': '1',   # 下午 (對應 'afternoon': 1)
    'Evening': '2',     # 傍晚 (對應 'evening': 2)
    'Night': '3'        # 晚上 (對應 'night': 3)
}

# 活動字典 (對應 activity_map from 轉檔用.py)
# Keys: 前端選項 (CamelCase, "Journaling" 拼寫已修正)
# Values: 對應的數字字串
events = {
    'Commuting': '0',   # 通勤 (對應 'commuting': 0)
    'Cooking': '1',     # 烹飪 (對應 'cooking': 1)
    'Date': '2',        # 約會 (對應 'date': 2)
    'Exercising': '3',  # 運動 (對應 'exercising': 3)
    'Journaling': '4',  # 寫日誌 (對應 'journaling': 4, 原為 Jornaling)
    'Reflecting': '5',  # 反思 (對應 'reflecting': 5)
    'Relaxing': '6'     # 放鬆 (對應 'relaxing': 6)
}

# --- 數據庫加載 ---
CSV_FILE_PATH = os.path.join(os.path.dirname(__file__), "music_1000_with_links_dict_modify.csv")
try:
    df = pd.read_csv(CSV_FILE_PATH)
    # CSV 中的 'key' 欄位是整數，用於索引
    songs_db = df.set_index('key')['titles-artist-youtube_link'].to_dict()
    print(f"成功從 '{CSV_FILE_PATH}' 加載 {len(songs_db)}條歌曲數據。")
except FileNotFoundError:
    print(f"錯誤：找不到歌曲數據 CSV 檔案 '{CSV_FILE_PATH}'。請確保檔案路徑正確。")
    print("應用程式將以空數據庫模式運行，推薦功能將無法使用。")
    songs_db = {} # 使用空字典，避免後續操作因 songs_db 未定義而出錯
except KeyError as e:
    print(f"錯誤：CSV 檔案 '{CSV_FILE_PATH}' 中缺少必要的欄位 (例如 'key' 或 'titles-artist-youtube_link')：{e}")
    print("應用程式將以空數據庫模式運行，推薦功能將無法使用。")
    songs_db = {}


# --- 輔助函數 ---
def is_valid_input(mood_input, time_input, activity_input):
    """檢查前端傳入的選擇是否在我們定義的字典中都存在"""
    return mood_input in moods and \
           time_input in times and \
           activity_input in events

def get_combined_key(mood_input, time_input, activity_input):
    """根據用戶輸入（字串）從字典中查找對應的數字字串，並組合成 CSV key（整數）"""
    if not is_valid_input(mood_input, time_input, activity_input):
        return None
    try:
        # 從字典獲取對應的數字字串
        mood_num_str = moods[mood_input]
        time_num_str = times[time_input]
        activity_num_str = events[activity_input]
        
        # 組合成鍵字串，例如 "000", "936"
        key_str = mood_num_str + time_num_str + activity_num_str
        return int(key_str) # 轉換為整數，以匹配 songs_db 的鍵類型
    except KeyError as e:
        print(f"錯誤：在字典中找不到鍵 {e}。 mood:'{mood_input}', time:'{time_input}', activity:'{activity_input}'")
        return None
    except ValueError as e:
        print(f"錯誤：無法將組成的鍵字串 '{key_str}' 轉換為整數：{e}")
        return None

def has_songs_for_key(combined_key_int):
    """檢查此整數鍵是否存在於歌曲數據庫中"""
    if combined_key_int is None:
        return False
    return combined_key_int in songs_db

def get_song_details_for_key(combined_key_int):
    """
    根據整數鍵從數據庫獲取歌曲的詳細資訊列表。
    每首歌的資訊包含 "title" (歌名 - 藝術家) 和 "url" (原始 YouTube 連結)。
    注意：此函數依賴於 CSV 中 'titles-artist-youtube_link' 欄位的格式。
    如果歌名或藝術家本身包含 '-' 分隔符，解析可能會不準確。
    """
    if not has_songs_for_key(combined_key_int):
        return []

    songs_string = songs_db[combined_key_int]  # 例如："歌1-藝1-URL1;歌2-藝2-URL2"
    song_entries = songs_string.split(';')    # 分割成單個歌曲條目
    
    detailed_songs_list = []
    for entry in song_entries:
        parts = entry.split('-', 2) # 最多分割2次，得到 [title, artist, url_part]
                                    # 這樣可以處理 URL 中包含 '-' 的情況
        if len(parts) == 3:
            title_str = parts[0].strip()
            artist_str = parts[1].strip()
            url_str = parts[2].strip() # URL 是分割後的第三部分
            
            detailed_songs_list.append({
                "title": f"{title_str} - {artist_str}", # 組合歌名和藝術家
                "url": url_str
            })
        else:
            # 如果分割結果不符合預期 (例如，缺少 '-' 分隔符)
            print(f"警告：歌曲條目格式不正確，無法解析: '{entry}'。預期格式 '標題-藝術家-連結'。")
            # 可以選擇跳過此條目，或添加一個帶有錯誤提示的條目
            # detailed_songs_list.append({"title": f"格式錯誤: {entry}", "url": ""})
    return detailed_songs_list

# ========== Flask 應用程式 ==========
app = Flask(__name__)

@app.route('/')
def index_route(): # 避免與內建的 index 名稱衝突
    return render_template('index.html')

@app.route('/dicts')
def dicts_route():
    """提供前端下拉選單所需的選項列表"""
    return jsonify({
        'moods': list(moods.keys()),
        'times': list(times.keys()),
        'events': list(events.keys()) # 已在頂部字典修正 "Journaling"
    })

@app.route('/suggest', methods=['POST'])
def suggest_route():
    time.sleep(0.5)
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '請求中未包含有效的 JSON 數據。'}), 400

    mood_input = data.get('mood')
    time_input = data.get('time')
    activity_input = data.get('activity')

    if not (mood_input and time_input and activity_input):
        return jsonify({'success': False, 'message': '請求參數不完整，請確保已選擇所有條件。'}), 400

    # 檢查輸入的有效性 (是否在我們定義的選項內)
    if not is_valid_input(mood_input, time_input, activity_input):
        return jsonify({'success': False, 'message': '輸入的條件包含無效選項，請重新選擇。'}), 400
    
    # 獲取組合鍵
    combined_key = get_combined_key(mood_input, time_input, activity_input)
    if combined_key is None: # 處理 get_combined_key 內部可能發生的錯誤
        return jsonify({'success': False, 'message': '內部錯誤：無法生成查詢鍵值。'}), 500

    # 檢查此組合是否有歌曲
    if not has_songs_for_key(combined_key):
        return jsonify({'success': False, 'message': '抱歉，目前沒有符合此組合的歌單，歡迎稍後再試！'})

    # 獲取歌曲詳細資訊列表
    songs_details = get_song_details_for_key(combined_key)

    if not songs_details: # 理論上如果 has_songs_for_key 為 true，這裡不應為空，除非解析出錯
        print(f"警告：鍵 {combined_key} 存在於 songs_db，但 get_song_details_for_key 返回空列表。")
        return jsonify({'success': False, 'message': '找到了對應的歌曲記錄，但解析歌曲詳細資訊時發生問題。'})
    
    # 構造成功時的訊息
    message_text = f"根據您的選擇，為您推薦 {len(songs_details)} 首歌："
    # 為了讓前端的臨時歌名提取邏輯能工作，可以繼續提供帶數字列表的 message
    # 但前端應優先使用 'songs' 陣列
    song_list_for_message = "\n".join([f"{i+1}. {song['title']}" for i, song in enumerate(songs_details)])
    full_message_text = message_text + "\n" + song_list_for_message + "\n點擊列表中的歌曲即可播放。"

    return jsonify({
        'success': True,
        'message': full_message_text,
        'songs': songs_details # 結構化的歌曲列表
    })

@app.route('/exit', methods=['POST'])
def exit_route():
    print("接收到關閉伺服器請求...")
    # 在生產環境中，直接關閉伺服器通常不是一個好的做法。
    # Flask 開發伺服器的關閉功能主要用於開發和測試。
    def shutdown_server():
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            print('警告：無法以正常方式關閉伺服器 (可能非 Werkzeug 開發伺服器環境)。')
            # 在這種情況下，我們無法真正停止進程，但可以讓前端知道請求已處理
        else:
            print('伺服器正在關閉...')
            func()
    
    # 在一個新線程中執行關閉，以允許當前請求完成並返回回應
    # 注意：這仍然是針對開發伺服器的行為
    threading.Thread(target=shutdown_server).start()
    return jsonify({'message': '伺服器關閉請求已發送。您可以安全關閉此頁面。'}), 200

if __name__ == '__main__':
    # 監聽所有網絡接口 (0.0.0.0)，方便在局域網內訪問測試
    # debug=True 在生產環境中應設為 False
    app.run(debug=True, host='0.0.0.0', port=5000)
