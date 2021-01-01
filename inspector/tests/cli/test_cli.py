from inspector.cli import cli as root_cli


def test_root_cli(runner):

    result = runner.invoke(root_cli, ["--help"])

    if result.exit_code != 0:
        raise result.exception
