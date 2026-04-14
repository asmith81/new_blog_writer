Run Stage 4 only: assemble the MDX file and deploy to FG4B_Website.

Usage: /publish <slug>

Requires: drafts/{slug}/article.md and 03_images.json must exist.
Writes to: FG4B_Website/src/content/blog/{slug}.mdx

Steps:
1. Ensure venv is active: source venv/Scripts/activate
2. Run: python -m app.cli publish $ARGUMENTS
3. Show the destination path and confirm the file was written
4. Remind the user to run /preview to verify rendering before committing
