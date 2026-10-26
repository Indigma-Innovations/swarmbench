"""MkDocs hook: render the agent catalog from ``swarmbench.catalog`` into the docs.

A page that contains ``<!-- swarmbench:catalog -->`` gets the roster table,
``<!-- swarmbench:references -->`` the reference points and held-out opponents
and ``<!-- swarmbench:cli-help -->`` the output of ``swarmbench --help``, so the
documentation never drifts from the code.
"""

def _table(specs, numbered: bool) -> str:
    head = "| # | Key | Name | Family | Realistic | Idea |" if numbered else \
        "| Key | Name | Realistic | Idea |"
    rule = "|---:|---|---|---|---|---|" if numbered else "|---|---|---|---|"
    lines = [head, rule]
    for i, spec in enumerate(specs, start=1):
        realistic = "yes" if spec.realistic else "no"
        idea = spec.description
        if spec.falls_back_to:
            idea += f" *Plays exactly as `{spec.falls_back_to}` when no rival is a supplied bot.*"
        if numbered:
            lines.append(f"| {i} | `{spec.key}` | {spec.name} | {spec.family} | {realistic} | {idea} |")
        else:
            lines.append(f"| `{spec.key}` | {spec.name} | {realistic} | {idea} |")
    return "\n".join(lines)


def _cli_help() -> str:
    import contextlib
    import io
    import os

    from swarmbench import cli

    buffer = io.StringIO()
    os.environ["COLUMNS"] = "100"
    with contextlib.redirect_stdout(buffer), contextlib.suppress(SystemExit):
        cli.main(["--help"])
    return "```text\n" + buffer.getvalue().rstrip() + "\n```"


def on_page_markdown(markdown: str, page, config, files) -> str:
    if "<!-- swarmbench:" not in markdown:
        return markdown
    import swarmbench as sb

    roster = sb.resolve(["paper"])
    references = [s for s in sb.ordered() if s.note.startswith("reference")]
    markdown = markdown.replace("<!-- swarmbench:catalog -->", _table(roster, numbered=True))
    markdown = markdown.replace("<!-- swarmbench:references -->", _table(references, numbered=False))
    if "<!-- swarmbench:cli-help -->" in markdown:
        markdown = markdown.replace("<!-- swarmbench:cli-help -->", _cli_help())
    return markdown
