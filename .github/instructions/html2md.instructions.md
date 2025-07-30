---
applyTo: '_posts/*/*.html'
---
# Convert HTML to Markdown

define post_id, it is the file name without extension.
ex: /_posts/2016/2016-04-29-rancher-on-azure-lab.html, the post id is ```2016-04-29-rancher-on-azure-lab```, and the publish date is ```2016-04-29```



convert html content to markdown format
keep yaml part, do not change it ( requirement: frontmatter format)

download external images to /wp-content/images/{post_id}/* and update images path to /wp-content/images/{post_id}/*
exclude myself hosted images, do not download them ( *.chicken-house.net)

remove all html tags

convert code blocks ( <code> ) to markdown code blocks ( ```language )

output markdown file to _posts/{year}/{post_id}.md


--
check list:
- [ ] check each image tag, confirm the image is a local file and is in the right folder. if not exist, please alert me.
