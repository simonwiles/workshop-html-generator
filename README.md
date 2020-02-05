
# Workshop HTML generator
This repo contains code and a template used to generate HTML versions of workshops from the [CIDR workshops repository](https://github.com/sul-cidr/Workshops).  A GitHub Actions workflow on that repo uses the code here to generate/update the published versions when a push is made.

## Possible Enhancements
* add visible "last updated" value
* encode all images as base64?
* Use `<details/>` to allow "spoiler"-style activity "answers".
	- Use https://github.com/javan/details-element-polyfill to support IE and old browsers (and Edge until it moves to blink).
* Consider adding SASS/SCSS support to allow making the CSS source neater.
* Think about local assets that use relative URLs -- right now the advice is to use absolute URLs.  This is probably appropriate anyway, so that the .md files can stand alone as resources, but there might be some pain points here in the future.  
