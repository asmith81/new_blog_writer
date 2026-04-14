Upload a local image to Cloudinary and insert a BlogImage component into the article.

Usage: /add-image <slug> <image_path> --after "<heading text>"

Example: /add-image my-article-slug ./photos/crew.jpg --after "Our Installation Process"

Steps:
1. Ensure venv is active: source venv/Scripts/activate
2. Run: python -m app.cli add-image $ARGUMENTS
3. Show the Cloudinary URL and confirm the BlogImage component was inserted
4. Remind the user to run /publish again if the article has already been published
