Run the full blog pipeline for a new article topic.

Usage: /write <topic> [--type how-to|guide|list|comparison] [--auto] [--fg4b "prose"] [--fg4b-file path]

Default mode: pauses after Stage 1 (research brief) for review before continuing.
Use --auto to run all stages without pausing.

Steps:
1. Ensure venv is active: source venv/Scripts/activate
2. Run: python -m app.cli write $ARGUMENTS
3. Show the output
4. In default mode: display the generated brief and ask the user to approve before running /draft
