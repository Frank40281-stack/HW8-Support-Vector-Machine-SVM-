import os
import sys
import subprocess
import urllib.request
import zipfile
import shutil

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON_LOCAL_DIR = os.path.join(BASE_DIR, "python312")
PYTHON_INSTALLER_PATH = os.path.join(BASE_DIR, "python_installer.exe")
VENV_DIR = os.path.join(BASE_DIR, ".venv")
FFMPEG_DIR = os.path.join(BASE_DIR, "ffmpeg")
FFMPEG_BIN_DIR = os.path.join(FFMPEG_DIR, "bin")
FFMPEG_ZIP = os.path.join(BASE_DIR, "ffmpeg.zip")

def download_file(url, target_path, label):
    print(f"Downloading {label}...")
    def progress_hook(count, block_size, total_size):
        if total_size > 0:
            percent = min(100, int(count * block_size * 100 / total_size))
            sys.stdout.write(f"\rProgress: {percent}%")
        else:
            sys.stdout.write(f"\rProgress: {count * block_size} bytes downloaded")
        sys.stdout.flush()

    opener = urllib.request.build_opener()
    opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
    urllib.request.install_opener(opener)
    urllib.request.urlretrieve(url, target_path, progress_hook)
    print("\nDownload complete.")

def main():
    # 1. Install local Python 3.12 if not already present
    local_python_exe = os.path.join(PYTHON_LOCAL_DIR, "python.exe")
    if not os.path.exists(local_python_exe):
        print("Python 3.12 not found locally. Installing local Python 3.12 to prevent compiler issues...")
        python_url = "https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe"
        try:
            download_file(python_url, PYTHON_INSTALLER_PATH, "Python 3.12 Installer")
            print("Installing Python 3.12 silently (this may take a minute)...")
            cmd = [
                PYTHON_INSTALLER_PATH,
                "/quiet",
                "InstallAllUsers=0",
                "PrependPath=0",
                f"TargetDir={PYTHON_LOCAL_DIR}",
                "Include_launcher=0",
                "InstallLauncherAllUsers=0",
                "Include_test=0"
            ]
            subprocess.run(cmd, check=True)
            if os.path.exists(local_python_exe):
                print(f"Local Python 3.12 successfully installed at: {PYTHON_LOCAL_DIR}")
            else:
                raise Exception("Installer finished but python.exe was not found in TargetDir.")
        except Exception as e:
            print(f"Failed to install local Python 3.12: {e}")
            sys.exit(1)
        finally:
            if os.path.exists(PYTHON_INSTALLER_PATH):
                os.remove(PYTHON_INSTALLER_PATH)
    else:
        print(f"Local Python 3.12 already installed at: {PYTHON_LOCAL_DIR}")

    # 2. Create Virtual Environment using local Python 3.12
    if os.path.exists(VENV_DIR):
        print("Removing existing old virtual environment...")
        try:
            shutil.rmtree(VENV_DIR)
        except Exception as e:
            print(f"Warning: Could not remove old .venv folder automatically: {e}")
            print("Trying to overwrite inside it...")
            
    print("Creating virtual environment linked to Python 3.12...")
    subprocess.run([local_python_exe, "-m", "venv", VENV_DIR], check=True)

    # Determine venv pip and python
    python_exe = os.path.join(VENV_DIR, "Scripts", "python.exe")

    # 3. Install dependencies inside the virtual environment
    print("Installing Python dependencies inside virtual environment (using pre-built wheels)...")
    subprocess.run([python_exe, "-m", "pip", "install", "--upgrade", "pip"], check=True)
    subprocess.run([python_exe, "-m", "pip", "install", "-r", os.path.join(BASE_DIR, "requirements.txt")], check=True)
    subprocess.run([python_exe, "-m", "pip", "install", "-r", os.path.join(BASE_DIR, "requirements-dev.txt")], check=True)

    # 4. Setup FFmpeg
    ffmpeg_exe = os.path.join(FFMPEG_BIN_DIR, "ffmpeg.exe")
    if not os.path.exists(ffmpeg_exe):
        print("FFmpeg not found locally. Downloading FFmpeg Essentials...")
        url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        try:
            download_file(url, FFMPEG_ZIP, "FFmpeg Essentials")
            print("Extracting FFmpeg binaries...")
            os.makedirs(FFMPEG_BIN_DIR, exist_ok=True)
            with zipfile.ZipFile(FFMPEG_ZIP, 'r') as zip_ref:
                for file_info in zip_ref.infolist():
                    filename = os.path.basename(file_info.filename)
                    if filename in ["ffmpeg.exe", "ffplay.exe", "ffprobe.exe"]:
                        print(f"Extracting {filename}...")
                        with zip_ref.open(file_info) as source, open(os.path.join(FFMPEG_BIN_DIR, filename), "wb") as target:
                            shutil.copyfileobj(source, target)
            print("FFmpeg binaries successfully extracted to:", FFMPEG_BIN_DIR)
        except Exception as e:
            print(f"Error downloading/extracting FFmpeg: {e}")
            print("Trying fallback URL...")
            fallback_url = "https://github.com/GyanD/codexffmpeg/releases/download/7.1/ffmpeg-7.1-essentials_build.zip"
            try:
                download_file(fallback_url, FFMPEG_ZIP, "FFmpeg Fallback")
                print("Extracting FFmpeg binaries from fallback...")
                os.makedirs(FFMPEG_BIN_DIR, exist_ok=True)
                with zipfile.ZipFile(FFMPEG_ZIP, 'r') as zip_ref:
                    for file_info in zip_ref.infolist():
                        filename = os.path.basename(file_info.filename)
                        if filename in ["ffmpeg.exe", "ffplay.exe", "ffprobe.exe"]:
                            print(f"Extracting {filename}...")
                            with zip_ref.open(file_info) as source, open(os.path.join(FFMPEG_BIN_DIR, filename), "wb") as target:
                                shutil.copyfileobj(source, target)
                print("FFmpeg binaries successfully extracted to:", FFMPEG_BIN_DIR)
            except Exception as fe:
                print(f"Fallback failed as well: {fe}")
                sys.exit(1)
        finally:
            if os.path.exists(FFMPEG_ZIP):
                os.remove(FFMPEG_ZIP)
    else:
        print("FFmpeg is already configured at:", FFMPEG_BIN_DIR)

    print("\nSetup environment completed successfully!")

if __name__ == "__main__":
    main()
