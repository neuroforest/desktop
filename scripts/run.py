import logging
import os
import sys
import subprocess

import neo4j

from neuro.tools.tw5api import tw_get, tw_actions
from neuro.utils import network_utils


def verify_neo4j():
    logging.getLogger("neo4j").setLevel(logging.ERROR)
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")
    neo4j_driver = neo4j.GraphDatabase.driver(uri, auth=(user, password))

    try:
        neo4j_driver.verify_connectivity()
        print("Neo4j connected")
    except neo4j.exceptions.ServiceUnavailable:
        print(f"Neo4j inaccessible: {uri}")
        sys.exit(1)
    except Exception as e:
        print("Neo4j inaccessible:", e)
        sys.exit(1)
    finally:
        neo4j_driver.close()


def register_protocol():
    url = sys.argv[1]
    uuid = url.replace("neuro://", "")

    if not network_utils.is_port_in_use(os.getenv("ND_PORT")):
        print("NeuroDesktop not running")
        return

    try:
        tid_title = tw_get.filter_output(f"[search:neuro.id[{uuid}]]")[0]
        tw_actions.open_tiddler(tid_title)
    except IndexError:
        print(f"Not found: {uuid}")


def main():
    if len(sys.argv) > 1:
        register_protocol()
    else:
        os.chdir(BUILD_DIR)
        verify_neo4j()
        print("Running nw.js")
        subprocess.Popen([
            os.getenv("BUILD") + "/nw"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


if __name__ == "__main__":
    BUILD_DIR = os.getenv("BUILD")
    main()
