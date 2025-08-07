```markdown
# 用 WSL + VS Code 重新打造 Linux 開發環境 – 問題 / 解決方案匯整

# 問題／解決方案 (Problem/Solution)

## Problem: Windows 上 Docker Volume I/O 速度慢到不可用  

**Problem**:  
在 Windows 上以 Docker Desktop 執行需要大量隨機 I/O 的容器 (例：向量資料庫 Qdrant、Jekyll 部落格建置) 時，  
• Qdrant 已匯入 4 萬筆資料後啟動要 1 分鐘  
• Jekyll build 一篇文章要 110 秒  
嚴重拖慢開發與測試流程。  

**Root Cause**:  
1. Windows container 透過 `-v C:\path:/container/path` 掛載 volume 時，I/O 會走  
   Windows App → DrvFS(9P) → WSL Kernel → ext4.vhdx → SSD  
2. DrvFS 與 Hyper-V 虛擬磁碟層層轉譯，隨機 4K Benchmark 只有原生 NTFS 的 3 %–6 % 效能 (16 MiB/s vs 576 MiB/s)。  
3. NTFS ↔ EXT4 權限 / inotify 無法對應，檔案監聽改成 polling 也進一步拖慢 build。  

**Solution**:  
1. 把所有高 I/O volume 搬進 WSL 原生檔案系統 (EXT4)。範例路徑  
   ```bash
   # 在 WSL 內
   sudo mkdir -p /opt/docker/qdrant_data
   ```  
2. 以 mklink 把該目錄映射回 Windows，保留原有工作流：  
   ```powershell
   mklink /d \\wsl$\Ubuntu\opt\docker  C:\CodeWork\docker
   ```  
3. 若 I/O 更苛刻，直接把獨立 SSD/Partition 以 EXT4 掛入 WSL：  
   ```powershell
   # Windows 管理員
   wsl --mount \\.\PHYSICALDRIVE3 --bare
   # WSL 內格式化並掛載
   sudo mkfs.ext4 /dev/sdc1
   sudo mount /dev/sdc1 /opt/docker
   ```  
4. Docker Compose 只引用 WSL 內路徑，不再經過 DrvFS：  
   ```yaml
   volumes:
     qdrant-data:
       driver: local
       driver_opts:
         type: none
         device: /opt/docker/qdrant_data
         o: bind
   ```

**Cases 1 – Qdrant**  
• 路徑在 `/mnt/c/...` 時啟動 38.376 s → 移到 `/opt/docker/...` 後 1.499 s (25× 加速)。  

**Cases 2 – fio Benchmark**  
• Windows→Windows 576 MiB/s (基準)  
• Windows→WSL 16 MiB/s (2.8 %)  
• WSL→WSL(EXT4) 209 MiB/s (36 %)  
• WSL→實體 EXT4 SSD 780 MiB/s (120 % of baseline)  

**Cases 3 – Jekyll**  
• build 靜態站台 110 s → 6 s (約 18× 改善)。  



## Problem: 跨 OS 開發時 VS Code / 檔案監聽失效，體驗破碎  

**Problem**:  
• 在 Windows 上用 VS Code 編輯，容器在 Linux 端 rebuild；  
• DrvFS 無法傳遞 inotify，Live-Reload 失效、需人工重啟；  
• 任何 `git pull && jekyll serve` 都極慢且易錯。  

**Root Cause**:  
1. VS Code 執行於 Windows，對檔案採 NTFS 路徑；  
2. Linux 端容器需 Polling 才能偵測變更，I/O ×2 放大；  
3. 不同 OS 上的 path / exec format 轉換增加開銷與心智負擔。  

**Solution**: VS Code Remote Development – WSL  
1. 安裝 VS Code Remote – WSL extension (`ms-vscode-remote.remote-wsl`)  
2. 在 WSL 內直接執行 `code .`，script 會：  
   • 自動部署/升級 `vscode-server` 至 WSL EXT4  
   • 啟動本機 VS Code UI，透過隧道連線到 WSL  
3. 所有 IntelliSense / build / debug 發生在 WSL，UI 仍在 Windows，  
   inotify、檔案權限、路徑完全原生。  
4. VS Code Terminal 預設就是 Bash；`docker compose up`、`dotnet build` 直接在 Linux 跑，速度與行為與雲端一致。  

**Cases 1 – GitHub Pages**  
• VS Code Remote 後，Jekyll Live-Reload 能即時偵測檔案變更；  
• build 由 110 s → 6 s；預覽可直接以 VS Code Port Forward 開啟。  

**Cases 2 – 多人協作**  
• 新人只需 clone repo + `code .` 即擁有一致 Linux Toolchain；  
• 不需再安裝 Ruby、Python、GCC 等本機依賴，降低 On-Board 時間。  



## Problem: 在 Docker 內使用 GPU / CUDA 麻煩，LLM 難以落地  

**Problem**:  
• Windows 裝 CUDA 相依性複雜；  
• GPU 難以 pass-through 至容器；  
• 想在本機流暢執行 Ollama / Stable-Diffusion 等模型。  

**Root Cause**:  
1. Windows 與 Linux 驅動版本、CUDA Toolkit 相容矩陣繁雜；  
2. 傳統 Hyper-V 無 GPU Virtualization，需安裝 2 份 Driver；  
3. Docker Desktop 在 Windows 尚未完整支援 `--gpus`。  

**Solution**: WSL2 GPU 虛擬化 + NVIDIA Container Toolkit  
步驟：  
```powershell
# 1. Windows 安裝 565.xx 以上 WDDM 2.9+ NVIDIA Driver
# 2. WSL 端安裝 NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/libnvidia-container/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt update && sudo apt install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
# 3. 確認 GPU 可用
nvidia-smi
# 4. 執行 Ollama
docker run -d --gpus all -p 11434:11434 -v ollama:/root/.ollama --name ollama ollama/ollama
```  

**為何可行**  
• WSL2 內建 `/dev/dxg` GPU Virtual Device；  
• Host Driver 處理真正硬體，WSL 只需微型 dxgkrnl。  
• NVIDIA-CTK 將 `nvidia-container-runtime` hook 轉向 `/dev/dxg`。  

**Cases 1 – Llama3 Inference**  
• 問答延遲 << 1 sec，RTX 4060 Ti 16G GPU 使用率可見；  
• 同一台機器即可再用 `docker compose` 併行 Open-WebUI 前端。  

**Cases 2 – 後續擴充**  
• vLLM、Stable-Diffusion、Whisper-cpp 均只需加 `--gpus all` 即可搬到容器；  
• 減少手動安裝 CUDA/Python 版本衝突時間 (原需數小時 → 幾分鐘)。  
```


## Problem: Docker Desktop 授權與資源佔用過重  

**Problem**:  
Docker Desktop 商業授權費、背景服務佔記憶體與 CPU；  
開發者實際只需要核心 docker engine + CLI。  

**Root Cause**:  
Docker Desktop 附帶 GUI、K8s、VPNKit 與大量 Windows Service。  

**Solution**:  
1. 直接在 WSL 發行版 (`Ubuntu 24.04`) 安裝 `docker-ce`：  
   ```bash
   curl -fsSL https://get.docker.com | sh
   sudo usermod -aG docker $USER
   ```  
2. 於 Windows Terminal 設定預設啟動 profile = WSL；  
3. 若需 Windows PowerShell 操作 Docker，可透過 `docker.exe` CLI  
   (Docker 安裝程式已在 `%ProgramFiles%\Docker\Docker\resources\bin` 投放)。  

**Cases**:  
• 移除 Docker Desktop 後，系統常駐 RAM 使用量 -500 MB，背景服務從 10+ 條降至 0。  



```