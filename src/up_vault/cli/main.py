import typer

from up_vault.cli.ingest import app as ingest_app

app = typer.Typer()


app.add_typer(ingest_app, name="ingest")


if __name__ == "__main__":
    app()
