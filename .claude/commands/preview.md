Copy the published MDX to FG4B_Website and open the Astro dev server with a file watcher.

Usage: /preview <slug>

Requires: FG4B_Website/src/content/blog/{slug}.mdx must exist (run /publish first).

Steps:
1. Ensure venv is active: source venv/Scripts/activate
2. Run: python -m app.cli preview $ARGUMENTS
3. Show the local preview URL (default: http://localhost:4321/blog/{slug})
4. The watcher will sync changes from drafts/{slug}/article.md to FG4B_Website automatically
