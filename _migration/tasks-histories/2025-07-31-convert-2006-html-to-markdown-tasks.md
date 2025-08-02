## Convert 2006 HTML files to Markdown - 2025-07-31

### Original Requirements
Follow the instructions, convert /_posts/2006/*.html, convert the chinese filename, convert the html content to markdown

### Task Instructions Applied
- basic.instructions.md: File naming conventions, YAML frontmatter, redirect_from handling
- batch.instructions.md: Task tracking and process management

### Files to Process
- [x] 2006-12-25-background-thread-in-asp-net.html (success)
- [x] 2006-12-06-volume-shadow-copy-service.html (success)
- [x] 2006-12-10-cs-2-1-sp2-metaweblog-api-newmediaobject-method-support.html (success)

### Processing Steps for Each File
1. Read current HTML file content
2. Convert Chinese filename elements to English (if any)
3. Convert HTML content to Markdown format
4. Add proper YAML frontmatter
5. Add redirect_from entries for old URLs
6. Save as .md file
7. Delete original .html file
8. Update url-mapping.txt for disqus migration
