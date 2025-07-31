#!/usr/bin/env python3
import os
import re
import yaml
from pathlib import Path

def extract_frontmatter(content):
    """提取 YAML frontmatter"""
    if not content.startswith('---'):
        return {}, content
    
    try:
        # 找到第二個 ---
        end_marker = content.find('---', 3)
        if end_marker == -1:
            return {}, content
        
        frontmatter_str = content[3:end_marker].strip()
        body = content[end_marker + 3:].strip()
        
        # 解析 YAML
        frontmatter = yaml.safe_load(frontmatter_str) if frontmatter_str else {}
        return frontmatter, body
    except Exception as e:
        print(f"Error parsing YAML: {e}")
        return {}, content

def filename_to_url(filename):
    """從檔名轉換為現在的網址格式"""
    # 移除 .md 副檔名
    name = filename.replace('.md', '')
    
    # 解析日期和標題
    # 格式: yyyy-mm-dd-title
    match = re.match(r'(\d{4})-(\d{2})-(\d{2})-(.+)', name)
    if match:
        year, month, day, title = match.groups()
        return f"/{year}/{month}/{day}/{title}/"
    
    return None

def process_markdown_files(base_path, years):
    """處理指定年份的 markdown 檔案"""
    url_mappings = []
    
    for year in years:
        year_path = Path(base_path) / "_posts" / str(year)
        if not year_path.exists():
            print(f"Directory {year_path} does not exist")
            continue
            
        # 找到所有 .md 檔案
        md_files = list(year_path.glob("*.md"))
        print(f"Processing {len(md_files)} files in {year}")
        
        for md_file in md_files:
            try:
                # 讀取檔案內容
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 提取 frontmatter
                frontmatter, body = extract_frontmatter(content)
                
                # 從檔名產生現在的網址
                current_url = filename_to_url(md_file.name)
                if not current_url:
                    print(f"Cannot parse filename: {md_file.name}")
                    continue
                
                # 找到 redirect_from 中以 /yyyy 開頭的路徑
                redirect_from = frontmatter.get('redirect_from', [])
                if isinstance(redirect_from, str):
                    redirect_from = [redirect_from]
                
                # 篩選以 /yyyy 開頭的原始網址
                for redirect_url in redirect_from:
                    if re.match(r'^/\d{4}/', redirect_url):
                        url_mappings.append((redirect_url, current_url))
                        print(f"Found mapping: {redirect_url} -> {current_url}")
                        
            except Exception as e:
                print(f"Error processing {md_file}: {e}")
                continue
    
    return url_mappings

def main():
    base_path = Path(__file__).parent
    years = [2004, 2005, 2006]
    
    print("Generating URL mapping from redirect_from data...")
    print("=" * 60)
    
    # 處理檔案
    url_mappings = process_markdown_files(base_path, years)
    
    # 輸出到 url-mapping.txt
    output_file = base_path / "url-mapping.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        for original_url, current_url in url_mappings:
            f.write(f"{original_url}, {current_url}\n")
    
    print("=" * 60)
    print(f"Generated {len(url_mappings)} URL mappings")
    print(f"Output saved to: {output_file}")
    
    # 顯示前幾筆作為範例
    print("\nFirst 10 mappings:")
    for i, (original_url, current_url) in enumerate(url_mappings[:10]):
        print(f"{i+1:2d}. {original_url} -> {current_url}")

if __name__ == "__main__":
    main()
