# SVM RBF Kernel 3D Visualization & Interactive Dashboard
> **支持向量機 (SVM) 徑向基函數 (RBF) 核技巧 3D 視覺化與互動超平面網頁**

本專案是一個完整且優雅的機器學習教學展示工具，用以呈現 **支持向量機 (SVM) 徑向基函數 (RBF) 核技巧 (Kernel Trick)** 的核心數學邏輯與幾何特點。專案生成一個在 2D 空間中線性不可分的「圓環數據（Concentric Circles）」，並藉由訓練 RBF SVM 模型，計算出每個資料點的決策距離得分（Decision Function Score）作為 3D 的 Z 軸，從而展示資料如何在更高維度中變得線性可分。

---

## 🌟 專案核心特點 (Key Features)

1. **🎬 Manim 3D 演示動畫 (3D Animation Demo)**
   - 使用 Python 數學動畫庫 **Manim** 製作。
   - 動態引導：從 2D 平面點陣展示「無法用直線劃分」的困境，相機漸漸旋轉傾斜，同時將資料點在 Z 軸向上提升（Class 0）與向下降低（Class 1），形成壯麗的「山峰與山谷」幾何形狀。
   - 完美切分：在 $Z=0$ 處置入一個半透明灰色決策超平面（Decision Hyperplane），並將最靠近超平面的**支持向量點 (Support Vectors)** 閃爍高亮為金色。
   
2. **📊 Streamlit 實時互動網頁 (Interactive Web Dashboard)**
   - 搭載動態調參側邊欄：可自由調節 **C (懲罰係數)**、**Gamma ($\gamma$, 核函數係數)** 以及 **Dataset Noise (雜訊強度)**。
   - Plotly 3D 互動圖表：可自由縮放、翻轉 3D 視角，即時繪製出所有的點、高亮的支持向量球體、 $Z=0$ 的平面，以及 **SVM 3D 決策邊界曲面景觀 (Decision Boundary Surface Landscape)**。
   - 整合演示影片：直接在網頁中嵌入了預先渲染完成的 Manim 動畫。

---

## 📂 專案檔案結構 (Project Structure)

```yaml
hw9-0618/
│
├── requirements.txt         # 線上部署/Streamlit網頁的核心依賴 (numpy, scikit-learn, plotly, streamlit)
├── requirements-dev.txt     # 本地開發與Manim影片渲染的依賴 (manim)
├── setup_env.py             # 一鍵環境安裝腳本 (為Windows自動配置 Python 3.12, .venv 與免安裝 FFmpeg 執行檔)
├── run_viz.py               # Manim 動畫運行包裝器 (自動加載本地 FFmpeg 環境變數並運行 Manim)
│
├── svm_data.py              # Phase 1: SVM 模型訓練、數據計算與序列化導出 (.json & .joblib)
├── svm_viz.py               # Phase 2: Manim 3D 動畫場景渲染代碼
├── streamlit_app.py         # Phase 3: Streamlit 互動式 Web App (含數學原理解析)
│
├── svm_data.json            # 產出的結構化圓環數據點與決策高度
├── svm_model.joblib         # 序列化保存的 SVM 訓練模型 (可用於後續加載)
├── demo_animation.mp4       # 預先渲染完成的 1 MB 演示影片 (用於 Streamlit 網頁嵌入)
└── .gitignore               # 排除本地大體積二進位目錄 (.venv, python312, ffmpeg, media/)
```

---

## 🛠️ 本地快速開始 (Quick Start)

專案提供了針對 Windows 環境的自動化一鍵式配置，即使本地沒有安裝編譯工具或 FFmpeg，也能順利運行。

### 1. 初始化虛擬環境與下載 FFmpeg
在專案根目錄下運行環境配置腳本。它會自動下載 Python 3.12、建立 `.venv`、安裝所有 Pip 依賴，並下載靜態 FFmpeg 壓縮包解壓到本地 `ffmpeg/` 目錄下：
```bash
python setup_env.py
```

### 2. 生成 SVM 數據與保存模型
運行數據生成腳本，這會訓練 SVM、生成 `svm_data.json` 並保存訓練好的 `svm_model.joblib` 檔：
```bash
.venv\Scripts\python.exe svm_data.py
```

### 3. 本地渲染 3D 演示動畫 (Manim)
使用專案包裝器加載 FFmpeg 的 PATH 並編譯影片（`-ql` 代表低畫質快速渲染）：
```bash
python run_viz.py -ql
```
*渲染完成的影片將儲存在本地的 `media/` 目錄中，並複製一份到根目錄作為 `demo_animation.mp4`*。

### 4. 啟動互動式網頁 (Streamlit)
在本機啟動 Streamlit Web 伺服器：
```bash
.venv\Scripts\streamlit.exe run streamlit_app.py
```
啟動後，瀏覽器會自動打開本機網址：👉 **[http://127.0.0.1:8501](http://127.0.0.1:8501)** 即可開始進行互動調參！

---

## 🚀 部署至 Streamlit Cloud (Deployment)

本專案已完成相容性優化，可直接一鍵部署至 **Streamlit Community Cloud**：
- **依賴項拆分**：專案將大體積且需要系統級編譯的 `manim` 庫隔離至 `requirements-dev.txt`，而 Streamlit 部署專用的 `requirements.txt` 僅保留了預編譯的二進位包（`numpy`、`scikit-learn`、`plotly`），確保 Streamlit 伺服器不會在構建時發生 exit code 報錯。
- **影片自動嵌入**：部署後，Streamlit 網頁會直接載入根目錄下的 `demo_animation.mp4` 作為演示動畫，無需在雲端運行任何 Manim 渲染。
