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
        print("輸入有誤,請重新輸入。")
        return False
    else:
        # 將輸入轉成代碼
        int_1 = int(str(moods[n1])+ str(times[n2])+ str(events[n3]))
        print(type(int_1))
        print(int_1)

        # 顯示推薦歌單
        if int_1 in songs_db:
            return True
        else:
            print("\n很抱歉,目前尚未有符合此組合的歌單,歡迎日後再來看看！")
            return False

def suggest(n1,n2,n3):
    int_1 = int(str(moods[n1])+ str(times[n2])+ str(events[n3]))
    print(type(int_1))
    print(int_1)
    print("\n根據你的選擇,為你推薦以下歌單：")
    list_1 = songs_db[int_1].split(";")
    list_inner_all = []
    for i in range(len(list_1)):
        list_inner  = list_1[i].split("-")
        print(list_inner[0]+"-"+list_inner[1])
        list_inner_all.append(list_inner[2])
    return list_inner_all
    
while True:
    n1,n2,n3 = input_user()
    if check_input(n1,n2,n3) == True:
        suggest(n1,n2,n3)
    
