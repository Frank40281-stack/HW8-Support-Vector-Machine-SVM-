# Project Development Log: SVM RBF Kernel 3D Visualizer

This log documents all discussions, Q&As, debugging steps, and solutions implemented during the development of the **SVM RBF Kernel 3D Visualization & Interactive Dashboard** project.

---

## 📅 Log Timeline & Execution History

### 1. Environment Configuration & Python 3.14 Compilation Issues
*   **Problem:** The host machine defaulted to Python 3.14.3. When installing requirements (`manim`, `scikit-learn`, `numpy`), `manim`'s dependencies `moderngl` and `glcontext` did not have pre-compiled binary wheels for Python 3.14 on Windows. Pip attempted to build them from source but failed because Microsoft Visual C++ Build Tools were not installed.
*   **Discussion & Q&A:**
    *   *Q:* Can we install the VC++ compilers?
    *   *A:* No, installing compilation tools requires admin privileges and is slow.
    *   *Q:* Is there an alternative?
    *   *A:* Yes. We can download and silently install a local version of Python 3.12.3 (which has full pre-compiled binary wheels for all packages) locally into the workspace, build a virtual environment linked to it, and install everything instantly.
*   **Solution implemented:**
    *   Developed [setup_env.py](file:///d:/%E6%9B%BE%E6%98%B1%E8%AA%A0AI%E4%BD%9C%E6%A5%AD/hw9-0618/setup_env.py) to download `python-3.12.3-amd64.exe` from python.org, install it silently to a local `python312/` directory without requiring admin rights, remove the installer, build `.venv` using the local python 3.12, and download/extract a static build of FFmpeg to `ffmpeg/bin/`.
    *   Created [run_viz.py](file:///d:/%E6%9B%BE%E6%98%B1%E8%AA%A0AI%E4%BD%9C%E6%A5%AD/hw9-0618/run_viz.py) to prepend `ffmpeg/bin/` to `os.environ["PATH"]` dynamically before launching Manim.

---

### 2. Phase 1: SVM Mathematics & Data Serialization
*   **Goal:** Generate concentric 2D circles, train an RBF SVM, and align Z heights with the decision score.
*   **Q&A:**
    *   *Q:* How do we ensure the inner circle rises as a peak while the outer circle remains low?
    *   *A:* By identifying the inner circle class via mean distance from the origin and checking if its average decision function score is positive. If it is negative, we multiply the entire score vector by `-1`. This keeps the decision boundary hyperplane mathematically aligned at $Z = 0$ while visually separating the classes into a mountain and valley.
*   **Solution implemented:**
    *   Created [svm_data.py](file:///d:/%E6%9B%BE%E6%98%B1%E8%AA%A0AI%E4%BD%9C%E6%A5%AD/hw9-0618/svm_data.py) which trains the SVM, exports the coordinates and support vectors to [svm_data.json](file:///d:/%E6%9B%BE%E6%98%B1%E8%AA%A0AI%E4%BD%9C%E6%A5%AD/hw9-0618/svm_data.json), and serializes the classifier to [svm_model.joblib](file:///d:/%E6%9B%BE%E6%98%B1%E8%AA%A0AI%E4%BD%9C%E6%A5%AD/hw9-0618/svm_model.joblib).

---

### 3. Phase 2: Manim 3D Video Rendering Errors
*   **Error A:** `TypeError: Mobject.next_to() got an unexpected keyword argument 'buf'`
    *   *Cause:* The spacing parameter in Manim's positioning API is `buff`, not `buf`.
    *   *Fix:* Replaced `buf` with `buff` in [svm_viz.py](file:///d:/%E6%9B%BE%E6%98%B1%E8%AA%A0AI%E4%BD%9C%E6%A5%AD/hw9-0618/svm_viz.py).
*   **Error B:** `AttributeError: 'ThreeDCamera' object has no attribute 'animate'`
    *   *Cause:* Manim does not allow camera attributes to be animated using the standard `.animate` syntax inside `self.play`.
    *   *Fix:* Replaced the call with `self.move_camera(phi=..., theta=..., added_anims=[...])` which natively supports camera movements in parallel with other animations.

---

### 4. Phase 3: Streamlit App & Deployment Errors
*   **Error A (Streamlit Cloud Build Failure):** `installer returned a non-zero exit code` during dependency processing.
    *   *Cause:* Streamlit Community Cloud (hosted on Linux) read [requirements.txt](file:///d:/%E6%9B%BE%E6%98%B1%E8%AA%A0AI%E4%BD%9C%E6%A5%AD/hw9-0618/requirements.txt) which contained `manim`. Streamlit Cloud failed to build Manim because it lacked Linux system-level dev libraries (LaTeX, Cairo, Pango).
    *   *Fix:* Separated dependencies. Created [requirements-dev.txt](file:///d:/%E6%9B%BE%E6%98%B1%E8%AA%A0AI%E4%BD%9C%E6%A5%AD/hw9-0618/requirements-dev.txt) for `manim` (dev environment). Kept only web dependencies in [requirements.txt](file:///d:/%E6%9B%BE%E6%98%B1%E8%AA%A0AI%E4%BD%9C%E6%A5%AD/hw9-0618/requirements.txt) (`numpy`, `scikit-learn`, `plotly`, `streamlit`). Updated [setup_env.py](file:///d:/%E6%9B%BE%E6%98%B1%E8%AA%A0AI%E4%BD%9C%E6%A5%AD/hw9-0618/setup_env.py) to install both files locally. This bypassed the cloud compiler requirements completely.
*   **Error B (Plotly ValueError):** `Invalid value in colorscale 'coolwarm'`
    *   *Cause:* Plotly surface plots do not support Matplotlib colorscales like `'coolwarm'` out-of-the-box.
    *   *Fix:* Changed the colorscale to Plotly's native `'RdBu'` (Red to Blue) diverging scale in [streamlit_app.py](file:///d:/%E6%9B%BE%E6%98%B1%E8%AA%A0AI%E4%BD%9C%E6%A5%AD/hw9-0618/streamlit_app.py).
*   **Error C (SyntaxError):** `SyntaxError: (unicode error) 'unicodeescape' codec can't decode bytes ...: truncated \xXX escape`
    *   *Cause:* The text contained LaTeX syntax like `\xi` (slack variables) and `\gamma` (parameter name). Because the triple-quoted strings were standard strings (`"""..."""`), the python interpreter parsed `\xi` as `\x` (Unicode hex escape indicator) and crashed.
    *   *Fix:* Prefixed the markdown string blocks with `r` (i.e. `r"""..."""`), converting them to raw string literals.

---

### 5. Video Embedding & Git Integration
*   **Video Embedding:** Copied the rendered Manim mp4 video to the root directory as [demo_animation.mp4](file:///d:/%E6%9B%BE%E6%98%B1%E8%AA%A0AI%E4%BD%9C%E6%A5%AD/hw9-0618/demo_animation.mp4) and added it to the web app using `st.video("demo_animation.mp4")`.
*   **Git User Config Error:** `Author identity unknown` when attempting to commit.
    *   *Fix:* Configured local git settings in the repo only (so it doesn't affect global configs):
        - `git config user.name "Frank40281-stack"`
        - `git config user.email "frank40281@example.com"`
*   **Push & Landing Page:** Pushed the repository to GitHub. Updated [README.md](file:///d:/%E6%9B%BE%E6%98%B1%E8%AA%A0AI%E4%BD%9C%E6%A5%AD/hw9-0618/README.md) to place the deployed Streamlit Cloud URL ([https://n6ayb9qgwndzqt98hxaflr.streamlit.app/](https://n6ayb9qgwndzqt98hxaflr.streamlit.app/)) at the very top.
