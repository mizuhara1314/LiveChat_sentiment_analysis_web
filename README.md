# 1. 簡介：
  使用之前訓練好的bert_lstm情感模型來實時預測yt跟twitch直播間的觀眾情緒，更新間格為10秒，測試文本在upload的test.txt裡
# 2. 效果：





https://github.com/user-attachments/assets/d0935a80-5d0b-408e-a1d4-b728cdb0f17a





![螢幕擷取畫面 2024-09-11 205640](https://github.com/user-attachments/assets/4cb232b9-9376-4e83-b908-1091bdf1a8f1)
![螢幕擷取畫面 2024-09-11 204945](https://github.com/user-attachments/assets/2e0861aa-fa1d-4f33-8071-ae23e038b065)
![螢幕擷取畫面 2024-09-11 204922](https://github.com/user-attachments/assets/a6bcbbb4-ce5f-4db0-8014-a06d46b358c8)





# 3. 運行項目：

### 注意事項 ###
先至anaconda3\Lib\site-packages\pytchat\core文件夾下的pytchat.py中删除这一部分代码(否則會出現"signal only works in main thread of the main interpreter")

```bash

if interruptable:
    signal.signal(signal.SIGINT, lambda a, b: self.terminate())

```

然後至 https://drive.google.com/file/d/1lnJuSLQKl6Xi-o9SYQ3hwElazgswvjKf/view?usp=sharing 下載模型，並解壓到項目根目錄下讓app.py讀取
然後在工作環境選擇conda interpreter

在 Flask 後端項目下運行後端代碼：

```bash
python app.py  
```
會運行在本機port 7000

或是
```bash
python -m flask run
```

會默認運行在port 5000

然後在瀏覽器開啟localhost即可：
# 4. 缺點：

載入模型功能模塊時無法讀取bert_classfier類(動態連結問題?)，得加個setattr()解決這bug，同時autoPredict函數默認在多線程進行會造成重複獲取數據，需使用互斥鎖

# 5. 改進
未來可以使用像kafka之類的實時流數據框架或者類似c#的sinalR/websocket通訊來取代ajax/axios需要定時輪循達成監聽
