document.addEventListener('DOMContentLoaded', function() {
    const recommendBtn = document.getElementById('recommend-btn');
    const exitBtn = document.getElementById('exit-btn');
    const moodSel = document.getElementById('mood');
    const timeSel = document.getElementById('time');
    const activitySel = document.getElementById('activity');
    const outputBox = document.getElementById('output-box');

    // 動態載入下拉選單選項
    fetch('/dicts')
        .then(res => res.json())
        .then(data => {
            fillSelect(moodSel, data.moods, '請選擇心情');
            fillSelect(timeSel, data.times, '請選擇時段');
            fillSelect(activitySel, data.events, '請選擇活動');
        });

    function fillSelect(select, arr, placeholder) {
        select.innerHTML = '';
        const opt = document.createElement('option');
        opt.value = '';
        opt.textContent = placeholder;
        select.appendChild(opt);
        arr.forEach(function(item) {
            const o = document.createElement('option');
            o.value = item;
            o.textContent = item;
            select.appendChild(o);
        });
    }

    recommendBtn.onclick = function() {
        const mood = moodSel.value;
        const time = timeSel.value;
        const activity = activitySel.value;
        outputBox.value = '';
        if (!mood || !time || !activity) {
            outputBox.value = '請選擇所有條件';
            return;
        }
        // 發送推薦請求
        fetch('/suggest', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mood, time, activity })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                outputBox.value = data.message;
                // 同時立即在新分頁開啟所有連結
                data.urls.forEach(function(url) {
                    window.open(url, '_blank', 'noopener');
                });
            } else {
                outputBox.value = data.message;
            }
        })
        .catch(() => {
            outputBox.value = '查詢失敗，請稍後再試';
        });
    };

    exitBtn.onclick = function() {
        fetch('/exit', {method: 'POST'})
            .then(() => {
                outputBox.value = '伺服器已結束，請關閉本頁面';
            });
    };
});
