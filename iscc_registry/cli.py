# -*- coding: utf-8 -*-
import io
import json
from os.path import abspath, basename, dirname, join
from loguru import logger as log
import click
import cbor2
from iscc_cli import lib
import iscc_registry
from iscc_registry.conn import db_client, w3_client, chain_name, ipfs_client
from iscc_registry.deploy import deploy as deploy_contract
from iscc_registry.publish import publish
from iscc_registry.observe import RegEntry, find_next, observe as iscc_reg_server
from iscc_registry.verify import create_proof, verify_proof


@click.group()
@click.option("-d", "--debug", default=False, is_flag=True, help="Enable debug mode")
def cli(debug):
    if not debug:
        log.remove()
    else:
        log.info("Debug mode enabled")
        log.info(iscc_registry.settings)


@cli.command()
def deploy():
    """Deploy ISCC Registry contract to chain."""
    w3 = w3_client()
    if click.confirm(f"Deploy registry contract to {chain_name(w3)}"):
        addr = deploy_contract()
        click.echo(f"ISCC Registry contract deployed to {addr}")
    code_path = abspath(dirname(dirname(iscc_registry.__file__)))
    if click.confirm(f"Save contract address to {iscc_registry.ENV_PATH}?"):
        with open(iscc_registry.ENV_PATH, "wt") as outf:
            outf.write(f"CONTRACT_ADDRESS={addr}")
            click.echo("Contract address configuration saved.")
    else:
        click.echo(f"Remember to set CONTRACT_ADDRESS env variable to {addr}")


@cli.command()
@click.option("-r", "--rebuild", default=False, is_flag=True, help="Rebuild meta-index")
def observe(rebuild):
    """Watch Registry contract and index ISCC-IDs"""
    iscc_reg_server(rebuild=rebuild)


@cli.command()
@click.option(
    "-a",
    "--account",
    type=click.INT,
    default=0,
    show_default=True,
    help="Wallet index of account to use for registration.",
)
@click.argument("file", type=click.File("rb"))
def register(file, account):
    """Register a media asset."""
    ic = ipfs_client()
    iscc_result = lib.iscc_from_file(file)
    iscc_code = iscc_result.pop("iscc")
    fname = basename(file.name)
    log.info(f"ISCC-CODE for {fname}: {iscc_code}")

    # Check for probable ISCC-ID
    w3 = w3_client()
    addr = w3.eth.accounts[account]
    iscc_id = find_next(RegEntry(iscc=iscc_code, actor=addr))
    log.info(f"ISCC-ID will probably be: {iscc_id}")

    iscc_result["filename"] = fname
    meta_blob = cbor2.dumps(iscc_result)
    ipfs_result = ic.add(io.BytesIO(meta_blob))
    ipfs_cid = ipfs_result["Hash"]
    log.info(f"CID for {fname} metadata: {ipfs_cid}")
    if click.confirm(f"Register ISCC-CODE?"):
        txid = publish(iscc_code, ipfs_cid, account)
        click.echo(f"Registered ISCC-CODE: {iscc_code}")
        click.echo(f"Actor wallet address: {addr}")
        click.echo(f"Registration TX-ID:   {txid}")
        click.echo(f"Probable ISCC-ID:     {iscc_id}")


@cli.command()
@click.argument("domain", type=click.STRING, required=False)
@click.option(
    "-a",
    "--account",
    type=click.INT,
    default=0,
    show_default=True,
    help="Wallet index of account to use for registration.",
)
def prove(domain, account):
    """Create domain based self-verification proof"""
    if not domain:
        domain = click.prompt("Domain to prove (example: https://example.com/)")
    w3 = w3_client()
    address = w3.eth.accounts[account]
    proof = create_proof(domain, address)
    url = domain + "/iscc-proof.json"
    click.echo(
        f"Publish the following data at {url} to validate your account {address}:"
    )
    click.echo(proof)


@cli.command()
@click.argument("iscc_id", type=click.STRING)
def resolve(iscc_id):
    """Resolve ISCC-ID via meta-index"""
    meta_index = db_client()
    result = meta_index.get(iscc_id, None)
    if result:
        click.echo("Registry Entry:")
        click.echo(json.dumps(result, indent=2))
        ic = ipfs_client()
        raw = ic.cat(result["cid"])
        obj = cbor2.loads(raw)
        click.echo("IPFS Data:")
        click.echo(json.dumps(obj, indent=2))
    else:
        click.echo(f"No entry found for {iscc_id}")


if __name__ == "__main__":
    cli()
