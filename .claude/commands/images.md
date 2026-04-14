Run Stage 3 only: generate images with DALL-E and upload to Cloudinary.

Usage: /images <slug>

Requires: drafts/{slug}/article.md must exist (run /draft first).

Steps:
1. Ensure venv is active: source venv/Scripts/activate
2. Run: python -m app.cli images $ARGUMENTS
3. Show the Cloudinary URLs for each generated image
4. Ask the user to review images and confirm before running /publish
