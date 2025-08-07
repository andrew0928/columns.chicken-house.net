# 用 WSL + VSCode 重新打造 Linux 開發環境

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 作者為什麼決定把主要開發環境改成「WSL + VS Code」？
為了讓開發、測試和部署都能直接使用原生 Linux 環境，同時又能與 Windows 桌面工具無縫整合。具體誘因包含：
1. 需要在本機 Docker 上跑 AI／CUDA 工作負載，不想再被 Docker Desktop for Windows 綁住授權與效能。
2. 想解決 Windows ↔ Docker Volume IO 嚴重掉速的老問題。
3. 希望建立一組長期可用、以 Linux 為核心但仍可沿用 Windows 工具鏈（VS Code、Git、.NET）的通用工作環境。
4. 借重 Windows 11 24H2 重灌契機，順勢把硬體與軟體環境全面翻新。

## Q: 作者最想一次解決的四大痛點是什麼？
1. 拋開 Docker Desktop for Windows，直接在 Linux（WSL）裡跑 Docker。  
2. 擺脫 Docker 掛 Windows Volume 時的 IO 慢速瓶頸。  
3. 讓 Docker 容器能無痛使用 GPU／CUDA，方便本地跑 LLM、Stable Diffusion 等工作負載。  
4. 打造一個「以 Linux 為本位、又能和 Windows 無縫整合」且低認知負荷的日常工作環境。

## Q: 作者量化 IO 效能後發現哪些驚人差距？
以 4 KiB 隨機讀寫測試 300 秒為例（fio 8 jobs、iodepth 64）：
• Windows App 直存 Windows NTFS：≈ 576 MiB/s（100% 基準）  
• WSL App 存 WSL EXT4（vhdx）：≈ 209 MiB/s（36%）  
• Windows App 存 WSL EXT4（9P+Hyper-V）：≈ 16 MiB/s（≈ 3%）  
• WSL App 存 Windows NTFS（DrvFS）：≈ 38 MiB/s（≈ 6%）  
實務案例中，向量資料庫 Qdrant Volume 放在 Windows NTFS 時 Container 要 38 秒才起來；搬到 WSL rootfs 後只要 1.5 秒，體感快 25 倍。

## Q: 磁碟效能瓶頸最後是怎麼解的？
1. 把所有需要高 IO 的 Docker Volume 改存放在 WSL 的 rootfs（例：`/opt/docker`）。  
2. 在 Windows 端用 `mklink /d` 建符號連結：  
   ```
   mklink /d \\wsl$\ubuntu\opt\docker C:\Codes\docker
   ```  
   讓日常操作仍可用 Windows 檔案總管或 VS Code 開啟同一路徑。  
3. 真正重度場景可再把整顆 SSD 直接以 EXT4 掛載進 WSL，完全省去 vhdx/Hyper-V 開銷。

## Q: 在 VS Code 裡要如何做到「前端在 Windows、所有編輯／編譯都在 Linux」？
1. 安裝 VS Code Remote Development 擴充套件（尤其是「Remote - WSL」）。  
2. 在 WSL 內執行 `code .`，指令稿會自動：  
   • 安裝／更新 VS Code Server 到 WSL  
   • 啟動 Windows 端 VS Code 並自動連回該 Server  
3. 之後 VS Code 左下角會顯示 `WSL: Ubuntu`，檔案對話框、終端機、Git 操作、除錯等都直接作用於 Linux 檔案系統與執行環境，速度與本地相同。

## Q: 要讓 Docker 容器在 WSL 中使用 GPU／CUDA，需要做哪些設定？
1. 在 Windows 裝好對應版本的 NVIDIA 顯示卡 Driver（WDDM 2.9 以上）。  
2. 進入 WSL：  
   ```
   curl -s -L https://nvidia.github.io/libnvidia-container/wsl/dist/nvidia-container-toolkit.list | \
     sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
   sudo apt update && sudo apt install -y nvidia-container-toolkit
   sudo nvidia-ctk runtime configure --runtime=docker
   sudo systemctl restart docker
   ```  
3. 測試 GPU 是否可見：`nvidia-smi`。  
4. 啟動容器時加 `--gpus all`，例如：  
   ```
   docker run -d --gpus all -p 11434:11434 --name ollama ollama/ollama
   ```  
   即可在 Ollama、Stable Diffusion 等容器內直接吃到 RTX 4060 Ti 的 CUDA 算力。

## Q: 作者對這次整體改造的總結或心得是什麼？
• WSL2 + VS Code Remote 已經做到「效能近原生、體驗近單機」；只要磁碟與 Volume 擺對地方，再加一張支援 CUDA 的顯示卡，Windows 桌機就能變身為舒適的 Linux 開發與 AI 推論平台。  
• Hyper-V、9P、DrvFS 這些轉譯層確實會吃掉 IO，最簡單的解法就是「讓重 IO 工作待在 WSL，Windows 只負責 UI」。  
• 微軟十年來一步步把 Windows、Linux、容器、GPU 及雲端生態打通，現在的整合度與生產力超乎預期──只要肯花一天設定，就能得到一個省錢、省心又高效的跨系統開發環境。