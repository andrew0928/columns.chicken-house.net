#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import csv
from urllib.parse import unquote
from datetime import datetime, timedelta

def extract_date_from_url(url):
    """Extract date (year, month, day) from URL"""
    match = re.search(r'/(\d{4})/(\d{1,2})/(\d{1,2})/', url)
    if match:
        year, month, day = match.groups()
        return (int(year), int(month), int(day))
    return None

def has_chinese_encoding(url):
    """Check if URL contains Chinese encoding (%xx%xx pattern)"""
    return bool(re.search(r'%[0-9A-Fa-f]{2}', url))

def dates_are_close(date1, date2, max_days=5):
    """Check if two dates are within max_days of each other"""
    if not date1 or not date2:
        return False
    
    try:
        dt1 = datetime(date1[0], date1[1], date1[2])
        dt2 = datetime(date2[0], date2[1], date2[2])
        return abs((dt1 - dt2).days) <= max_days
    except ValueError:
        return False

def normalize_url_for_comparison(url):
    """Remove trailing slash and normalize URL for comparison"""
    return url.rstrip('/')

def decode_chinese_url(url):
    """Decode URL-encoded Chinese characters"""
    try:
        return unquote(url, encoding='utf-8')
    except:
        return url

def find_best_match(target_url, url_mappings):
    """Find the best match for a target URL in the mappings"""
    target_normalized = normalize_url_for_comparison(target_url)
    target_date = extract_date_from_url(target_url)
    
    # Try exact match first
    if target_normalized in url_mappings:
        return url_mappings[target_normalized]
    
    # Try date-based matching with URL decoding
    target_decoded = decode_chinese_url(target_url)
    
    best_match = None
    best_score = 0
    
    for old_url, new_url in url_mappings.items():
        old_date = extract_date_from_url(old_url)
        
        # Check date proximity
        if dates_are_close(target_date, old_date, max_days=5):
            old_decoded = decode_chinese_url(old_url)
            
            # Calculate similarity score based on URL path structure
            score = 0
            
            # Same date gets high score
            if target_date == old_date:
                score += 50
            elif dates_are_close(target_date, old_date, max_days=1):
                score += 30
            elif dates_are_close(target_date, old_date, max_days=3):
                score += 20
            else:
                score += 10
                
            # Similar path structure
            target_path = target_decoded.split('/')[-1].lower()
            old_path = old_decoded.split('/')[-1].lower()
            
            # Remove common prefixes/suffixes for comparison
            target_clean = re.sub(r'[^a-z0-9\u4e00-\u9fff]', '', target_path)
            old_clean = re.sub(r'[^a-z0-9\u4e00-\u9fff]', '', old_path)
            
            # Check for common words or characters
            if target_clean and old_clean:
                if target_clean == old_clean:
                    score += 40
                elif target_clean in old_clean or old_clean in target_clean:
                    score += 20
            
            if score > best_score:
                best_score = score
                best_match = new_url
    
    # Only return match if score is high enough
    if best_score >= 30:
        return best_match
    
    return None

def extract_individual_urls(text):
    """Extract individual URLs from potentially concatenated text"""
    # Find all complete URL patterns
    pattern = r'https://columns\.chicken-house\.net/\d{4}/\d{1,2}/\d{1,2}/[^,\s]*'
    urls = re.findall(pattern, text)
    
    cleaned_urls = []
    for url in urls:
        # Remove trailing punctuation and clean up
        clean_url = re.sub(r'[,\s]+$', '', url)
        if clean_url and len(clean_url) > 40:  # Minimum reasonable URL length
            cleaned_urls.append(clean_url)
    
    return cleaned_urls

def main():
    # Read the url-mapping.txt file (second file)
    url_mappings = {}
    
    print("Reading url-mapping.txt...")
    with open('url-mapping.txt', 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
                
            if ', ' in line:
                parts = line.split(', ', 1)
                if len(parts) == 2:
                    old_url, new_url = parts
                    old_url = normalize_url_for_comparison(old_url)
                    new_url = normalize_url_for_comparison(new_url)
                    url_mappings[old_url] = new_url
    
    print(f"Loaded {len(url_mappings)} URL mappings")
    
    # Read the mapping.csv file and process it properly
    results = []
    matched_count = 0
    processed_urls = set()  # To avoid duplicates
    
    print("Processing mapping.csv...")
    with open('mapping.csv', 'r', encoding='utf-8') as f:
        content = f.read()
        
        # Extract all individual URLs from the entire content
        all_urls = extract_individual_urls(content)
        
        print(f"Found {len(all_urls)} URLs to process...")
        
        for url in all_urls:
            if url in processed_urls:
                continue
            processed_urls.add(url)
            
            # Check if this URL has Chinese encoding
            if has_chinese_encoding(url):
                decoded_url = decode_chinese_url(url)
                print(f"Processing: {decoded_url[:80]}...")
                
                # Look for matching URL in url_mappings
                matched_url = find_best_match(url, url_mappings)
                
                if matched_url:
                    results.append([url, matched_url])
                    matched_count += 1
                    print(f"  ✓ Match found: {matched_url}")
                else:
                    results.append([url, ''])
                    print(f"  ✗ No match found")
            else:
                # No Chinese encoding, just add as is
                results.append([url, ''])
    
    # Write the results to a new CSV file with proper formatting
    output_file = 'mapping_final.csv'
    print(f"\nWriting results to {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['Original URL', 'Mapped URL'])  # Header
        for row in results:
            writer.writerow(row)
    
    print(f"✓ Complete! Matched {matched_count} URLs out of {len(results)} total entries")
    print(f"Results saved to: {output_file}")
    
    # Show some statistics
    chinese_urls = sum(1 for row in results if has_chinese_encoding(row[0]))
    matched_chinese_urls = sum(1 for row in results if has_chinese_encoding(row[0]) and row[1])
    
    print(f"\nStatistics:")
    print(f"- Total URLs: {len(results)}")
    print(f"- URLs with Chinese encoding: {chinese_urls}")
    print(f"- Matched Chinese URLs: {matched_chinese_urls}")
    print(f"- Match rate: {matched_chinese_urls/chinese_urls*100:.1f}%" if chinese_urls > 0 else "- Match rate: N/A")
    
    # Show some sample matches
    print(f"\nSample successful matches:")
    count = 0
    for row in results:
        if has_chinese_encoding(row[0]) and row[1]:
            decoded = decode_chinese_url(row[0])
            print(f"  {decoded} -> {row[1]}")
            count += 1
            if count >= 5:
                break

if __name__ == "__main__":
    main()
