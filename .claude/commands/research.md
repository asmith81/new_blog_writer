Run Stage 1 only: generate a keyword strategy brief.

Usage: /research

Runs an interview first — prompts for topic, article type, slug, and optional local experience prose.
If prose is provided, Stage 0 (fg4b-input) runs first, then Stage 1.

Steps:
1. Ensure venv is active: source venv/Scripts/activate
2. Run: python -m app.cli research $ARGUMENTS
3. Show the output and the contents of drafts/{slug}/01_brief.json
4. Ask the user to review the brief and confirm before proceeding to /draft
