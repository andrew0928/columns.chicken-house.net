---
applyTo: '_posts/*/*.html'
---
# Convert HTML to Markdown

## Step 1: Define Variables
Define `post_id` as the file name without extension and `year` from the file path.

**Example:** 
- Input: `/_posts/2016/2016-04-29-rancher-on-azure-lab.html`
- `post_id` = `2016-04-29-rancher-on-azure-lab`
- `year` = `2016`
- `publish_date` = `2016-04-29`

## Step 2: Convert Content
1. **Preserve YAML frontmatter** - Keep the YAML header unchanged (between `---` markers)
2. **Convert HTML to Markdown**:
   - Remove all HTML tags (`<p>`, `<div>`, `<span>`, etc.)
   - Convert `<code>` blocks to Markdown code blocks (` ```language `)
   - Convert HTML links `<a href="...">text</a>` to `[text](...)`
   - Convert HTML headings `<h1>`, `<h2>`, etc. to `#`, `##`, etc.
   - Convert HTML lists `<ul>`, `<ol>`, `<li>` to Markdown lists

## Step 3: Handle Images and Links
3. **Skip Local Images**: Do NOT download images already hosted on `columns.chicken-house.net`, 
4. change the image or link path to local path ( just left the path and query part of the URL, e.g. `/wp-content/uploads/2016/04/img_57000bc9912e2.png` )


## Step 4: Output
Create the converted file at the same path as the original HTML file, but with a `.md` extension.

**Example:**
- Input: `/_posts/2016/2016-04-29-rancher-on-azure-lab.html`
- Output: `/_posts/2016/2016-04-29-rancher-on-azure-lab.md`

## Step 5: Validation Checklist
After conversion, verify each image:
- [ ] Alert if any referenced image file is missing from the local directory
- [ ] Report any download failures for external images

## Error Handling
- If external image download fails, report the URL and continue processing
- If conversion encounters malformed HTML, report the issue but continue processing


## Step 6: Confirmation and Commit

- Confirm the conversion is successful, remove origin HTML file.
- Commit the changes to the repository with a message , include convert post_id, and the Validation Checklist.