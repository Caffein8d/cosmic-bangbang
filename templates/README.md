# Project Page Template

This folder contains a reusable HTML template for creating new project pages that match the visual style of the main site.

## How to Use

1. Copy `project-page-template.html` to the desired location (usually inside `website-creation-and-hosting/`).
2. Rename the file to match your project (e.g. `my-new-project.html`).
3. Update the following sections:
   - `<title>` tag
   - Status badge (color and text)
   - Main heading (`<h1>`)
   - Description paragraph
   - All content sections
4. Add or remove sections as needed while keeping the overall structure and styling consistent.

## Key Features Included

- Cosmic/nebula background (via shared `styles.css`)
- Responsive Tailwind layout
- Consistent navigation
- Card-based content sections
- Status badge styling
- Proper typography and spacing

## Notes

- Always link to `../styles.css` (relative path from inside the main folder).
- Use the same color palette and component styles as the existing pages for visual consistency.
- The template already includes the nebula wallpaper fix using root-relative paths.

## Example Folder Structure

```
website-creation-and-hosting/
├── index.html
├── growth-project.html
├── local-multi-llm-routing/
│   └── index.html
├── templates/
│   ├── README.md
│   └── project-page-template.html
└── styles.css
```