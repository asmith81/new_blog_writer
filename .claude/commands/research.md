Run Stage 1 only: generate a keyword strategy brief for an existing draft slug.

Usage: /research <slug>

Steps:
1. Ensure venv is active: source venv/Scripts/activate
2. Run: python -m app.cli research $ARGUMENTS
3. Show the output and the contents of drafts/{slug}/01_brief.json
4. Ask the user to review the brief and confirm before proceeding to /draft
