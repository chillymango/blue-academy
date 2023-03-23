"""
Generate garbage for now

At some point read from GBA
"""
import argparse
import os
import random
from command import CommandClient
from memparser import *
from memmap import MemoryMap
from models import *


def main(model_name: str, debug: bool = False) -> None:
    client = CommandClient("localhost", 10018)
    memory = client.do_data_command(b"dump_wram")
    if debug:
        import IPython; IPython.embed()
    mmap = MemoryMap.hydrate_from_memory(memory)
    print(getattr(mmap, model_name))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("model")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    main(args.model, debug=args.debug)
