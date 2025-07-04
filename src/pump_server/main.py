
import logging
import signal
import sqlite3
from uuid import UUID
import typer
from typer import BadParameter, Option, Argument
import yaml
from pathlib import Path
from cerberus import Validator
import sys

from .server import Server
from pd_pump.pump import Pump
logger = logging.getLogger(__name__)

config_schema = {
    'device': {'type': 'string', 'required': True},
    'uuid': {'type': 'string', 'required': True},
    'port': {'type': 'integer', 'required': True},
    'discovery': {'type': 'boolean', 'required': True},
    'certificate': {'type': 'string', 'required': True},
    'pkey': {'type': 'string', 'required': True},
    'database': {'type': 'string', 'required': False},
    'comport': {'type': 'string', 'required': True},
}

def main(config_path: str = Argument(..., help="Path to config.yaml"),
         quiet: bool = Option(False, "--quiet"),
         verbose: bool = Option(False, "--verbose"),
         debug: bool = Option(False, "--debug")):

    initialize_logging(quiet=quiet, verbose=verbose, debug=debug)

    try:
        with open(config_path) as f:
            v = Validator(config_schema)
            cfg = yaml.safe_load(f)
            if not v.validate(cfg):
                logging.error(v.errors)
                raise SystemExit("Invalid config file")
    except Exception as e:
        logging.error(f"Could not load config: {e}")
        sys.exit(1)

    uuid = UUID(cfg['uuid'])

    #Initialize Pump
    try:
        pump = Pump(port=cfg['comport'])
    except Exception as e:
        logging.error(f"Pump initialization failed: {e}")
        sys.exit(1)

    #initialize Sila2 server
    server = Server(config=cfg, pump=pump, server_uuid=uuid)

    #load certificates
    try:
        with open(cfg['certificate'], "rb") as f:
            cert = f.read()
        with open(cfg['pkey'], "rb") as f:
            pkey = f.read()

        #start server
        server.start(
            address = "127.0.0.1",
            port=cfg['port'],
            cert_chain=cert,
            private_key=pkey,
            enable_discovery=cfg['discovery']
        )
        logger.info("Server started")

        signal.signal(signal.SIGTERM, lambda *args: server.stop())

        try:
            server.grpc_server.wait_for_termination()
        except KeyboardInterrupt:
            pass

    finally:
        if server.running:
            server.stop()
            logger.info("Server shutdown complete")

def initialize_logging(*, quiet=False, verbose=False, debug=False):
    if sum((quiet, verbose, debug)) > 1:
        raise BadParameter("--quiet, --verbose and --debug are mutually exclusive")

    level = logging.WARNING
    if verbose:
        level = logging.INFO
    if debug:
        level = logging.DEBUG
    if quiet:
        level = logging.ERROR

    logging.basicConfig(level=level, format="%(asctime)s [%(levelname)s] %(message)s")
    logger.setLevel(level)

def run():
    typer.run(main)

if __name__ == "__main__":
    run()
