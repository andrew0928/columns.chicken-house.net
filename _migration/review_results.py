#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import csv
from urllib.parse import unquote

def decode_chinese_url(url):
    """Decode URL-encoded Chinese characters"""
    try:
        return unquote(url, encoding='utf-8')
    except:
        return url

def has_chinese_encoding(url):
    """Check if URL contains Chinese encoding (%xx%xx pattern)"""
    import re
    return bool(re.search(r'%[0-9A-Fa-f]{2}', url))

def main():
    print("=== CSV 合併結果報告 ===\n")
    
    successful_matches = []
    failed_matches = []
    non_chinese = []
    
    # Read the final CSV file
    with open('mapping_final.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)  # Skip header
        
        for row in reader:
            if len(row) < 2:
                continue
                
            original_url = row[0]
            mapped_url = row[1] if len(row) > 1 else ''
            
            if has_chinese_encoding(original_url):
                if mapped_url.strip():
                    successful_matches.append((original_url, mapped_url))
                else:
                    failed_matches.append(original_url)
            else:
                non_chinese.append(original_url)
    
    print(f"總計處理了 {len(successful_matches) + len(failed_matches) + len(non_chinese)} 筆 URL")
    print(f"- 含中文編碼的 URL: {len(successful_matches) + len(failed_matches)} 筆")
    print(f"- 成功配對: {len(successful_matches)} 筆 ({len(successful_matches)/(len(successful_matches) + len(failed_matches))*100:.1f}%)")
    print(f"- 配對失敗: {len(failed_matches)} 筆")
    print(f"- 不含中文編碼: {len(non_chinese)} 筆")
    
    print(f"\n=== 成功配對的範例 (前20筆) ===")
    for i, (original, mapped) in enumerate(successful_matches[:20], 1):
        decoded = decode_chinese_url(original)
        print(f"{i:2d}. 原始: {decoded}")
        print(f"    配對: {mapped}")
        print()
    
    if len(successful_matches) > 20:
        print(f"... 還有 {len(successful_matches) - 20} 筆成功配對的結果")
    
    print(f"\n=== 配對失敗的範例 (前10筆) ===")
    for i, original in enumerate(failed_matches[:10], 1):
        decoded = decode_chinese_url(original)
        print(f"{i:2d}. {decoded}")
    
    if len(failed_matches) > 10:
        print(f"... 還有 {len(failed_matches) - 10} 筆配對失敗的結果")

if __name__ == "__main__":
    main()
