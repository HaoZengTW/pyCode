
// ✅ 全域變數，確保 existingStations 可被所有函式使用
var existingStations = [];

window.onload = function() {
    var stationList = document.getElementById('stationList').children;
    for (var i = 0; i < stationList.length; i++) {
        existingStations.push({
            "station_id": stationList[i].getAttribute('data-station-id'),
            "station_name": stationList[i].getAttribute('data-station') || "未知測站",
            "rainfall_num": stationList[i].getAttribute('data-rainfall') || "0"
        });
    }
    console.log("已載入的 existingStations:", existingStations);  // ✅ 確保 `existingStations` 正確初始化
};

function addStation() {
    var selectElement = document.getElementById('stationSelect');
    var selectedOption = selectElement.options[selectElement.selectedIndex];
    var rainfallAmount = document.getElementById('rainfallAmount').value;

    if (!rainfallAmount) {
        alert("請輸入降雨量");
        return;
    }

    var stationId = selectedOption.value;
    var stationName = selectedOption.getAttribute('data-station-name');

    if (!stationId || stationId === "UNKNOWN_ID") {
        alert("錯誤：測站 ID 無效！");
        return;
    }

    var stationList = document.getElementById('stationList');

    // 檢查是否已經存在於 existingStations（資料庫測站）
    if (existingStations.some(s => s.station_id === stationId)) {
        alert("該測站已經在資料庫中！");
        return;
    }

    // 檢查是否已經存在於前端 stationList
    var displayedStations = stationList.getElementsByClassName('selected-station');
    for (var i = 0; i < displayedStations.length; i++) {
        if (displayedStations[i].getAttribute('data-station-id') === stationId) {
            alert("該測站已經添加！");
            return;
        }
    }

    var newStation = document.createElement('div');
    newStation.classList.add('selected-station');
    newStation.setAttribute('data-station-id', stationId);
    newStation.setAttribute('data-station', stationName);
    newStation.setAttribute('data-rainfall', rainfallAmount);
    newStation.innerHTML = `
        <span>${stationName} - 降雨量: ${rainfallAmount} mm</span>
        <button type="button" class="btn btn-danger btn-sm" onclick="removeStation(this)">移除</button>
    `;

    stationList.appendChild(newStation);
}

function removeStation(button) {
    var stationItem = button.parentElement;
    stationItem.remove();
}


function submitStations() {
    var stationList = document.getElementById('stationList').children;
    var selectedStations = [];

    // ✅ 讀取所有前端選擇的測站，準備傳送到後端
    for (var i = 0; i < stationList.length; i++) {
        var stationId = stationList[i].getAttribute('data-station-id');
        var stationName = stationList[i].getAttribute('data-station');
        var rainfallNum = stationList[i].getAttribute('data-rainfall');

        selectedStations.push({
            "station_id": stationId,
            "station_name": stationName || "未知測站",
            "rainfall_num": rainfallNum || "0"
        });
    }

    // ✅ 發送 AJAX 請求存入資料庫（會先清空，再插入新資料）
    $.ajax({
        url: '/save_selected_stations/',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({'selected_stations': selectedStations}),
        headers: {
            'X-CSRFToken': $('meta[name="csrf-token"]').attr('content')
        },
        success: function (response) {
            alert(response.message);
            location.reload();  // ✅ 成功後刷新頁面，顯示最新數據
        },
        error: function () {
            alert("儲存失敗，請重試！");
        }
    });
}


// 檢查字串是否為浮點數
function isFloat(value) {
    var floatRegex = /^-?\d+(\.\d+)?$/;
    return floatRegex.test(value);
}


// 10/23 upgrade
// 閘門開度表單
function monitor_sheet_insert() {

    var close_date = document.getElementById('close_date').value;
    var close_time = document.getElementById('close_time').value;
    // 组合日期和时间
    var data_time = `${close_date} ${close_time}:00`;
    
    // 创建请求数据对象
    var formData = {
        'valve_close_time': data_time,
        'before_size': document.getElementById('open_size').value,
        'before_flow': document.getElementById('open_flow').value,
        'after_size': document.getElementById('close_size').value,
        'after_flow': document.getElementById('close_flow').value,
    };

    $.ajax({
        url: "/monitor_sheet_insert/",
        type: "POST",
        dataType: "json",
        data: formData,
        success: function (data) {
            alert(data['msg']);
            window.location.replace("/monitor_sheet/");
            console.log(data); // For debugging
        },
        error: function (xhr, status, error) {
            alert("AJAX Error: " + error);
        }
    });
}

// delete record
function deleteRecord(id) {
    if (confirm('確定要刪除此筆資料嗎？')) {
        $.ajax({
            url: '/delete_valve_record/',  // 後端處理刪除的 API
            type: 'POST',  // 使用 POST 方法
            data: { 'id': id },  // 傳遞要刪除的資料 ID
            success: function(data) {
                if (data.status === 'success') {
                    alert(data.msg);
                    // 刪除成功後重新載入頁面
                    location.reload();
                } else {
                    alert(`Error: ${data.msg}`);
                }
            },
            error: function(xhr, status, error) {
                console.error('Error:', error);
                alert('發生錯誤，無法刪除資料');
            }
        });
    }
}

