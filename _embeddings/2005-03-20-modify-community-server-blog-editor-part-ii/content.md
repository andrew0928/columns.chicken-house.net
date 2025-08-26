![Community Server Editor Part 2](/images/2005-03-20-modify-community-server-blog-editor-part-ii/cs_editor_part2.jpg)

花了點時間研究 CommunityServer 1.0 的 source code, 發現三位作者的架構設計的相當漂亮, 上一篇提到的 TextEditor Wrapper, 就是用 Provider Pattern 的樣式設計出來的. 整套系統很多地方都用到 Provider Pattern, 包括安全機制 ( membership, roles, auth... etc) 也都採用一樣的作法, 未來可以很簡單的寫另一套 Provider, 然後只要改一下 configuration, 馬上就整個切換到新的 Provider.

這次我先拿 TextEditorWrapper 下手, 繼承下來後把我想要的東西都加上去, 然後在 communityserver.config 裡頭把我自己寫的 Wrapper 掛上去, 哇哈哈, 我上一篇說沒辦法改的東西都改好了 ![emotion](/images/2005-03-20-modify-community-server-blog-editor-part-ii/emotion-11.gif), 不但把表情符號都加到 Toolbar 裡, 同時原有 FreeTextBox 的一些進階功能也打開了. 雖然會用到的還是那幾個, 不過用起來爽度就是不一樣 ![emotion](/images/2005-03-20-modify-community-server-blog-editor-part-ii/emotion-2.gif)

下次再來改別的地方試試看..