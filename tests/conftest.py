"""Shared pytest fixtures for GDA."""

import pytest
from typer import Typer
from typer.testing import CliRunner

from dev.mocks.github import MockGitHubClient
from gda.main import app
from gda.services.archive import ArchiveService


@pytest.fixture()
def cli_runner() -> CliRunner:
    """Provide a CLI runner for testing Typer commands."""
    return CliRunner()


@pytest.fixture()
def typer_app() -> Typer:
    """Return the Typer application under test."""
    return app


@pytest.fixture()
def mock_github_client() -> MockGitHubClient:
    """Provide a mock GitHub client for testing."""
    return MockGitHubClient()


@pytest.fixture()
def archive_service() -> ArchiveService:
    """Provide an archive service for testing."""
    return ArchiveService()


@pytest.fixture()
def app_with_mocks(mock_github_client: MockGitHubClient) -> Typer:
    """Return app with mock services injected via callback override."""
    import typer

    from gda.context import AppContext
    from gda.services.archive import ArchiveService

    test_app = typer.Typer(
        name="gda",
        help="GitHub Data Assets - Test App",
        no_args_is_help=True,
    )

    @test_app.callback()
    def setup(ctx: typer.Context) -> None:
        ctx.obj = AppContext(
            github_client=mock_github_client,
            archive_service=ArchiveService(),
        )

    # Register commands from main app
    from gda.main import app

    for command_info in app.registered_commands:
        if command_info.callback:
            test_app.command(
                name=command_info.name,
                help=command_info.help,
                hidden=command_info.hidden,
            )(command_info.callback)

    return test_app
