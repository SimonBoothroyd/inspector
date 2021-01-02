from inspector.cli import cli as root_cli
from inspector.cli.cli import launch_cli


def test_root_cli(runner):

    result = runner.invoke(root_cli, ["--help"])

    if result.exit_code != 0:
        raise result.exception

    assert "launch" in result.output


def test_launch_cli(monkeypatch, runner):

    import uvicorn

    expected_message = "Start Server"

    def mock_run(*args, **kwargs):
        print(expected_message)

    monkeypatch.setattr(uvicorn, "run", mock_run)

    result = runner.invoke(launch_cli)

    if result.exit_code != 0:
        raise result.exception

    assert f"{expected_message}\n" == result.output
