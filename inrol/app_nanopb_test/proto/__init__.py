import os
import re
import sys

from os import path
from os.path import dirname
from os.path import basename
from shutil import which

from subprocess import call
from importlib import import_module

protoc = which("protoc") or os.environ["PROTOC"]
assert protoc is not None
assert path.exists(protoc)

pkgdir = dirname(__file__)
proto_src = [path.join(pkgdir, f) for f in os.listdir(pkgdir) if f.endswith(".proto")]
proto_out = [path.join(pkgdir, src.rsplit(".", 1)[0] + "_pb2.py") for src in proto_src]
proto_mod = ["." + basename(out).rsplit(".", 1)[0] for out in proto_out]


def generate_proto(src: str, out: str) -> None:
    src_exists = path.exists(src)
    out_exists = path.exists(out)
    out_outdated = out_exists and src_exists and path.getmtime(src) > path.getmtime(out)

    if not out_exists or out_outdated:
        assert src_exists
        print("Generating {0}".format(out))
        cmd = [protoc, "-I" + pkgdir, "--python_out=" + pkgdir, src]
        if call(cmd) != 0:
            sys.exit(-1)

        with open(out) as f:
            lines = f.readlines()

        with open(out, "w") as of:
            of.writelines(
                [re.sub(r"^(import\s+\w+_pb2)", r"from . \1", line) for line in lines]
            )


[*map(generate_proto, proto_src, proto_out)]
[*map(lambda m: import_module(m, __name__), proto_mod)]
