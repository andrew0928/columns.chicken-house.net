#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import glob
from pathlib import Path

# 中文到英文的檔名對應表
filename_mapping = {
    "2006-07-21-浩劫重生的-x31.html": "2006-07-21-thinkpad-x31-recovery-story.md",
    "2006-08-16-windows-live-writer.html": "2006-08-16-windows-live-writer.md",
    "2006-09-25-canon-powershot-g7-出現了.html": "2006-09-25-canon-powershot-g7-released.md",
    "2006-09-25-microsoft-windows-xp-media-center-edition-2005.html": "2006-09-25-microsoft-windows-xp-media-center-edition-2005.md",
    "2006-10-26-泛型-singleton-patterns.html": "2006-10-26-generic-singleton-patterns.md",
    "2006-10-27-泛型-singleton-patterns-ii.html": "2006-10-27-generic-singleton-patterns-ii.md",
    "2006-10-28-asp-net-tips-launch-asp-net-web-sites-without-iis-vs2005.html": "2006-10-28-asp-net-tips-launch-asp-net-web-sites-without-iis-vs2005.md",
    "2006-10-29-利用-nunitlite-在-app_code-下寫單元測試.html": "2006-10-29-using-nunitlite-in-app-code-unit-testing.md",
    "2006-10-29-替-app_code-目錄下的-code-寫單元測試.html": "2006-10-29-writing-unit-tests-for-app-code-directory.md",
    "2006-10-31-新硬碟-hitachi-travelstar-5k160.html": "2006-10-31-new-hard-disk-hitachi-travelstar-5k160.md",
    "2006-11-03-canon-digital-camera-相機獨享-記憶卡歸檔工具.html": "2006-11-03-canon-digital-camera-memory-card-archive-tool.md",
    "2006-11-04-canon-digital-camera-記憶卡歸檔工具-raw-support-update.html": "2006-11-04-canon-digital-camera-memory-card-archive-tool-raw-support-update.md",
    "2006-11-04-小紅點缺料-lenovo-sucks.html": "2006-11-04-trackpoint-shortage-lenovo-sucks.md",
    "2006-11-11-css-擋右鍵.html": "2006-11-11-css-disable-right-click.md",
    "2006-11-11-沒網路.html": "2006-11-11-no-internet-connection.md",
    "2006-11-12-ie6-縮放網頁-using-css-htc.html": "2006-11-12-ie6-zoom-webpage-using-css-htc.md",
    "2006-11-15-iq-test.html": "2006-11-15-iq-test.md",
    "2006-11-17-canon-digital-camera-記憶卡歸檔工具-release-notes.html": "2006-11-17-canon-digital-camera-memory-card-archive-tool-release-notes.md",
    "2006-11-18-digital-camera-filer-source-code-update.html": "2006-11-18-digital-camera-filer-source-code-update.md",
    "2006-11-19-ya-community-chicken-house-net-滿兩週年了-d.html": "2006-11-19-ya-community-chicken-house-net-two-years-anniversary.md",
    "2006-12-06-volume-shadow-copy-service.html": "2006-12-06-volume-shadow-copy-service.md",
    "2006-12-10-cs-2-1-sp2-metaweblog-api-newmediaobject-method-support.html": "2006-12-10-cs-2-1-sp2-metaweblog-api-newmediaobject-method-support.md",
    "2006-12-10-又來了.html": "2006-12-10-here-we-go-again.md",
    "2006-12-10-升級失敗-orz.html": "2006-12-10-upgrade-failed-orz.md",
    "2006-12-10-終於升級上來了.html": "2006-12-10-finally-upgraded-successfully.md",
    "2006-12-23-歸檔工具更新-cr2-supported.html": "2006-12-23-archive-tool-update-cr2-supported.md",
    "2006-12-25-background-thread-in-asp-net.html": "2006-12-25-background-thread-in-asp-net.md",
    "2006-12-30-background-thread-in-asp-net-ii.html": "2006-12-30-background-thread-in-asp-net-ii.md"
}

def html_to_markdown(content):
    """Convert basic HTML tags to Markdown"""
    # Convert paragraphs
    content = re.sub(r'<P>(.*?)</P>', r'\1\n', content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r'<p>(.*?)</p>', r'\1\n', content, flags=re.DOTALL | re.IGNORECASE)
    
    # Convert ordered lists
    content = re.sub(r'<OL>(.*?)</OL>', lambda m: convert_ol(m.group(1)), content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r'<ol>(.*?)</ol>', lambda m: convert_ol(m.group(1)), content, flags=re.DOTALL | re.IGNORECASE)
    
    # Convert unordered lists
    content = re.sub(r'<UL>(.*?)</UL>', lambda m: convert_ul(m.group(1)), content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r'<ul>(.*?)</ul>', lambda m: convert_ul(m.group(1)), content, flags=re.DOTALL | re.IGNORECASE)
    
    # Convert links
    content = re.sub(r'<A[^>]*href=["\']([^"\']*)["\'][^>]*>(.*?)</A>', r'[\2](\1)', content, flags=re.IGNORECASE)
    content = re.sub(r'<a[^>]*href=["\']([^"\']*)["\'][^>]*>(.*?)</a>', r'[\2](\1)', content, flags=re.IGNORECASE)
    
    # Convert images
    content = re.sub(r'<IMG[^>]*src=["\']([^"\']*)["\'][^>]*>', r'![](\1)', content, flags=re.IGNORECASE)
    content = re.sub(r'<img[^>]*src=["\']([^"\']*)["\'][^>]*>', r'![](\1)', content, flags=re.IGNORECASE)
    
    # Convert line breaks
    content = re.sub(r'<BR\s*/?>', '\n', content, flags=re.IGNORECASE)
    content = re.sub(r'<br\s*/?>', '\n', content, flags=re.IGNORECASE)
    
    # Remove other HTML tags
    content = re.sub(r'<[^>]+>', '', content)
    
    # Clean up multiple newlines
    content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
    
    return content.strip()

def convert_ol(content):
    items = re.findall(r'<LI>(.*?)</LI>', content, flags=re.DOTALL | re.IGNORECASE)
    if not items:
        items = re.findall(r'<li>(.*?)</li>', content, flags=re.DOTALL | re.IGNORECASE)
    result = ""
    for i, item in enumerate(items, 1):
        result += f"{i}. {item.strip()}\n"
    return result

def convert_ul(content):
    items = re.findall(r'<LI>(.*?)</LI>', content, flags=re.DOTALL | re.IGNORECASE)
    if not items:
        items = re.findall(r'<li>(.*?)</li>', content, flags=re.DOTALL | re.IGNORECASE)
    result = ""
    for item in items:
        result += f"- {item.strip()}\n"
    return result

print("Batch processing script created.")

def process_file(html_file_path, new_filename):
    """Process a single HTML file and convert to Markdown"""
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split frontmatter and content
        parts = content.split('---', 2)
        if len(parts) < 3:
            print(f"Error: No valid frontmatter found in {html_file_path}")
            return False
        
        frontmatter = parts[1]
        html_content = parts[2]
        
        # Update frontmatter - remove permalink, keep redirect_from
        frontmatter_lines = frontmatter.strip().split('\n')
        updated_frontmatter = []
        in_redirect_from = False
        
        for line in frontmatter_lines:
            if line.startswith('permalink:'):
                # Convert permalink to redirect_from entry
                permalink_url = line.split(':', 1)[1].strip().strip('"')
                if not any('redirect_from:' in l for l in updated_frontmatter):
                    updated_frontmatter.append('redirect_from:')
                    in_redirect_from = True
                updated_frontmatter.append(f'  - {permalink_url}')
            elif line.startswith('redirect_from:'):
                updated_frontmatter.append(line)
                in_redirect_from = True
            elif line.startswith('  - ') and in_redirect_from:
                updated_frontmatter.append(line)
            elif line.strip() and not line.startswith(' '):
                in_redirect_from = False
                updated_frontmatter.append(line)
            else:
                updated_frontmatter.append(line)
        
        # Convert HTML content to Markdown
        markdown_content = html_to_markdown(html_content)
        
        # Create new file
        new_file_path = html_file_path.replace('.html', '.md')
        if new_filename:
            dir_path = os.path.dirname(html_file_path)
            new_file_path = os.path.join(dir_path, new_filename)
        
        # Write new markdown file
        with open(new_file_path, 'w', encoding='utf-8') as f:
            f.write('---\n')
            f.write('\n'.join(updated_frontmatter))
            f.write('\n---\n\n')
            f.write(markdown_content)
        
        # Remove original HTML file
        os.remove(html_file_path)
        
        print(f"✅ Converted: {os.path.basename(html_file_path)} → {os.path.basename(new_file_path)}")
        return True
        
    except Exception as e:
        print(f"❌ Error processing {html_file_path}: {str(e)}")
        return False

def main():
    """Main batch processing function"""
    base_dir = "_posts/2006"
    
    # Get all remaining HTML files
    html_files = glob.glob(os.path.join(base_dir, "*.html"))
    
    if not html_files:
        print("No HTML files found to process.")
        return
    
    print(f"Found {len(html_files)} HTML files to process:")
    
    success_count = 0
    for html_file in sorted(html_files):
        filename = os.path.basename(html_file)
        new_filename = filename_mapping.get(filename, filename.replace('.html', '.md'))
        
        print(f"\nProcessing: {filename}")
        if process_file(html_file, new_filename):
            success_count += 1
        
    print(f"\n🎉 Batch processing complete!")
    print(f"✅ Successfully processed: {success_count}/{len(html_files)} files")
    
    if success_count < len(html_files):
        print(f"❌ Failed to process: {len(html_files) - success_count} files")

if __name__ == "__main__":
    main()
