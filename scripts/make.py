import json
import os
import shutil
import subprocess

from neuro.utils import config, internal_utils


def copy_nwjs():
    print("Building: NW.js")
    nwjs_dir = f"{internal_utils.get_path("desktop")}/nwjs/"
    nwjs_source_path = f"{nwjs_dir}/v{os.getenv('NWJS_VERSION')}"
    shutil.copytree(nwjs_source_path, BUILD_DIR)


def copy_tw5():
    print("Building: TW5")
    tw5_source_path = internal_utils.get_path("tw5")
    shutil.rmtree(f"{BUILD_DIR}/tw5", ignore_errors=True)
    shutil.copytree(tw5_source_path, f"{BUILD_DIR}/tw5")


def copy_plugins_and_themes():
    print("Building: plugins and themes")
    for plugin in json.loads(os.getenv("EXTERNAL_PLUGINS")):
        plugin_source_path = plugin["path"]
        plugin_target_path = internal_utils.get_path("desktop") + "/build/tw5/plugins/" + plugin["name"]
        shutil.rmtree(plugin_target_path, ignore_errors=True)
        shutil.copytree(plugin_source_path, plugin_target_path)

    for theme in json.loads(os.getenv("EXTERNAL_THEMES")):
        theme_source_path = theme["path"]
        theme_target_path = internal_utils.get_path("desktop") + "/build/tw5/themes/" + theme["name"]
        shutil.rmtree(theme_target_path)
        shutil.copytree(theme_source_path, theme_target_path)


def copy_source():
    print("Building: source")
    source = internal_utils.get_path("desktop") + "/source"
    shutil.copytree(source, f"{BUILD_DIR}/source")
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
    shutil.rmtree(BUILD_DIR, ignore_errors=True)
    copy_nwjs()
    copy_tw5()
    copy_plugins_and_themes()
    copy_source()
    install_node_modules()


if __name__ == "__main__":
    BUILD_DIR = os.getenv("BUILD")
    main()
