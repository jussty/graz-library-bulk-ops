"""Command-line interface for Graz Library Bulk Operations Tool"""

import click
from . import __version__

# TODO: Implement CLI commands


@click.group()
@click.version_option(version=__version__)
def main():
    """Graz Library Bulk Operations Tool

    A command-line tool for bulk operations at Stadtbibliothek Graz.
    """
    pass


@main.command()
@click.argument("query")
@click.option(
    "--type",
    type=click.Choice(["keyword", "author", "title", "isbn"]),
    default="keyword",
    help="Type of search",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file (csv or json)",
)
def search(query, type, output):
    """Search for books in the catalog"""
    click.echo(f"Searching for: {query}")
    click.echo(f"Search type: {type}")
    if output:
        click.echo(f"Output file: {output}")
    click.echo("Search - NOT YET IMPLEMENTED")


@main.command()
@click.argument("file", type=click.Path(exists=True))
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file",
)
def bulk_search(file, output):
    """Search for multiple books from a file"""
    click.echo(f"Bulk search from: {file}")
    if output:
        click.echo(f"Output file: {output}")
    click.echo("Bulk search - NOT YET IMPLEMENTED")


@main.command()
@click.argument("isbn")
@click.option(
    "--email",
    "-e",
    required=True,
    help="User email for notification",
)
def reserve(isbn, email):
    """Reserve a book"""
    click.echo(f"Reserving book: {isbn}")
    click.echo(f"Email: {email}")
    click.echo("Reservation - NOT YET IMPLEMENTED")


@main.command()
@click.argument("title")
@click.option(
    "--recipient",
    "-r",
    required=True,
    help="Recipient name",
)
@click.option(
    "--email",
    "-e",
    required=True,
    help="Recipient email",
)
@click.option(
    "--address",
    "-a",
    help="Delivery address",
)
@click.option(
    "--pickup",
    "-p",
    help="Pickup location",
)
def mail_order(title, recipient, email, address, pickup):
    """Submit a mail order"""
    click.echo(f"Mail order for: {title}")
    click.echo(f"Recipient: {recipient} <{email}>")
    if address:
        click.echo(f"Address: {address}")
    if pickup:
        click.echo(f"Pickup: {pickup}")
    click.echo("Mail order - NOT YET IMPLEMENTED")


if __name__ == "__main__":
    main()
