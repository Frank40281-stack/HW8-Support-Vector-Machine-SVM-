import os
import sys
import subprocess

def main():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    FFMPEG_BIN_DIR = os.path.join(BASE_DIR, "ffmpeg", "bin")
    VENV_BIN_DIR = os.path.join(BASE_DIR, ".venv", "Scripts")

    # Add local FFmpeg and virtual env bin directory to PATH
    env = os.environ.copy()
    paths = [FFMPEG_BIN_DIR, VENV_BIN_DIR]
    
    # Filter out directories that don't exist yet, but keep FFMPEG_BIN_DIR for runtime
    existing_paths = [p for p in paths if os.path.exists(p)]
    if FFMPEG_BIN_DIR not in existing_paths:
        existing_paths.append(FFMPEG_BIN_DIR)
        
    env["PATH"] = os.pathsep.join(existing_paths) + os.pathsep + env.get("PATH", "")

    # Python interpreter in virtual environment
    python_exe = os.path.join(VENV_BIN_DIR, "python.exe")
    if not os.path.exists(python_exe):
        print(f"Error: Virtual environment python not found at {python_exe}.")
        print("Please run 'setup_env.py' first to initialize the environment.")
        sys.exit(1)

    # Base arguments for Manim execution
    # Default is low quality render and preview (-pql)
    args = [python_exe, "-m", "manim", "svm_viz.py", "SVM3DVisualization", "-pql"]
    
    # If the user provides command line arguments, override the default
    if len(sys.argv) > 1:
        args = [python_exe, "-m", "manim", "svm_viz.py", "SVM3DVisualization"] + sys.argv[1:]

    print(f"Executing: {' '.join(args)}")
    print(f"FFmpeg path prepended to environment: {FFMPEG_BIN_DIR}")
    
    try:
        subprocess.run(args, env=env, check=True)
    except subprocess.CalledProcessError as e:
        print(f"\nExecution failed with code {e.returncode}")
        sys.exit(e.returncode)

if __name__ == "__main__":
    main()
