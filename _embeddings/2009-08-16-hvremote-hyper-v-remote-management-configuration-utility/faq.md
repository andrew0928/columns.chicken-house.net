# HVRemote (Hyper-V Remote Management Configuration Utility)

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 在沒有 Active Directory 環境的情況下，要如何遠端管理 Hyper-V Server？
必須先在 Client 與 Server 端建立相同帳號、開放防火牆中的 WMI 與 DCOM、並為指定帳號設定 WMI 權限等多項安全性設定；若想簡化流程，可以直接使用 HVRemote.wsf 腳本，一次就自動完成所有必要設定。

## Q: HVRemote 是什麼？可以解決什麼問題？
HVRemote.wsf 是由 Microsoft 技術部落格作者 John Howard 釋出的 Script，可自動完成 Hyper-V 遠端管理所需的所有安全性與網路設定，讓「在 Workgroup 中遠端管理 Hyper-V」這件事從「繁複手動步驟」變成「在 Client 與 Server 端各執行一次 Script」即可搞定。

## Q: 在哪裡可以下載 HVRemote 及參考操作文件？
1. 部落格說明與下載：  
   http://blogs.technet.com/jhoward/archive/2008/11/14/configure-hyper-v-remote-management-in-seconds.aspx  
2. MSDN Code Gallery：  
   http://code.msdn.microsoft.com/HVRemote  
3. TechNet 文件：  
   http://technet.microsoft.com/en-us/library/ee256062(WS.10).aspx  
此外，作者亦附上一份完整的 PDF 操作手冊，可依文件步驟快速完成設定。

## Q: 除了 MMC 之外，Hyper-V 是否提供類似 RDP 的一鍵連線工具？
有的，只要安裝 Hyper-V 管理工具後，系統中會出現  
C:\Program Files\Hyper-V\vmconnect.exe  
執行後即可像使用 Remote Desktop Client 一樣，直接驗證並連線至指定虛擬機。  

## Q: HVRemote 使用時需要注意什麼？
HVRemote.wsf 必須在「Client 端」與「Server 端」各執行一次，才能將兩邊的帳號、權限、防火牆及 WMI 等設定同步完成，否則仍可能出現權限不足或連線失敗的情況。