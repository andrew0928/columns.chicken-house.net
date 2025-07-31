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

def extract_urls_from_line(line):
    """Extract individual URLs from a potentially malformed line"""
    # Split by common URL patterns
    urls = []
    
    # Find all URL patterns starting with https://columns.chicken-house.net/
    url_pattern = r'https://columns\.chicken-house\.net/[^,\s]*[^,\s]'
    matches = re.findall(url_pattern, line)
    
    for match in matches:
        # Clean up the URL - remove trailing commas or other punctuation
        clean_url = re.sub(r'[,\s]+$', '', match)
        if clean_url and clean_url not in urls:
            urls.append(clean_url)
    
    return urls

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
                else:
                    print(f"Warning: Line {line_num} has unexpected format: {line}")
            else:
                print(f"Warning: Line {line_num} missing comma separator: {line}")
    
    print(f"Loaded {len(url_mappings)} URL mappings")
    
    # Read the mapping.csv file (first file)
    results = []
    matched_count = 0
    
    print("Processing mapping.csv...")
    with open('mapping.csv', 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            
            # Extract URLs from the potentially malformed line
            urls = extract_urls_from_line(line)
            
            for url in urls:
                url_normalized = normalize_url_for_comparison(url)
                
                # Check if this URL has Chinese encoding
                if has_chinese_encoding(url):
                    print(f"Processing URL with Chinese encoding: {url}")
                    
                    # Extract date from the URL
                    first_date = extract_date_from_url(url)
                    
                    # Look for matching URL in url_mappings
                    matched_url = None
                    
                    # First try exact match
                    if url_normalized in url_mappings:
                        matched_url = url_mappings[url_normalized]
                        matched_count += 1
                        print(f"  ✓ Exact match found: {matched_url}")
                    else:
                        # Try date-based matching
                        for old_url, new_url in url_mappings.items():
                            old_date = extract_date_from_url(old_url)
                            
                            if dates_are_close(first_date, old_date):
                                # Check if the path structure is similar (ignoring Chinese characters)
                                if has_chinese_encoding(old_url):
                                    matched_url = new_url
                                    matched_count += 1
                                    print(f"  ✓ Date-based match found: {old_url} -> {new_url}")
                                    break
                    
                    if matched_url:
                        results.append([url, matched_url])
                    else:
                        results.append([url, ''])
                        print(f"  ✗ No match found for: {url}")
                else:
                    # No Chinese encoding, just add as is
                    results.append([url, ''])
    
    # Write the results to a new CSV file
    output_file = 'mapping_combined.csv'
    print(f"\nWriting results to {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
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

if __name__ == "__main__":
    main()
