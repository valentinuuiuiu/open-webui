import re

with open("backend/open_webui/__init__.py", "r") as f:
    content = f.read()

# Make sure we don't add it twice
if "def fanny(" not in content:
    addition = """
@app.command()
def fanny():
    try:
        from open_webui.cli.agentic_cli import start_repl
        start_repl()
    except ImportError as e:
        typer.echo(f"Could not load FannyMae CLI: {e}")
"""
    content = content.replace("if __name__ == '__main__':", addition + "\nif __name__ == '__main__':")

    with open("backend/open_webui/__init__.py", "w") as f:
        f.write(content)
