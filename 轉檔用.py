import os
import pandas as pd
import csv

#把csv檔案中的資料轉為dataframe,以song_id為索引
def csv_to_dataframe(file_path):
    df = pd.read_csv(file_path, index_col="song_id")
    return df

#檔案路徑為"D:\Github\mood_play\music_1000_with_links.csv"
music_df = csv_to_dataframe("D:\Github\mood_play\music_1000_with_links.csv")
print(music_df)

#將dataframe的資料以規則轉換為dict並以mood_map,time_map,activity_map組成的三位數為key

# 定義對應規則
mood_map = {
    'Calm': 0,
    'Cathartic': 1,
    'Comforting': 2,
    'Empowering': 3,
    'Excited': 4,
    'Joyful': 5,
    'Melancholic': 6,
    'Mysterious': 7,
    'Nostalgic': 8,
    'Romantic': 9
}
time_map = {
    'morning': 0,
    'afternoon': 1,
    'evening': 2,
    'night': 3
}
activity_map = {
    'commuting': 0,
    'cooking': 1,
    'date': 2,
    'exercising': 3,
    'journaling': 4,
    'reflecting': 5,
    'relaxing': 6
}

# 以三位數 key 組成新的 dict，值為"titles"+"-"+"artist"+"-"+"youtube_link" 的list
result_dict = {}
for song_id, row in music_df.iterrows():
    mood_num = mood_map.get(str(row['mood']).capitalize(), -1)
    time_num = time_map.get(str(row['time_of_day']).lower(), -1)
    activity_num = activity_map.get(str(row['activity']).lower(), -1)
    key = f"{mood_num}{time_num}{activity_num}"
    if key not in result_dict:
        result_dict[key] = []
    result_dict[key].append(row['title']+"-"+row['artist']+"-"+row['youtube_link'])

print(result_dict)

# 將結果輸出為 csv，每一列為 key, titles
with open(r"D:\Github\mood_play\music_1000_with_links_dict_modify.csv", "w", newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["key", "titles"+"-"+"artist"+"-"+"youtube_link"])
    for key, titles in result_dict.items():
        writer.writerow([key, ";".join(titles)])  # 用分號分隔所有歌名