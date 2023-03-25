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


def main(model_name: str, idx: int = None, debug: bool = False) -> None:
    client = CommandClient("localhost", 10018)
    memory = client.do_data_command(b"dump_wram")
    mmap = MemoryMap.hydrate_from_memory(memory)
    if debug:
        import IPython; IPython.embed()
    model = getattr(mmap, model_name)
    if idx is not None:
        print(model[idx])
    else:
        print(model)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("model")
    parser.add_argument("--index", type=int)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    main(args.model, idx=args.index, debug=args.debug)
