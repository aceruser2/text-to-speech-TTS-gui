import os
import sys
import locale

locale.setlocale(locale.LC_ALL, "")

import sys
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QTextEdit,
    QFileDialog,
    QMessageBox,
    QLabel,
)
import os
import re
import jieba

# TTS
import torch
from TTS.utils.radam import RAdam
from collections import defaultdict

torch.serialization.add_safe_globals([RAdam, defaultdict, dict])  # 允許 TTS 的 RAdam
from TTS.api import TTS

device = "cuda" if torch.cuda.is_available() else "cpu"


class TextToSpeechApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Text to Speech GUI")
        self.resize(500, 400)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.text_edit = QTextEdit()
        self.layout.addWidget(QLabel("文字內容："))
        self.layout.addWidget(self.text_edit)

        self.upload_btn = QPushButton("上傳文字檔")
        self.upload_btn.clicked.connect(self.upload_text_file)
        self.layout.addWidget(self.upload_btn)

        self.confirm_btn = QPushButton("確認語音儲存資料夾")
        self.confirm_btn.clicked.connect(self.select_output_folder)
        self.layout.addWidget(self.confirm_btn)

        self.translate_btn = QPushButton("轉譯文字為語音")
        self.translate_btn.clicked.connect(self.text_to_speech)
        self.layout.addWidget(self.translate_btn)

        self.output_folder = None
        self.tts = TTS(
            model_name="tts_models/zh-CN/baker/tacotron2-DDC-GST",
            progress_bar=False,
        ).to(device)

    def upload_text_file(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Text Files (*.txt)")
        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            if file_paths:
                file_path = file_paths[0]
                with open(file_path, "r", encoding="utf-8") as f:
                    self.text_edit.setPlainText(f.read())

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "選擇語音儲存資料夾")
        if folder:
            self.output_folder = folder
            QMessageBox.information(self, "資料夾已選擇", f"語音將儲存於：\n{folder}")

    def text_to_speech(self):
        text = self.text_edit.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "錯誤", "請先輸入或上傳文字。")
            return
        if not self.output_folder:
            QMessageBox.warning(self, "錯誤", "請先確認語音儲存資料夾。")
            return
        # 僅保留中文與常用標點
        filtered_text = re.sub(
            r"[^\u4e00-\u9fff，。！？、；：「」『』（）《》〈〉—…·]", "", text
        )
        if filtered_text != text:
            QMessageBox.information(self, "提示", "已自動過濾非中文或不支援字元。")

        # 切分資料夾
        split_dir = os.path.join(self.output_folder, "splits")
        os.makedirs(split_dir, exist_ok=True)

        # 輸出音檔資料夾
        outputs_dir = os.path.join(self.output_folder, "outputs")
        os.makedirs(outputs_dir, exist_ok=True)

        # 以標點切分句子，保留標點
        sentences = re.split(r"([。！？])", filtered_text)
        segments = []
        for i in range(0, len(sentences) - 1, 2):
            seg = sentences[i] + sentences[i + 1]
            if seg.strip():
                segments.append(seg)
        if len(sentences) % 2 != 0 and sentences[-1].strip():
            segments.append(sentences[-1])

        # 合併片段，讓每段至少400~500字
        merged_segments = []
        buffer = ""
        for seg in segments:
            if len(buffer) + len(seg) < 400:
                buffer += seg
            else:
                if buffer:
                    merged_segments.append(buffer)
                buffer = seg
        if buffer:
            merged_segments.append(buffer)

        # 逐段生成文本與語音
        import soundfile as sf

        for idx, seg in enumerate(merged_segments, 1):
            split_txt_path = os.path.join(split_dir, f"split_{idx}.txt")
            with open(split_txt_path, "w", encoding="utf-8") as f:
                f.write(seg)
            output_wav_path = os.path.join(outputs_dir, f"output_{idx}.wav")
            try:
                wav = self.tts.tts(seg)
                sf.write(output_wav_path, wav, self.tts.synthesizer.output_sample_rate)
            except Exception as e:
                QMessageBox.critical(self, "錯誤", f"第{idx}段語音轉譯失敗：{e}")
                continue
        QMessageBox.information(
            self, "完成", f"已切分並生成 {len(merged_segments)} 段語音與文本。"
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TextToSpeechApp()
    window.show()
    sys.exit(app.exec())


