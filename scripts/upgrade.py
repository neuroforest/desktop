import os
import shutil
import subprocess

from neuro.utils import config


class Nwjs:
    def __init__(self, nwjs_version=None, nwjs_url=None, overwrite=False):
        self.nwjs_version = nwjs_version
        self.nwjs_url = nwjs_url
        self.overwrite = overwrite
        self.local_nwjs = os.getenv("DESKTOP") + "/nwjs"
        self.tarfile_local = f"{self.local_nwjs}/v{self.nwjs_version}.tar.gz"
        self.tarfile_remote = f"{self.nwjs_url}/v{self.nwjs_version}/nwjs-sdk-v{self.nwjs_version}-linux-x64.tar.gz"
        self.extract_temp = f"{self.local_nwjs}/nwjs-sdk-v{self.nwjs_version}-linux-x64"
        self.extract_final = f"{self.local_nwjs}/v{self.nwjs_version}"

        if not os.path.isdir(self.local_nwjs):
            os.makedirs(self.local_nwjs)
        self.download()
        self.extract()

    def download(self):
        print("Downloading...", end="")
        if os.path.isfile(self.tarfile_local) and not self.overwrite:
            print("EXISTS")
            return
        elif os.path.isfile(self.tarfile_local) and self.overwrite:
            os.remove(self.tarfile_local)

        self.overwrite = True

        subprocess.run([
            "wget",
            "-c",
            "--show-progress", "-q",
            "-O", self.tarfile_local,
            self.tarfile_remote
        ], check=True)
        print("OK")

    def extract(self):
        print("Extracting...", end="")
        if os.path.isdir(self.extract_final) and not self.overwrite:
            print("EXISTS")
            return
        elif os.path.isdir(self.extract_final) and self.overwrite:
            shutil.rmtree(f"{self.local_nwjs}/v{self.nwjs_version}")

        subprocess.run([
            "tar",
            "-xvzf",
            self.tarfile_local,
            "-C", self.local_nwjs], stdout=subprocess.DEVNULL, check=True)
        subprocess.run([
            "mv",
            self.extract_temp,
            self.extract_final])
        print("OK")


if __name__ == "__main__":
    Nwjs(nwjs_version=os.getenv("NWJS_VERSION"), nwjs_url=os.getenv("NWJS_URL"))
