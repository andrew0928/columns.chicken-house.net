#!/bin/zsh
# Build synthesis files from artifacts to docs/_synthesis
# Usage: ./build-synthesis.sh [year-pattern]
# Example: ./build-synthesis.sh 2025    # Only 2025 posts
#          ./build-synthesis.sh         # All posts

set -e

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
cd "$SCRIPT_DIR"

PATTERN="${1:-*}"  # Default: all years

echo "Building synthesis files for pattern: ${PATTERN}-*"
echo "============================================"

count=0
for src_dir in artifacts/synthesis/${PATTERN}-*; do
  if [ -d "$src_dir" ]; then
    dir_name=$(basename "$src_dir")
    dest_dir="docs/_synthesis/${dir_name}"
    
    # 建立目標目錄
    mkdir -p "$dest_dir"
    
    # 從 _posts 取得標題
    post_file=$(find docs/_posts -name "${dir_name}.md" 2>/dev/null | head -1)
    if [ -f "$post_file" ]; then
      title=$(grep "^title:" "$post_file" | sed 's/^title: *"//' | sed 's/"$//')
    else
      title="$dir_name"
    fi
    
    # 從 dir_name 解析日期來建立 source_post URL
    year=$(echo "$dir_name" | cut -d'-' -f1)
    month=$(echo "$dir_name" | cut -d'-' -f2)
    day=$(echo "$dir_name" | cut -d'-' -f3)
    slug=$(echo "$dir_name" | cut -d'-' -f4-)
    source_post="/${year}/${month}/${day}/${slug}/"
    
    # 處理每種 synthesis 類型
    for type in summary faq solution; do
      src_file="${src_dir}/${type}.md"
      if [ -f "$src_file" ]; then
        dest_file="${dest_dir}/${type}.md"
        
        # redirect_from URL
        redirect_url="${source_post}${type}/"
        
        # 建立帶 frontmatter 的檔案
        cat > "$dest_file" << EOF
---
layout: synthesis
title: "${title} - ${type}"
synthesis_type: ${type}
source_post: ${source_post}
redirect_from:
  - ${redirect_url}
---

EOF
        cat "$src_file" >> "$dest_file"
        echo "  Created: $dest_file"
        count=$((count + 1))
      fi
    done
  fi
done

echo "============================================"
echo "Total files created: $count"
