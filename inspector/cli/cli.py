import click
import uvicorn


@click.group()
def cli():
    """The root group for all CLI commands."""


@click.command("launch", help="Launch the inspector RESTful API.")
@click.option(
    "--host",
    default="127.0.0.1",
    type=click.STRING,
    help="The ip address to use for the API.",
    show_default=True,
)
@click.option(
    "--port",
    default=5000,
    type=click.INT,
    help="The port to use for the API.",
    show_default=True,
)
@click.option(
    "--log-level",
    default="info",
    type=click.Choice(["none", "debug", "info", "warning", "error", "critical"]),
    help="The verbosity of the API logger.",
    show_default=True,
)
def launch_cli(host, port, log_level):

    uvicorn.run(
        "inspector.backend.app:app",
        host=host,
        port=port,
        log_level=log_level,
    )


cli.add_command(launch_cli)
