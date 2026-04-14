Run Stage 2 only: write the article draft from an approved research brief.

Usage: /draft <slug>

Requires: drafts/{slug}/01_brief.json must exist (run /research first).

Steps:
1. Ensure venv is active: source venv/Scripts/activate
2. Run: python -m app.cli draft $ARGUMENTS
3. Show the output and word count of the generated article.md
4. Ask the user if they want to proceed to /images or make edits first
