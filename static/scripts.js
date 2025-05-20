// static/scripts.js
document.addEventListener('DOMContentLoaded', function() {
    // DOM 元素獲取
    const recommendBtn = document.getElementById('recommend-btn');
    const exitBtn = document.getElementById('exit-btn');
    const moodSel = document.getElementById('mood');
    const timeSel = document.getElementById('time');
    const activitySel = document.getElementById('activity');
    const outputBox = document.getElementById('output-box');
    const sidebar = document.getElementById('sidebar');
    const songPlaylist = document.getElementById('song-playlist'); // ul 元素

    // 動態載入下拉選單選項
    fetch('/dicts')
        .then(res => {
            if (!res.ok) {
                console.error("獲取字典 API 回應不正確:", res);
                throw new Error(`HTTP 錯誤！狀態: ${res.status}`);
            }
            return res.json();
        })
        .then(data => {
            if (moodSel) fillSelect(moodSel, data.moods, '請選擇心情');
            if (timeSel) fillSelect(timeSel, data.times, '請選擇時段');
            if (activitySel) fillSelect(activitySel, data.events, '請選擇活動');
        })
        .catch(error => {
            console.error("載入下拉選單失敗:", error);
            if (outputBox) outputBox.value = "無法載入選項，請檢查主控台以獲取更多資訊。";
        });

    function fillSelect(selectElement, items, placeholder) {
        if (!selectElement) {
            console.warn("fillSelect: selectElement 未找到");
            return;
        }
        selectElement.innerHTML = ''; // 清空現有選項
        const placeholderOpt = document.createElement('option');
        placeholderOpt.value = '';
        placeholderOpt.textContent = placeholder;
        selectElement.appendChild(placeholderOpt);

        if (Array.isArray(items)) {
            items.forEach(function(item) {
                const opt = document.createElement('option');
                opt.value = item; // 前端顯示的選項文字
                opt.textContent = item;
                selectElement.appendChild(opt);
            });
        } else {
            console.warn("fillSelect: items 不是一個陣列或未定義:", items);
        }
    }

    // 「推薦」按鈕點擊事件
    if (recommendBtn) {
        recommendBtn.addEventListener('click', function() {
            const mood = moodSel ? moodSel.value : '';
            const time = timeSel ? timeSel.value : '';
            const activity = activitySel ? activitySel.value : '';
            
            if (outputBox) outputBox.value = '歌曲搜尋中，請稍候...'; // 提供即時反饋

            if (!mood || !time || !activity) {
                if (outputBox) outputBox.value = '請先選擇所有條件（心情、時段、活動）。';
                if (sidebar) sidebar.classList.remove('active'); // 確保側邊欄是關閉的
                if (songPlaylist) songPlaylist.innerHTML = ''; // 清空可能存在的舊列表
                // 當條件不完整時，Gemini 按鈕應該是禁用的 (由 MutationObserver 處理)
                return;
            }

            // 清空上一次的 AI 描述 (如果 Gemini 描述框存在)
            const geminiVibeOutput = document.getElementById('gemini-vibe-output');
            if (geminiVibeOutput) {
                geminiVibeOutput.textContent = '';
                geminiVibeOutput.style.display = 'none';
            }

            // --- 修改開始：在發起請求前先關閉側邊欄 ---
            if (sidebar) {
                sidebar.classList.remove('active');
                // 使用 requestAnimationFrame 給予關閉動畫一點時間
                requestAnimationFrame(() => {
                    proceedWithRecommendation();
                });
            } else {
                proceedWithRecommendation();
            }
            // --- 修改結束 ---
            
            fetch('/suggest', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ mood, time, activity })
            })
            .then(res => {
                if (!res.ok) {
                    // 嘗試解析 JSON 格式的錯誤訊息
                    return res.json().then(errData => {
                        console.error("伺服器錯誤回應 (JSON):", errData);
                        throw new Error(errData.message || `伺服器錯誤！狀態: ${res.status}`);
                    }).catch(() => { // 如果錯誤回應不是 JSON
                        console.error("伺服器錯誤回應 (非JSON):", res.status, res.statusText);
                        throw new Error(`伺服器錯誤！狀態: ${res.status}`);
                    });
                }
                return res.json();
            })
            .then(data => {
                console.log("收到推薦數據:", data); // 調試用
                if (data.success && data.songs && data.songs.length > 0) {
                    if (outputBox) outputBox.value = data.message; // 在文字框顯示後端訊息
                    if (sidebar) sidebar.classList.add('active'); // 滑出側邊欄
                    if (songPlaylist) songPlaylist.innerHTML = ''; // 清空舊的播放列表

                    data.songs.forEach((song, index) => {
                        if (!song || typeof song.title !== 'string' || typeof song.url !== 'string') {
                            console.warn(`第 ${index + 1} 首歌曲數據格式不正確，已跳過:`, song);
                            return; // 跳過格式不正確的歌曲數據
                        }

                        const listItem = document.createElement('li');
                        listItem.textContent = song.title; // 使用後端返回的 "歌名 - 藝術家"
                        listItem.dataset.songUrl = song.url; // 存儲原始 URL

                        // --- 修改開始：增強歌曲列表項的點擊事件處理 ---
                        listItem.addEventListener('click', function(event) {
                            console.log('歌曲列表項被點擊:', this.textContent); // 確認事件觸發
                            const urlToOpen = this.dataset.songUrl;
                            console.log('嘗試開啟的 URL:', urlToOpen); // 確認獲取的 URL

                            if (urlToOpen && typeof urlToOpen === 'string' && urlToOpen.trim() !== '') {
                                console.log(`準備在新分頁中開啟 (window.open): ${urlToOpen}`);
                                try {
                                    const newWindow = window.open(urlToOpen, '_blank', 'noopener,noreferrer');
                                    if (newWindow) {
                                        // 新視窗成功開啟或至少嘗試開啟 (某些瀏覽器下，即使被攔截，這裡也可能不是 null)
                                        console.log("window.open 已執行。如果沒有新分頁，請檢查瀏覽器彈出視窗攔截設定。");
                                    } else {
                                        // window.open 明確返回 null，通常意味著被攔截
                                        console.warn("window.open 返回 null，可能被彈出視窗攔截器明確阻擋。");
                                        if(outputBox) outputBox.value += `\n提示：瀏覽器可能已阻擋開啟歌曲連結。請檢查您的彈出視窗設定。`;
                                    }
                                } catch (e) {
                                    console.error("window.open 時發生 JavaScript 錯誤:", e);
                                    if(outputBox) outputBox.value += `\n錯誤：開啟歌曲連結時發生問題 (${e.message})。`;
                                }
                            } else {
                                console.warn("此歌曲沒有有效的 URL (可能是空值、非字串或僅包含空白) 可供開啟:", this.textContent, "URL 數據:", urlToOpen);
                                if(outputBox) outputBox.value += `\n警告：歌曲 "${this.textContent}" 沒有有效的連結可供開啟。`;
                            }
                        });
                        // --- 修改結束 ---
                        if (songPlaylist) songPlaylist.appendChild(listItem);
                    });

                    // --- 修改開始：在填充完列表後再開啟側邊欄 ---
                    if (sidebar) {
                        // 確保在 DOM 更新後再添加 active class，給予渲染機會
                        requestAnimationFrame(() => {
                            sidebar.classList.add('active');
                        });
                    }
                    // --- 修改結束 ---
                    
                    // 自動在新分頁開啟所有推薦歌曲的連結
                    if (data.songs && data.songs.length > 0) {
                        // let openedCount = 0; // 不再需要計數
                        let newTabMessage = "\n歌曲已推薦，您可以點擊列表中的歌曲在新分頁中開啟。"; // 修改提示訊息
                        if (outputBox && !outputBox.value.includes(newTabMessage.trim())) { // 避免重複添加訊息
                             outputBox.value += newTabMessage;
                        }

                        //data.songs.forEach(function(song) {
                        //    if (song.url && typeof song.url === 'string' && song.url.trim() !== '') { // 增加檢查
                                // 為了避免與手動點擊的日誌混淆，這裡的自動開啟可以不加額外日誌，或加不同前綴
                        //        window.open(song.url, '_blank', 'noopener,noreferrer');
                        //        openedCount++;
                        //    }
                        //});
                        //if (outputBox) {
                        //    outputBox.value += `\n已為您嘗試開啟 ${openedCount} 個歌曲連結。請檢查瀏覽器是否阻擋了彈出式視窗。`;
                        //}
                    }
                    // 歌曲列表已填充，Gemini 按鈕的啟用將由 HTML 中的 MutationObserver 處理

                } else {
                    if (outputBox) outputBox.value = data.message || '找不到符合條件的歌曲。';
                    if (sidebar) sidebar.classList.remove('active');
                    if (songPlaylist) songPlaylist.innerHTML = ''; // 清空列表，觸發 MutationObserver 禁用 Gemini 按鈕
                }
            })
            .catch(error => {
                console.error("查詢歌曲失敗:", error);
                if (outputBox) outputBox.value = `查詢歌曲失敗：${error.message} 請檢查主控台。`;
                if (sidebar) sidebar.classList.remove('active');
                if (songPlaylist) songPlaylist.innerHTML = ''; // 清空列表
            });
        });
    }

    // 「結束」按鈕點擊事件
    if (exitBtn) {
        exitBtn.addEventListener('click', function() {
            if (outputBox) outputBox.value = "正在請求關閉伺服器...";
            const geminiVibeBtn = document.getElementById('gemini-vibe-btn'); // 獲取 Gemini 按鈕

            fetch('/exit', { method: 'POST' })
                .then(res => {
                    if (res.ok) {
                        return res.json().then(data => data.message || '伺服器已請求關閉，您可以關閉此頁面。');
                    }
                    throw new Error('關閉伺服器請求失敗。');
                })
                .then(message => {
                    if (outputBox) outputBox.value = message;
                    if (sidebar) sidebar.classList.remove('active');
                    if (songPlaylist) songPlaylist.innerHTML = '';
                    if (recommendBtn) recommendBtn.disabled = true;
                    if (exitBtn) exitBtn.disabled = true;
                    if (geminiVibeBtn) geminiVibeBtn.disabled = true; // 結束時也禁用 Gemini 按鈕

                    // 清空 Gemini 輸出
                    const geminiVibeOutput = document.getElementById('gemini-vibe-output');
                    if (geminiVibeOutput) {
                        geminiVibeOutput.textContent = '';
                        geminiVibeOutput.style.display = 'none';
                    }
                })
                .catch(error => {
                    console.error("結束伺服器失敗:", error);
                    if (outputBox) outputBox.value = `結束伺服器時發生錯誤: ${error.message}`;
                });
        });
    }
});