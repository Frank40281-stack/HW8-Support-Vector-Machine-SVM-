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

st.markdown("""
### How it works:
1. **2D Space (X_1, X_2)**: The red points are clustered in the center, and the blue points surround them. There is no straight line that can separate them in 2D.
2. **Dimension Mapping (Z-axis)**: The SVM model maps the points to 3D. The $Z$ coordinate of each point is its distance score from the boundary computed using the RBF kernel:
   $$Z_i = f(\\mathbf{x}_i) = \\sum_{j \\in \\text{SV}} \\alpha_j y_j K(\\mathbf{x}_j, \\mathbf{x}_i) + b$$
3. **Linear Separation**: The gray plane at $Z = 0$ acts as the **decision hyperplane**. All red points are above this plane ($Z > 0$), and all blue points are below it ($Z < 0$).
4. **Interactive Controls**: You can adjust **Gamma** and **C** in the sidebar. Watch how a larger **Gamma** makes the RBF peak narrower and taller.
""")
