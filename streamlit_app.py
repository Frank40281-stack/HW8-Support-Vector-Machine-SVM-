import streamlit as st
import numpy as np
from sklearn.datasets import make_circles
from sklearn.svm import SVC
import plotly.graph_objects as go

st.set_page_config(page_title="SVM RBF Kernel 3D Interactive Visualizer", layout="wide")

st.title("Interactive SVM RBF Kernel 3D Visualization")
st.write("""
This interactive tool visualizes how the **Support Vector Machine (SVM) Radial Basis Function (RBF) Kernel** maps 
a 2D linearly inseparable dataset (concentric circles) into a higher-dimensional 3D space, making it linearly separable.
""")

# Sidebar controls
st.sidebar.header("SVM Hyperparameters")
c_val = st.sidebar.slider("Regularization Parameter (C)", min_value=0.1, max_value=10.0, value=1.0, step=0.1)
gamma_val = st.sidebar.slider("RBF Kernel Coefficient (Gamma)", min_value=0.1, max_value=5.0, value=1.0, step=0.1)
noise_val = st.sidebar.slider("Dataset Noise", min_value=0.0, max_value=0.3, value=0.08, step=0.01)

# Generate data
X, y = make_circles(n_samples=100, noise=noise_val, factor=0.5, random_state=42)

# Train SVM
clf = SVC(kernel='rbf', C=c_val, gamma=gamma_val)
clf.fit(X, y)

# Z score calculations
distances = np.linalg.norm(X, axis=1)
mean_dist_0 = np.mean(distances[y == 0])
mean_dist_1 = np.mean(distances[y == 1])
inner_class = 0 if mean_dist_0 < mean_dist_1 else 1

scores = clf.decision_function(X)
# Ensure inner class goes up
inner_scores = scores[y == inner_class]
sign = 1
if np.mean(inner_scores) < 0:
    scores = -scores
    sign = -1

# Identify support vectors
sv_indices = clf.support_

# Create 3D Scatter Plot
fig = go.Figure()

# Plot Class 0 (Inner Circle)
c0_mask = y == 0
fig.add_trace(go.Scatter3d(
    x=X[c0_mask, 0],
    y=X[c0_mask, 1],
    z=scores[c0_mask],
    mode='markers',
    name='Class 0 (Inner)',
    marker=dict(
        size=5,
        color='#FF4D4D', # Coral Red
        opacity=0.8
    )
))

# Plot Class 1 (Outer Circle)
c1_mask = y == 1
fig.add_trace(go.Scatter3d(
    x=X[c1_mask, 0],
    y=X[c1_mask, 1],
    z=scores[c1_mask],
    mode='markers',
    name='Class 1 (Outer)',
    marker=dict(
        size=5,
        color='#3399FF', # Dodger Blue
        opacity=0.8
    )
))

# Plot Support Vectors (highlighted)
fig.add_trace(go.Scatter3d(
    x=X[sv_indices, 0],
    y=X[sv_indices, 1],
    z=scores[sv_indices],
    mode='markers',
    name='Support Vectors',
    marker=dict(
        size=8,
        color='#FFD700', # Gold
        symbol='circle-open',
        line=dict(color='#FFD700', width=4),
        opacity=0.9
    )
))

# Plot Decision Hyperplane (Z = 0)
x_grid = np.linspace(-1.5, 1.5, 10)
y_grid = np.linspace(-1.5, 1.5, 10)
X_grid, Y_grid = np.meshgrid(x_grid, y_grid)
Z_grid = np.zeros_like(X_grid)

fig.add_trace(go.Surface(
    x=X_grid,
    y=Y_grid,
    z=Z_grid,
    colorscale=[[0, 'rgba(128,128,128,0.35)'], [1, 'rgba(128,128,128,0.35)']],
    showscale=False,
    name='Hyperplane (Z=0)',
    hoverinfo='skip'
))

# Plot the full decision boundary surface
# The decision boundary surface is z = f(x, y)
x_dense = np.linspace(-1.5, 1.5, 45)
y_dense = np.linspace(-1.5, 1.5, 45)
X_dense, Y_dense = np.meshgrid(x_dense, y_dense)
grid_points = np.c_[X_dense.ravel(), Y_dense.ravel()]
Z_dense = clf.decision_function(grid_points) * sign
Z_dense = Z_dense.reshape(X_dense.shape)

fig.add_trace(go.Surface(
    x=X_dense,
    y=Y_dense,
    z=Z_dense,
    colorscale='RdBu',
    opacity=0.45,
    showscale=True,
    colorbar=dict(title="Decision Score", thickness=15),
    name='Decision Boundary Landscape'
))

# Customize Layout
fig.update_layout(
    title=f"SVM Decision Boundary Landscape (Gamma={gamma_val}, C={c_val})",
    scene=dict(
        xaxis=dict(title='X_1', range=[-1.8, 1.8]),
        yaxis=dict(title='X_2', range=[-1.8, 1.8]),
        zaxis=dict(title='Z (Decision Score)'),
        camera=dict(
            eye=dict(x=1.4, y=1.4, z=1.1)
        )
    ),
    margin=dict(l=0, r=0, b=0, t=40),
    width=900,
    height=650
)

st.plotly_chart(fig, use_container_width=True)

# 3D Animation Video Demo
st.subheader("Manim 3D Dimension Transition Video")
st.write("This video shows the transition animation from 2D space to 3D space, demonstrating how the hyperplane separates the classes:")
st.video("demo_animation.mp4")

st.markdown("---")
st.header("📚 支持向量機 (SVM) 核心理論與機制詳解")

st.markdown("""
> 💡 **核心思想**：「不僅要分得對，還要分得夠開（留有最大的安全邊緣）。」
""")

# Use columns for core concepts
col1, col2, col3 = st.columns(3)
with col1:
    st.info("""
    ### 📄 超平面 (Hyperplane)
    在二維空間中是一條**線**，三維空間中是一個**面**，而在更高的維度中，這個用來切分資料的邊界就稱為**超平面**。若特徵是 $N$ 維，超平面就是一個 $N-1$ 維的子空間。
    """)
with col2:
    st.warning("""
    ### 📐 邊緣 (Margin)
    超平面到距離它最近的資料點之間的**幾何距離**。SVM 的終極目標就是找到一個最佳超平面，使得這個邊緣達到**最大化**（Maximized Margin），以獲得更好的泛化能力。
    """)
with col3:
    st.success("""
    ### 🎯 支持向量 (Support Vectors)
    躺在邊緣邊界上的**關鍵資料點**。超平面的位置和方向完全由這些支持向量決定。若移動其他點，超平面不變；但若移動支持向量，超平面將隨之改變！
    """)

st.markdown(r"""
### 2. ⚖️ 線性可分與硬邊緣 (Hard Margin)
若一組資料非常完美，可以用一條直線（或超平面）毫無錯誤地將兩類分開，這叫做**線性可分（Linearly Separable）**。
在這種理想狀況下，SVM 會採用**硬邊緣（Hard Margin）**策略：
- 嚴格不允許任何錯分點。
- **缺點**：如果資料中帶有雜訊（Noise）或異常值（Outliers），硬邊緣會導致模型無法找到解，或者變得非常容易**過擬合（Overfitting）**。

### 3. ⚙️ 線性不可分與軟邊緣 (Soft Margin)
現實世界中的資料通常充滿雜訊，很少有完美線性可分的情況。此時如果堅持不准出錯，模型反而會失去泛化能力。因此，SVM 引入了**軟邊緣（Soft Margin）**與**鬆弛變數（Slack Variables, $\xi$）**：
- 允許部分資料點被錯分，或者落在邊緣邊界之內。
- 透過超參數 **$C$（懲罰係數）** 來平衡「邊緣最大化」與「減少錯分點」之間的矛盾：
  - **大 $C$**：對錯誤的容忍度低。模型會拼命想把所有點分對，導致邊緣變窄，容易過擬合。
  - **小 $C$**：對錯誤的容忍度高。模型允許更多點出錯，以換取更大的邊緣，增加泛化能力，但可能欠擬合。

### 4. 🔮 點石成金的「核技巧」（Kernel Trick）
當資料在原本的低維空間中，無論怎麼畫線都無法分開（例如：藍色點在外圈包圍著內圈的紅色點），該怎麼辦？SVM 祭出了最強大的武器：**核技巧（Kernel Trick）**。
- **原理**：透過一個非線性映射，將低維空間中線性不可分的資料，投射到高維度空間。在那個高維度空間裡，原本混在一起的資料就會變得「線性可分」。
- **為什麼叫「技巧」**：如果直接把資料轉到高維度計算，計算量會呈指數級爆炸（維度災難）。核技巧的厲害之處在於，它**不需要真的把點算出來投射過去**，而是直接利用**「核函數」**在低維空間計算出高維空間中的內積，極大地節省了計算資源。

#### 🧬 常見的核函數 (Kernel Functions)：
- **線性核 (Linear Kernel)**：不進行高維轉換，適用於資料本身就線性可分，或特徵維度已經非常高（如文字分類）。
- **多項式核 (Polynomial Kernel)**：透過特徵的多項式組合來建立邊界。
- **高斯核 / 徑向基函數 (RBF Kernel)**：最常用、最強大的核。它將資料映射到**無限維的空間**，幾乎可以處理任何複雜的非線性邊界（本專案即採用此核）。
- **Sigmoid 核**：類似於神經網路的雙曲正切激勵函數。
""")

st.markdown("### 5. ⚖️ SVM 的優缺點分析")
col_adv, col_dis = st.columns(2)
with col_adv:
    st.success("""
    #### ✅ 優點
    * **理論完美、泛化能力強**：基於結構風險最小化，調好 $C$ 的情況下不容易過擬合。
    * **抓住關鍵**：決策超平面只由少數「支持向量」決定，對遠離邊界的異常值不敏感。
    * **高維有效**：即使特徵維度比樣本數還要多（例如基因數據、文本特徵），SVM 依然表現優異。
    * **核函數靈活**：可以透過更換不同的核函數來捕捉各種複雜的非線性關係。
    """)
with col_dis:
    st.error("""
    #### ❌ 缺點
    * **運作慢、耗記憶體**：當樣本量 $N$ 非常大時，計算兩兩之間的距離會導致計算複雜度呈二次或三次方增長（$O(N^2)$ 或 $O(N^3)$），非常吃資源。
    * **對參數敏感**：核函數的選擇、高斯核的 $\gamma$ 參數以及懲罰係數 $C$ 的選擇對結果影響巨大，需要花時間進行網格搜索（Grid Search）調參。
    * **黑盒子傾向**：由於使用了高維映射，很難直觀地解釋「為什麼這個特徵重要」。
    * **無法直接導出機率**：SVM 預測的是類別，而不是「屬於該類的機率是多少」（需使用額外轉換如 Platt scaling）。
    """)

st.markdown("""
### 6. 🎯 總結與應用場景
SVM 是一個**「重質不重量」**的演算法。它非常適合用在**特徵很多、但樣本量中等**（通常在幾萬筆以內）的精準分類場景。
* 📝 **典型應用**：文本分類（如垃圾郵件偵測）、圖像識別（如人臉識別）、生物資訊學（如基因蛋白分類與癌症預測）。
""")
