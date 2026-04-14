"""Pipeline orchestrator — runs stages in sequence or individually."""
from typing import Literal

from rich.console import Console

from app.stages import draft, fg4b_input, images, publish, research

console = Console()

_STAGES: dict[int, tuple[str, callable]] = {
    0: ("fg4b-input", lambda slug, **kw: fg4b_input.run(slug, kw.get("raw_prose", ""))),
    1: ("research", lambda slug, **kw: research.run(slug)),
    2: ("draft", lambda slug, **kw: draft.run(slug)),
    3: ("images", lambda slug, **kw: images.run(slug)),
    4: ("publish", lambda slug, **kw: publish.run(slug)),
}


class Pipeline:
    def __init__(self, slug: str, mode: Literal["auto", "default", "manual"] = "default"):
        self.slug = slug
        self.mode = mode

    def run_stage(self, stage: int, **kwargs) -> None:
        name, fn = _STAGES[stage]
        console.print(f"[bold cyan]Running stage {stage}: {name}[/bold cyan]")
        fn(self.slug, **kwargs)

    def run_from(self, stage: int, **kwargs) -> None:
        for n in range(stage, len(_STAGES)):
            self.run_stage(n, **kwargs)
            if self.mode == "default" and n == 1:
                console.print("\n[yellow]Stage 1 complete. Review the brief above, then run /draft to continue.[/yellow]")
                break
