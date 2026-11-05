import sys
import requests
import time
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt

console = Console()

class FannyMaeCLI:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        self.session = requests.Session()
        self.headers = {"Content-Type": "application/json"}
        # For a full implementation, we'd need to auth (e.g. login and get token).
        # We'll assume the user is authenticating or bypassing auth for local CLI usage.
        self.token = None

    def login(self, email, password):
        try:
            res = self.session.post(
                f"{self.base_url}/api/v1/auths/signin",
                json={"email": email, "password": password}
            )
            res.raise_for_status()
            data = res.json()
            self.token = data.get("token")
            self.headers["Authorization"] = f"Bearer {self.token}"
            return True
        except Exception as e:
            console.print(f"[red]Login failed: {e}[/red]")
            return False

    def chat(self, prompt, model_id="llama3:latest"): # Default model, should be configurable
        if not self.token:
            console.print("[red]Not authenticated. Please login first.[/red]")
            return

        payload = {
            "model": model_id,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False
        }

        try:
            res = self.session.post(
                f"{self.base_url}/api/chat/completions",
                headers=self.headers,
                json=payload
            )
            res.raise_for_status()
            data = res.json()
            reply = data["choices"][0]["message"]["content"]
            return reply
        except Exception as e:
            console.print(f"[red]Error communicating with backend: {e}[/red]")
            return "Sorry, I encountered an error."

def start_repl():
    console.print("[bold magenta]Welcome to FannyMae OS (Agentic Hub) - CLI Edition[/bold magenta]")
    console.print("Type 'exit' or 'quit' to close.\n")

    cli = FannyMaeCLI()

    # Very basic dummy auth fallback or configuration prompt
    # Since we know from memory: admin / ionutbaltag3@gmail.com / madalina_1A
    # We will try to auto-login.
    console.print("[cyan]Attempting to authenticate as FannyMae...[/cyan]")
    email = "ionutbaltag3@gmail.com"
    password = "madalina_1A"

    if not cli.login(email, password):
        console.print("[yellow]Auto-login failed. Make sure the server is running on http://localhost:8080[/yellow]")
        console.print("[yellow]You can start it in another terminal with: open-webui serve[/yellow]")
        # We don't exit, let user try anyway or we can mock it for now.
    else:
        console.print("[green]Authentication successful![/green]\n")

    while True:
        try:
            user_input = Prompt.ask("[bold blue]You[/bold blue]")
            if user_input.strip().lower() in ['exit', 'quit']:
                break
            if not user_input.strip():
                continue

            console.print("\n[bold magenta]FannyMae[/bold magenta] is thinking...")
            reply = cli.chat(user_input)

            if reply:
                console.print("\n[bold magenta]FannyMae:[/bold magenta]")
                console.print(Markdown(reply))
                console.print()

        except (KeyboardInterrupt, EOFError):
            break

    console.print("[magenta]Goodbye![/magenta]")

if __name__ == "__main__":
    start_repl()
