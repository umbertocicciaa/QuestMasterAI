"""Command line interface for QuestMaster AI."""

import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from .app import QuestMasterApp
from .core.config import get_settings
from .core.logging import setup_logging

console = Console()


@click.group()
@click.option(
    "--log-level",
    default="INFO",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
    help="Logging level",
)
@click.option("--debug", is_flag=True, help="Enable debug mode")
@click.option("--api-key", help="OpenAI API key override")
@click.pass_context
def cli(ctx: click.Context, log_level: str, debug: bool, api_key: Optional[str]) -> None:
    """QuestMaster AI: Agentic AI for Interactive Storytelling."""
    ctx.ensure_object(dict)
    ctx.obj["log_level"] = log_level
    ctx.obj["debug"] = debug
    ctx.obj["api_key"] = api_key
    
    # Setup logging
    setup_logging(log_level=log_level, debug=debug)


@cli.command()
@click.option(
    "--lore-path",
    type=click.Path(exists=True, path_type=Path),
    help="Path to lore file",
)
@click.pass_context
def phase1(ctx: click.Context, lore_path: Optional[Path]) -> None:
    """Run Phase 1: Story Generation with PDDL validation."""
    try:
        app = QuestMasterApp(api_key=ctx.obj["api_key"])
        
        console.print(Panel.fit("🚀 Starting Phase 1: Story Generation", style="bold blue"))
        
        if not app.check_requirements():
            console.print("[red]❌ Requirements not met. Please check the issues above.[/red]")
            sys.exit(1)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Generating and validating PDDL...", total=None)
            validation_result = app.run_phase1(str(lore_path) if lore_path else None)
            progress.update(task, completed=True)
        
        if validation_result.success:
            console.print("[green]✅ Phase 1 completed successfully![/green]")
            console.print(f"Execution time: {validation_result.execution_time:.2f}s")
            if validation_result.plan:
                console.print(f"Plan length: {len(validation_result.plan)} steps")
        else:
            console.print("[red]❌ Phase 1 failed![/red]")
            console.print(f"Error: {validation_result.error_message}")
            sys.exit(1)
            
    except Exception as e:
        console.print(f"[red]❌ Phase 1 failed: {e}[/red]")
        if ctx.obj["debug"]:
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.pass_context
def phase2(ctx: click.Context) -> None:
    """Run Phase 2: Interactive Story Game generation."""
    try:
        app = QuestMasterApp(api_key=ctx.obj["api_key"])
        
        console.print(Panel.fit("🎮 Starting Phase 2: Interactive Story Game", style="bold green"))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Generating story and frontend...", total=None)
            app.run_phase2()
            progress.update(task, completed=True)
        
        console.print("[green]✅ Phase 2 completed successfully![/green]")
        
        settings = get_settings()
        console.print(f"Story saved to: {settings.story_path}")
        console.print(f"Frontend saved to: {settings.frontend_path}")
        
    except Exception as e:
        console.print(f"[red]❌ Phase 2 failed: {e}[/red]")
        if ctx.obj["debug"]:
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.option(
    "--lore-path",
    type=click.Path(exists=True, path_type=Path),
    help="Path to lore file",
)
@click.pass_context
def run(ctx: click.Context, lore_path: Optional[Path]) -> None:
    """Run the complete QuestMaster pipeline (Phase 1 + Phase 2)."""
    try:
        app = QuestMasterApp(api_key=ctx.obj["api_key"])
        
        console.print(Panel.fit("🌟 QuestMaster AI - Full Pipeline", style="bold magenta"))
        
        if not app.check_requirements():
            console.print("[red]❌ Requirements not met. Please check the issues above.[/red]")
            sys.exit(1)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Running QuestMaster pipeline...", total=None)
            app.run_full_pipeline(str(lore_path) if lore_path else None)
            progress.update(task, completed=True)
        
        console.print("[green]🎉 QuestMaster pipeline completed successfully![/green]")
        
        settings = get_settings()
        console.print(f"✨ Story saved to: {settings.story_path}")
        console.print(f"✨ Frontend saved to: {settings.frontend_path}")
        console.print("\\n[yellow]You can now run the frontend with:[/yellow]")
        console.print(f"[cyan]streamlit run {settings.frontend_path}[/cyan]")
        
    except Exception as e:
        console.print(f"[red]❌ Pipeline failed: {e}[/red]")
        if ctx.obj["debug"]:
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.pass_context
def check(ctx: click.Context) -> None:
    """Check system requirements and configuration."""
    try:
        app = QuestMasterApp(api_key=ctx.obj["api_key"])
        
        console.print(Panel.fit("🔍 Checking QuestMaster Requirements", style="bold yellow"))
        
        if app.check_requirements():
            console.print("[green]✅ All requirements satisfied![/green]")
        else:
            console.print("[red]❌ Some requirements not met.[/red]")
            sys.exit(1)
            
    except Exception as e:
        console.print(f"[red]❌ Requirement check failed: {e}[/red]")
        if ctx.obj["debug"]:
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.pass_context
def frontend(ctx: click.Context) -> None:
    """Start the Streamlit frontend (if generated)."""
    settings = get_settings()
    
    if not settings.frontend_path.exists():
        console.print("[red]❌ Frontend not found. Run 'questmaster run' first.[/red]")
        sys.exit(1)
    
    console.print(f"[green]🚀 Starting Streamlit frontend...[/green]")
    console.print(f"Frontend file: {settings.frontend_path}")
    
    import subprocess
    
    try:
        subprocess.run([
            "streamlit", "run",
            str(settings.frontend_path),
            "--server.port", str(settings.streamlit_port),
            "--server.address", settings.streamlit_host,
        ])
    except KeyboardInterrupt:
        console.print("\\n[yellow]Frontend stopped.[/yellow]")
    except FileNotFoundError:
        console.print("[red]❌ Streamlit not found. Please install with: pip install streamlit[/red]")
        sys.exit(1)


def main() -> None:
    """Main CLI entry point."""
    cli()


if __name__ == "__main__":
    main()
