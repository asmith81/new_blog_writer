Run the full blog pipeline for a new article topic.

Usage: /write [--auto]

Runs an interview first — prompts for topic, article type, slug, and optional local experience prose.
Use --auto to run all stages without pausing.

Steps:
1. Ensure venv is active: source venv/Scripts/activate
2. Run: python -m app.cli write $ARGUMENTS
3. Show the output
4. In default mode: display the generated brief and ask the user to approve before running /draft
