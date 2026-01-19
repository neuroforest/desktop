import os
import shutil
import subprocess
import sys
import time

from neuro.utils import internal_utils, time_utils, terminal_style


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
    shutil.rmtree(f"{BUILD_DIR}/tw5/.git")


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
        "install", "-l",
        "fs",
        "neo4j-driver"
    ], stdout=subprocess.DEVNULL)


def archive():
    global BUILD_DIR
    archive_name = f"build-{time_utils.DATE_ISO}"
    BUILD_DIR = internal_utils.get_path("archive") + f"/desktop/{archive_name}"
    print(f"Creating desktop archive {archive_name}")
    main()


def main():
    start_time = time.time()
    os.makedirs(BUILD_DIR, exist_ok=True)
    copy_nwjs()
    internal_utils.copy_plugins_and_themes()
    copy_tw5()
    copy_source()
    install_node_modules()
    end_time = time.time()
    print(f"{terminal_style.SUCCESS} {terminal_style.BOLD}Finished in {end_time - start_time:.1f} s.{terminal_style.RESET}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "archive":
            archive()
        else:
            custom_build_path = sys.argv[1]
            if not os.path.isabs(custom_build_path):
                custom_build_path = os.path.abspath(custom_build_path)
            BUILD_DIR = custom_build_path
            main()
    else:
        BUILD_DIR = os.getenv("BUILD")
        main()
