---
layout: post
title: "Memory Management (II) - Test Result"
categories:
- "系列文章: Memory Management"
tags: [".NET","作業系統","技術隨筆"]
published: true
comments: true
permalink: "/2008/03/03/memory-management-ii-test-result/"
redirect_from:
  - /columns/post/2008/03/03/Memory-Management-(II)-Test-Result.aspx/
  - /post/2008/03/03/Memory-Management-(II)-Test-Result.aspx/
  - /post/Memory-Management-(II)-Test-Result.aspx/
  - /columns/2008/03/03/Memory-Management-(II)-Test-Result.aspx/
  - /columns/Memory-Management-(II)-Test-Result.aspx/
  - /columns/post/2008/03/03/Memory-Management-(II)---Test-Result.aspx/
  - /post/2008/03/03/Memory-Management-(II)---Test-Result.aspx/
  - /post/Memory-Management-(II)---Test-Result.aspx/
  - /columns/2008/03/03/Memory-Management-(II)---Test-Result.aspx/
  - /columns/Memory-Management-(II)---Test-Result.aspx/
  - /blogs/chicken/archive/2008/03/03/3019.aspx/
wordpress_postid: 118
---


該來揭曉謎底了，在人氣不怎麼高的地方拋這些冷門的問題，看的我都覺的 "這版主真是不自量力" .. 咳咳.. 為了把之前的心得，在現在的主流作業系統及平台再驗證一次，只好自己花了點小工夫，把 C 挖出來寫個測試程式，不過 C / C++ 實在太久沒寫了，已經忘到連語法都得翻 HELP 的程度 :~ 花了些時間才搞定。

不過也因為這樣，連帶的查了一下如何編譯 x64 的程式碼，還有一些相關的設定項目。這次測試只測了 windows 的環境，沒辦法，這把年紀實在沒力氣再去摸第二種 OS 了，如果有善心人事要幫我測的話，我倒是很樂意把你測的結果一起放上來! 程式碼請看 [<a href="#03">註3</a>]

不多說廢話，測試主要會針對三種環境來測試:

1. 一般的 x86 (win32)
1. 在 x64 下的 32 位元執行環境 (wow64)
1. 原生的 x64 程式

原本還想加上 /3GB options 來測的，不過這樣跟 (2) 幾乎是一樣的，只差在 3GB 跟 4GB 的可用空間而以，差異不大，當然就省下來了 [H]

測試結果就直接抓畫面附在底下了。程式碼當然都是同一份。原始 project 放在 [這裡]。其實這次問題的關鍵，跟 windows / linux，32/64，都沒有直接關係，唯一有關的是，**你的 memory address space 到底有沒有用完**... 怎麼說? 先來看結果:

1. x86 build (run under windows 2003 standard x64):  
![](/wp-content/be-files/WindowsLiveWriter/b924c2e3d4b2_2526/image_11.png)
1. x86 build + /LARGEADDRESSAWARE option (under 2003 x64)  
![](/wp-content/be-files/WindowsLiveWriter/b924c2e3d4b2_2526/image3_1.png)
1. x64 build  
![](/wp-content/be-files/WindowsLiveWriter/b924c2e3d4b2_2526/image6_1.png)

看不出個所以然? 簡單畫個表格整理一下測試結果:

測試環境統一為 Windows 2003 x64 版本，可用記憶體為 2GB，分頁檔有 4GB。

|測試項目|測試 #01|測試 #02|測試 #03|
|--------|-------|-------|--------|
|執行環境|32Bits (WOW64)|32Bits (WOW64)|64Bits (Native)|
|Build Options|x86|x86 + LargeAddressAware|x64|
|可定址空間 / 實際可用空間|2048MB / 1920MB|4096MB / 3904MB|8TB / 4032MB|
|問題的測試結果 / 可以配置的 72mb 區塊|NO / 2|NO / 2|YES / 27|



這結果大概會跌破一堆人的眼鏡，雖然板上回應的很冷清，不過私下 MSN 問了幾個人，有很肯定的，也有不確定的，當然也有亂猜猜的很肯定的 (S＊M，就是你...)，不過答案都很兩極，不是都不行，不然就是都可以...

就理論上來說，分頁的記憶體管理方式，的確是不能解決在 virtual memory address space 過度分散 (fragment) 的問題，如果程式或作業系統沒有作適度的 defrag，那麼你要挖一塊記憶體的要求一定會失敗，但是為什麼測試 #03 會通過? 因為實際可用的 Memory ( Physical RAM + Swap File ) 也不過 6GB，你的程式需索無度，要求超過的怎麼樣也生不出來。6GB 扣掉其它 OS / AP 用掉的，跟理論上能用的 8TB 實在是差太多，造成你的 virtual memory address space 跟本不可能用完。當然 *不可能* 這字眼別用太滿，十年前也是認為 4GB 跟本不可能用完，不過我現在的 PC 就已經裝了 6GB ... [:$] 上表中列了一些較特別的參數，像是明明是 32 位元，怎麼可定址空間是 2048MB ? 還有 LargeAddressAware 是什麼? 這些屬 windows 較特別的規矩，我在文章最後面的 [<a href="#01">註1</a>] 說明一下。

現在的 PC，隨便都是 1GB / 2GB RAM，加上分頁檔，超過 4GB 跟本是件很普通的事，意思是寫不好的程式，的確是已經會面臨到這樣的困境了，明明記憶體還夠用，但是系統卻回報 Out Of Memory ...。只可惜這樣的問題，OS一點忙都幫不上。因為 OS 沒有辦法替你做 Memory Defragment 的動作 [<a href="#02">註2</a>]。[上一篇](/post/Memory-Management---(I)-Fragment-.aspx) 我有畫張記憶體配置的圖，只能用來說明 #01 / #02 的情況，換成 #03 就不大適用了。只要可定址空間夠大，基本上你只需要考慮你配置的記憶體總量有沒有超過可用的記憶體就好，是不大需要在意是不是有 fragment 的問題，除非你的可配置空間跟可用空間很接近，這問題才會浮現出來。就像積木買來，積木的體積跟盒子差不多大，你要全擺進去就得花點工夫安排一下，否則一定會有一些是收不進去的一樣 (幫吳小皮收玩具的感想... -_-)。不過如果你換一個大盒子，或是把整個房間當成大盒子來看，隨便丟都沒問題，連會不會撞在一起都不用耽心，一定不會有空間夠卻放不進去的問題，這就是差別。

這測試結果看起來很可怕，感覺起來只要是 32 位元的程式，加上是 server or services，會長時間運作的，好像都有可能碰到這種問題。這不算是 Memory Leak (因為記憶體是真的有成功的被釋放)，那麼 Java / .NET 宣稱的 Garbage Collection 回收機制到底會不會碰到這個問題? 別耽心，等著看下一篇就知道了 XD



--

註 1. /LARGEADDRESSAWARE:

32 位元系統可定址空間應該是 2^32 = 4GB 沒錯，不過 Microsoft 把它一分為二，規劃一半是給 Kernal，另一半才是給 APP 使用。意思是你的程式再怎麼用只能用到 2GB。不過這種問題幾年前就浮現出來了，Microsoft 特地在 OS 上加了 /3GB 這種參數，可以把 OS : AP = 2GB : 2GB 的規劃，調整為 1GB : 3GB。不過相對的程式在編譯時也要加上 /LARGEADDRESSAWARE 參數，才有可能讓 AP 取得 2GB 以上的記憶體。

所以即使在 x64 下執行的 x86 應用程式，跟本沒有 OS 那 2GB 的需求，一般 x86 APP 在 64 位元作業系統下仍然只能用到 2GB，但是不同參數編譯出來的程式碼，就能用到 4GB (如果是在加上 /3GB 的 x86 OS，則大約是 3GB)



註 2. 為什麼 OS 不能替 Memory 執行 Defragment 的動作?

原因很簡單，測試的程式是用 C / C++ 這類可以直接存取 pointer 的程式語言寫的。試想一下 OS 如果替你把已配置的記憶體區塊挪一挪會發生什麼事? 你拿到的 pointer 全都成了廢物，因為它指向的記憶體，可能已經不是當時你認識的資料了... 因為資料有可能被強迫搬家，你的通訊錄再也沒有用，老朋友就失聯了...

因此，別的程式語言不一定，但是允許你直接使用 pointer 的語言，這類的問題你閃不掉，一定得自己想辦法...



註 3. 測試程式碼

這段 code 我做了點改變，因為 4kb block size 實在太小了 (相對於 4GB 上限)，印出訊息一大堆，執行又慢，因此我自己把問題的參數調整一下，把問題的 4kb 改成 64mb，而最後要配置的 5kb 則改成 72mb。若對這段 code 有興趣的人，可以直接 copy 去用。我直接把 source code 貼在底下 ( C++ 語法忘了一大半 :P，因此用的都是單純的 C ... 除了 conio.h 之外，應該隨便都能成功編譯吧，看誰有興趣可以拿到 Linux 下去試看看....):



```C
#include <stdio.h>
#include <stdlib.h>
#include <conio.h>
#include <malloc.h>

void init_buffer(void *ptr, unsigned int size) {
    if (ptr == NULL) return;

    //for (int count = 0; count < size / sizeof(long); count++) {
    //    ((long *)ptr)[count] = 0;
    //}
}

int main(const int&amp; args) {
    void *buffer1[4096];
    void *buffer2[4096];
    void *buffer3[4096];

    //
    //    allocate
    //
    printf("\n\n");
    printf("1. Allocate 64mb block(s) as more as possible...\n");

    int total = 0;
    for (int count = 0; count < 4096; count++) {
        buffer1[count] = buffer2[count] = NULL;
        buffer1[count] = malloc(64 * 1024 * 1024);

        if (buffer1[count] == NULL) break;
        init_buffer(buffer1[count], 64 * 1024 * 1024);
        printf("#");
        total++;

        buffer2[count] = malloc(64 * 1024 * 1024);

        if (buffer2[count] == NULL) break;
        init_buffer(buffer2[count], 64 * 1024 * 1024);
        printf("#");
        total++;
    }

    printf("\n   Total %d blocks were allocated ( %d MB).\n", total, total * 64);


    //
    //    free
    //
    printf("\n\n");
    printf("2. Free Blocks...\n");

    for (int count = 0; count < 4096; count++) {
        if (buffer2[count] == NULL) break;
        free(buffer2[count]);
        buffer2[count] = NULL;
        total--;
        printf("#");
    }

    printf("\n   Total: %d blocks (%d MB)\n", total, total * 64);
    

    //
    //    allocate
    //
    printf("\n\n");
    printf("3. Allocate 72mb block(s) as more as possible...\n");

    int total2 = 0;
    for (int count = 0; count < 4096; count++) {
        buffer3[count] = malloc(72 * 1024 * 1024);
        if (buffer3[count] == NULL) break;
        printf("#");
        total2++;
    }

    printf("\n   Total: 64mb x %d, 72mb x %d blocks allocated( %d MB).\n", total, total2, total * 64 + total2 * 72);
    printf("\nDump Blocks Address:\n");

    for (int count = 0; count < 4096; count++) {
        if (buffer1[count] == NULL) break;
        printf("  64mb block ponter: [%08p] ~ [%08p] \n", buffer1[count], (long)buffer1[count] + 64 * 1024 * 1024);
    }

    for (int count = 0; count < 4096; count++) {
        if (buffer3[count] == NULL) break;
        printf("  72mb block ponter: [%08p] ~ [%08p] \n", buffer3[count], (long)buffer3[count] + 72 * 1024 * 1024);
    }


    _getch();
    return 0;
}
```