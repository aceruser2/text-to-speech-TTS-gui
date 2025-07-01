
sudo apt-get install qt6-qpa-plugins libqt6gui6
sudo apt install libxcb-cursor0

# 中文亂碼處理
# 1. 請確認系統與終端機編碼為 UTF-8
# 2. Python 讀寫檔案時加上 encoding="utf-8"
# 3. 若 PyQt6 介面亂碼，請在程式開頭加：
#   import sys
#   import locale
#   locale.setlocale(locale.LC_ALL, '')
#   sys.setdefaultencoding('utf-8')  # Python 3 預設即為 utf-8，通常不需設
# 文字轉語音 GUI 工具 (Text-to-Speech GUI Tool)

這是一個使用 PyQt6 和 Coqui-TTS 製作的圖形化介面工具，可以將中文文字轉換為語音。

## 功能

*   支援直接輸入文字或上傳 `.txt` 文字檔。
*   自動過濾非中文字元與不支援的標點符號。
*   智慧文本切分：
    *   根據句點、問號、驚嘆號等標點符號進行語意切分，確保句子完整性。
    *   自動合併短句，確保每個待處理的文本片段長度足夠 (約 400 字以上)，避免因文本過短導致的 `Kernel size can't be greater than actual input size` 轉譯錯誤。
*   獨立檔案生成：
    *   為每個切分後的文本段落，分別生成對應的 `.txt` 文字檔和 `.wav` 語音檔。
    *   生成的檔案會存放在指定的輸出資料夾中，並分門別類至 `outputs` (語音) 和 `splits` (文本) 子資料夾，方便對照。

## 環境設定

建議使用虛擬環境安裝。

```bash
# 建立虛擬環境
python -m venv venv

# 啟用虛擬環境 (Windows)
.\venv\Scripts\activate
# 啟用虛擬環境 (macOS/Linux)
source venv/bin/activate

# 安裝所需套件
pip install -r requirements.txt
```

## 使用說明

1.  **執行程式**:
    ```bash
    python main.py
    ```

2.  **輸入文字**:
    *   **方法一**: 直接在 "文字內容" 的輸入框中貼上或輸入您想轉換的文字。
    *   **方法二**: 點擊 "上傳文字檔" 按鈕，選擇一個 `.txt` 檔案。程式會自動讀取檔案內容並顯示在輸入框中。

3.  **選擇輸出資料夾**:
    *   點擊 "確認語音儲存資料夾" 按鈕。
    *   在跳出的對話框中，選擇一個您希望儲存語音檔案的資料夾。

4.  **開始轉譯**:
    *   確認文字內容和輸出資料夾都已設定完成後，點擊 "轉譯文字為語音" 按鈕。
    *   程式會開始處理文字並生成語音。處理過程中，介面可能會暫時沒有回應，請耐心等候。

5.  **查看結果**:
    *   轉譯完成後，程式會彈出 "完成" 的提示訊息。
    *   前往您先前選擇的輸出資料夾，您會看到兩個新的子資料夾：
        *   `outputs`: 存放所有生成的 `.wav` 語音檔案。
        *   `splits`: 存放所有切分後的 `.txt` 文字檔。
    *   `outputs` 中的 `output_1.wav` 對應 `splits` 中的 `split_1.txt`，依此類推，方便您核對。

## 注意事項

*   本工具使用的 TTS 模型為 `tts_models/zh-CN/baker/tacotron2-DDC-GST`。
*   程式會自動過濾掉非中文以及除了 `，。！？、；：「」『』（）《》〈〉—…·` 以外的字元。
*   若轉譯過程中發生錯誤，程式會針對該段落彈出錯誤訊息，並繼續處理下一段落。