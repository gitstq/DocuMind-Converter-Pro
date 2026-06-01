"""
Command-line interface for DocuMind Converter.
"""

import sys
from pathlib import Path
from typing import List, Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from documind import DocumentConverter, __version__
from documind.config import config
from documind.models import ConversionStatus
from documind.utils import setup_logging, get_logger

# Initialize console and logger
console = Console()
logger = get_logger(__name__)


@click.group()
@click.version_option(version=__version__, prog_name="documind")
@click.option("--debug", is_flag=True, help="Enable debug mode")
@click.option("--config", type=click.Path(), help="Path to config file")
@click.pass_context
def cli(ctx: click.Context, debug: bool, config: Optional[str]) -> None:
    """🧠 DocuMind Converter - Intelligent Document Converter & Analyzer
    
    Transform documents with AI-powered insights. Convert between multiple formats
    and extract meaningful information using advanced AI capabilities.
    
    Examples:
        documind convert document.pdf
        documind convert document.docx -o output.md
        documind batch *.pdf -d ./output
        documind info document.pdf
    """
    # Ensure context object exists
    ctx.ensure_object(dict)
    ctx.obj["debug"] = debug
    
    # Setup logging
    log_level = "DEBUG" if debug else config.log_level if hasattr(config, 'log_level') else "INFO"
    setup_logging(log_level=log_level)
    
    # Load config if provided
    if config:
        from documind.config import Config
        Config.load_from_file(Path(config))


@cli.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.option("-o", "--output", type=click.Path(), help="Output file path")
@click.option("-f", "--format", "output_format", default="markdown", help="Output format (default: markdown)")
@click.option("-d", "--output-dir", type=click.Path(), help="Output directory")
@click.option("--ocr/--no-ocr", default=True, help="Enable/disable OCR for images/PDFs")
@click.option("--ocr-lang", default="eng", help="OCR language")
@click.pass_context
def convert(
    ctx: click.Context,
    input_path: str,
    output: Optional[str],
    output_format: str,
    output_dir: Optional[str],
    ocr: bool,
    ocr_lang: str,
) -> None:
    """Convert a document to another format."""
    try:
        converter = DocumentConverter()
        
        with console.status("[bold green]Converting document..."):
            result = converter.convert(
                input_path=input_path,
                output_path=output,
                output_format=output_format,
                output_dir=output_dir,
                ocr_enabled=ocr,
                ocr_language=ocr_lang,
            )
        
        if result.success:
            console.print(Panel(
                f"[bold green]✓ Conversion successful![/bold green]\n\n"
                f"Input: [cyan]{input_path}[/cyan]\n"
                f"Output: [cyan]{result.output_path}[/cyan]\n"
                f"Format: [yellow]{output_format}[/yellow]\n"
                f"Time: [dim]{result.processing_time_ms:.0f}ms[/dim]",
                title="DocuMind Converter",
                border_style="green"
            ))
            
            # Print content preview
            if result.content:
                preview = result.content[:500] + "..." if len(result.content) > 500 else result.content
                console.print("\n[bold]Preview:[/bold]")
                console.print(Panel(preview, border_style="dim"))
        else:
            console.print(Panel(
                f"[bold red]✗ Conversion failed[/bold red]\n\n"
                f"Errors:\n" + "\n".join(f"  • {e}" for e in result.errors),
                title="DocuMind Converter",
                border_style="red"
            ))
            sys.exit(1)
            
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        if ctx.obj.get("debug"):
            raise
        sys.exit(1)


@cli.command()
@click.argument("input_paths", nargs=-1, required=True)
@click.option("-d", "--output-dir", type=click.Path(), required=True, help="Output directory")
@click.option("-f", "--format", "output_format", default="markdown", help="Output format")
@click.option("-j", "--jobs", type=int, default=4, help="Number of parallel jobs")
@click.pass_context
def batch(
    ctx: click.Context,
    input_paths: tuple,
    output_dir: str,
    output_format: str,
    jobs: int,
) -> None:
    """Convert multiple documents in batch."""
    try:
        converter = DocumentConverter()
        
        with console.status("[bold green]Converting documents..."):
            result = converter.convert_batch(
                input_paths=list(input_paths),
                output_dir=output_dir,
                output_format=output_format,
                max_workers=jobs,
            )
        
        # Display results table
        table = Table(title="Batch Conversion Results")
        table.add_column("Status", style="bold")
        table.add_column("Count", justify="right")
        table.add_column("Percentage", justify="right")
        
        total = result.total_files
        table.add_row(
            "[green]Successful[/green]",
            str(result.successful),
            f"{result.successful/total*100:.1f}%" if total > 0 else "0%"
        )
        table.add_row(
            "[yellow]Partial[/yellow]",
            str(result.partial),
            f"{result.partial/total*100:.1f}%" if total > 0 else "0%"
        )
        table.add_row(
            "[red]Failed[/red]",
            str(result.failed),
            f"{result.failed/total*100:.1f}%" if total > 0 else "0%"
        )
        table.add_row("─" * 10, "─" * 5, "─" * 10)
        table.add_row("Total", str(total), "100%")
        
        console.print(table)
        console.print(f"\nTotal processing time: [dim]{result.total_processing_time_ms:.0f}ms[/dim]")
        
        if result.errors:
            console.print("\n[bold red]Errors:[/bold red]")
            for error in result.errors[:10]:  # Show first 10 errors
                console.print(f"  • {error}")
            if len(result.errors) > 10:
                console.print(f"  ... and {len(result.errors) - 10} more")
        
        if result.failed > 0:
            sys.exit(1)
            
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        if ctx.obj.get("debug"):
            raise
        sys.exit(1)


@cli.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.pass_context
def info(ctx: click.Context, input_path: str) -> None:
    """Display document information."""
    try:
        converter = DocumentConverter()
        doc_info = converter.get_info(input_path)
        
        table = Table(title=f"Document Information: {Path(input_path).name}")
        table.add_column("Property", style="cyan")
        table.add_column("Value")
        
        table.add_row("Path", str(doc_info.path))
        table.add_row("Format", doc_info.format.value if doc_info.format else "Unknown")
        table.add_row("Size", f"{doc_info.size_bytes:,} bytes ({doc_info.size_bytes / 1024:.1f} KB)")
        
        if doc_info.page_count:
            table.add_row("Pages", str(doc_info.page_count))
        if doc_info.word_count:
            table.add_row("Words", f"{doc_info.word_count:,}")
        if doc_info.title:
            table.add_row("Title", doc_info.title)
        if doc_info.author:
            table.add_row("Author", doc_info.author)
        if doc_info.subject:
            table.add_row("Subject", doc_info.subject)
        if doc_info.keywords:
            table.add_row("Keywords", ", ".join(doc_info.keywords))
        if doc_info.created_at:
            table.add_row("Created", doc_info.created_at.isoformat())
        if doc_info.modified_at:
            table.add_row("Modified", doc_info.modified_at.isoformat())
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        if ctx.obj.get("debug"):
            raise
        sys.exit(1)


@cli.command()
def formats() -> None:
    """List supported formats."""
    converter = DocumentConverter()
    supported = converter.get_supported_formats()
    
    table = Table(title="Supported Formats")
    table.add_column("Type", style="bold cyan")
    table.add_column("Formats")
    
    table.add_row("Input", ", ".join(supported["input"]))
    table.add_row("Output", ", ".join(supported["output"]))
    
    console.print(table)


@cli.command()
@click.option("--api-key", help="OpenAI API key")
@click.option("--model", default="gpt-4o-mini", help="OpenAI model")
@click.option("--output-dir", type=click.Path(), help="Default output directory")
def config_cmd(api_key: Optional[str], model: str, output_dir: Optional[str]) -> None:
    """Configure DocuMind settings."""
    config_lines = ["# DocuMind Configuration"]
    
    if api_key:
        config_lines.append(f'DOCUMIND_OPENAI_API_KEY="{api_key}"')
    config_lines.append(f'DOCUMIND_OPENAI_MODEL="{model}"')
    if output_dir:
        config_lines.append(f'DOCUMIND_OUTPUT_DIR="{output_dir}"')
    
    config_content = "\n".join(config_lines)
    
    console.print(Panel(
        config_content,
        title="Configuration",
        border_style="blue"
    ))
    
    console.print("\n[dim]Save this to ~/.documind.env or set as environment variables[/dim]")


def main() -> None:
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
