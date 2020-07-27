# -*- coding: utf-8 -*-
import io
import json
from os.path import basename
from loguru import logger as log
import click
import cbor2
from iscc_cli import lib
import iscc_registry
from iscc_registry.conn import db_client, w3_client, chain_name, ipfs_client
from iscc_registry.deploy import deploy as deploy_contract
from iscc_registry.publish import publish


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
        click.echo(f"Remember to set CONTRACT_ADDRESS env variable to {addr}")


@cli.command()
@click.argument("file", type=click.File("rb"))
def register(file):
    """Register a media asset."""
    ic = ipfs_client()
    iscc_result = lib.iscc_from_file(file)
    iscc_code = iscc_result.pop("iscc")
    fname = basename(file.name)
    log.info(f"ISCC-CODE for {fname}: {iscc_code}")
    iscc_result["filename"] = fname
    meta_blob = cbor2.dumps(iscc_result)
    ipfs_result = ic.add(io.BytesIO(meta_blob))
    ipfs_cid = ipfs_result["Hash"]
    log.info(f"CID for {fname} metadata: {ipfs_cid}")
    if click.confirm(f"Register ISCC-CODE?"):
        txid = publish(iscc_code, ipfs_cid)
        click.echo(f"Registration TX: {txid}")


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
