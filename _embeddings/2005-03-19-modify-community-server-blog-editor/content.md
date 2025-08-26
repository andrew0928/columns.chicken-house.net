![Community Server Editor](/images/2005-03-19-modify-community-server-blog-editor/cs_editor.jpg)

好像每次換一套 blog, 我的宿命就是先改 editor, 讓它可以貼圖及貼表情符號... 哈哈 ![emotion](/images/2005-03-19-modify-community-server-blog-editor/emotion-2.gif)

CommunityServer 用的是之前我介紹過的 FreeTextBox, 還不難改, 但是討厭的是 CS 並不是直接內嵌 FTB, 而是  
中間多擋了一層 CS 自己的 Editor Wrapper... ![emotion](/images/2005-03-19-modify-community-server-blog-editor/emotion-8.gif), 然後 CS 提供的 source code 就是少了這一塊...

沒辦法, 所以改出來的東西就有點格格不入, 多的工具列得排在畫面上方, 沒辦法加到原本 FTB 自己的工具列.  
不然 FTB 其實還有很多好用的工具列可以打開... 真是可惜..