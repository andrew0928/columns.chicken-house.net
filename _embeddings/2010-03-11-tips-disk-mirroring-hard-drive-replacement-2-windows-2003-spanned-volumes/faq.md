# [Tips] 用磁碟鏡像更換硬碟 #2 ─ Windows 2003 的跨距磁區

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 在 Windows Server 2003 中，「延伸磁區 (extend volume)」與 Windows Vista/Server 2008 之後的「extend volume」有什麼差別？
在 Windows Server 2003 裡的延伸磁區功能可以把兩顆硬碟 (或兩個分割區) 併成一個磁區來使用，屬於 JBOD (Just a Bunch Of Disks) 的概念；而從 Vista／Server 2008 開始，extend volume 只會把同一顆硬碟、同一個分割區後面的可用空間直接納進來，不再跨碟。若要跨多顆硬碟，則改用「span disk」。

## Q: 若要在 Windows Server 2003 利用磁碟鏡像 (Mirror) 來更換硬碟，需要哪些主要步驟？
1. 將舊硬碟 (例如磁碟1) 與新硬碟 (例如磁碟2) 建立鏡像。  
2. 等待重新同步 (Resync) 完成。  
3. 移除鏡像，使新硬碟獨立。  
4. 使用 2003 的「延伸磁區」功能，把新硬碟剩餘的空間併進原先的分割區 (如 D:)。

## Q: 為何作者認為 Vista/Server 2008 內建的 extend/shrink volume 很實用？
過去若要調整分割區大小，必須依賴像 Partition Magic 這類第三方軟體，操作時常讓人擔心資料損毀。Vista/Server 2008 起內建 extend 與 shrink volume，可直接安全地調大或縮小分割區，省去額外工具與風險。

## Q: 在 Windows Vista／Server 2008 的「span disk」最多可把幾顆硬碟併成一個磁區？
最多可以把 32 顆硬碟合併為一個磁區。

## Q: Windows Server 2003 的可跨碟延伸磁區最接近哪種磁碟架構模式？
它的概念與 JBOD (Just a Bunch Of Disks) 相似，能將多顆不同容量的硬碟拼接成單一邏輯磁區。