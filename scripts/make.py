import os
import shutil
import subprocess
import time

from neuro.utils import config, internal_utils
from neuro.tools.local import assemble
from neuro.tools.terminal import style


def copy_nwjs():
    print("Building: NW.js")
    nwjs_dir = internal_utils.get_path("desktop") + "/nwjs"
    nwjs_source_path = f"{nwjs_dir}/v{os.getenv('NWJS_VERSION')}/"
    rsync_copy_command = [
        "rsync",
        "-a",
        "--delete",
        nwjs_source_path,
        BUILD_DIR
    ]
    subprocess.run(rsync_copy_command, check=True, stdout=subprocess.DEVNULL)


def copy_tw5():
    print("Building: TW5")
    tw5_source_path = internal_utils.get_path("tw5")
    rsync_copy_command = [
        "rsync",
        "-a",
        "--delete",
        tw5_source_path,
        BUILD_DIR
    ]
    subprocess.run(rsync_copy_command, check=True, stdout=subprocess.DEVNULL)


def copy_source():
    print("Building: source")
    source = internal_utils.get_path("desktop") + "/source"
    rsync_copy_command = [
        "rsync",
        "-a",
        "--delete",
        source,
        BUILD_DIR
    ]
    subprocess.run(rsync_copy_command, check=True, stdout=subprocess.DEVNULL)
    shutil.move(f"{BUILD_DIR}/source/package.json", f"{BUILD_DIR}/package.json")


def install_node_modules():
    print("Building: node modules")
    os.chdir(BUILD_DIR)
    subprocess.run([
        "npm",
        "install", "-l"
        "fs",
        "neo4j-driver"
    ])


def main():
    start_time = time.time()
    os.makedirs(BUILD_DIR, exist_ok=True)
    copy_nwjs()
    copy_tw5()
    assemble.copy_plugins_and_themes()
    copy_source()
    install_node_modules()
    end_time = time.time()
    print(f"{style.SUCCESS} {style.BOLD}Finished in {end_time - start_time:.1f} s.{style.RESET}")


if __name__ == "__main__":
    BUILD_DIR = os.getenv("BUILD")
    main()
