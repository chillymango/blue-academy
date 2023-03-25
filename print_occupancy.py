"""
Debug print occupancy grid
"""
import numpy as np
import struct
import typing as T

from command import CommandClient
from memmap import MemoryMap


HASH_BUMP = {}


def populate_reduced_space_from_mmap(mem: MemoryMap) -> T.Dict[str, T.Any]:
    output = dict()

    # Populate occupancy grid from tiles
    output["occupancy"] = []
    for idx in range(180):
        tile = struct.unpack(">H", mem.tile.onscreen_tiles[2 * idx:2 * idx+2])[0]
        if tile in HASH_BUMP:
            hashed = HASH_BUMP[tile]
        else:
            hashed = hash(tile) % 256
            while True:
                if hashed not in HASH_BUMP.values():
                    HASH_BUMP[tile] = hashed
                    break
                hashed += 1

                if hashed == hash(tile) % 256:  # we made it a circle
                    print("Hash Bump Full...")
                    break
        output["occupancy"].append(hashed)

    # Fill out our map location
    output["map"] = (mem.location.map_number, mem.location.x_position, mem.location.y_position)
    return output


def populate_occupancy_from_orig_buffer(mem: MemoryMap) -> T.List[int]:
    output = []
    for idx in range(18 * 10):
        tile = struct.unpack(">H", mem.tile.onscreen_tiles[2 * idx:2 * idx+2])[0]
        if tile in HASH_BUMP:
            hashed = HASH_BUMP[tile]
        else:
            hashed = hash(tile) % 256
            while True:
                if hashed not in HASH_BUMP.values():
                    HASH_BUMP[tile] = hashed
                    break
                hashed += 1

                if hashed == hash(tile) % 256:  # we made it a circle
                    print("Hash Bump Full...")
                    break
        output.append(hashed)

    return output


def populate_occupancy_from_copy_buffer(mem: MemoryMap) -> T.List[int]:
    output = []
    for idx in range(18 * 12):
        tile = struct.unpack(">H", mem.tile.copy_buffer[2 * idx:2 * idx+2])[0]
        if tile in HASH_BUMP:
            hashed = HASH_BUMP[tile]
        else:
            hashed = hash(tile) % 256
            while True:
                if hashed not in HASH_BUMP.values():
                    HASH_BUMP[tile] = hashed
                    break
                hashed += 1

                if hashed == hash(tile) % 256:  # we made it a circle
                    print("Hash Bump Full...")
                    break
        output.append(hashed)

    return output


if __name__ == "__main__":
    client = CommandClient('localhost', 10018)
    mem = MemoryMap.hydrate_from_memory(client.dispatch("dump_wram"))
    grid = np.array(populate_occupancy_from_orig_buffer(mem))
    grid2 = np.array(populate_occupancy_from_copy_buffer(mem))
    grid = grid.reshape([18, 10])
    grid2 = grid2.reshape([18, 12])
    occ = grid2[:, 0:10]
    print(grid)
    print('\n')
    print(occ)
    import IPython; IPython.embed()
