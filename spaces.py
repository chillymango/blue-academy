"""
Build gym spaces from a Pokemon memory map
"""
import numpy as np
import struct
import typing as T
from bitstring import BitArray

from gymnasium import spaces
from command import CommandClient
from memmap import MemoryMap
from memparser import Entity


HASH_BUMP = {}


def create_reduced_space_from_mmap(mem: MemoryMap) -> spaces.Dict:
    """
    Reduced space

    What do we minimally need in order to represent our agent's observation?
    """
    output = spaces.Dict()

    # Generate an occupancy grid of 10 x 10
    # NOTE: I think we run out of memory if we make the vec too large
    # We'll use a hash bump
    #output["occupancy"] = spaces.MultiDiscrete([256] * 100)
    
    # Map our current location as a 3D box
    output["map"] = spaces.Box(np.array([0, 0, 0]), np.array([255, 255, 255]))

    # TODO: (eventually) add Pokemon stats etc.
    return output


def populate_reduced_space_from_mmap(mem: MemoryMap) -> T.Dict[str, T.Any]:
    output = dict()

    # Populate occupancy grid from tiles
    output["occupancy"] = []
    for idx in range(180):
        tile = struct.unpack(">H", mem.tile.onscreen_tiles[2 * idx:2 * idx+2])[0]
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


def create_spaces_from_mmap(memory_map: MemoryMap) -> spaces.Dict:
    output = spaces.Dict()
    # TODO: doing discovery implicitly is jank
    for attrname in dir(memory_map):
        if isinstance(getattr(memory_map, attrname), Entity):
            for label, subspace in build_spaces(getattr(memory_map, attrname)):
                # TODO: wow this is so shitty
                output[f"{attrname}_{label}"] = subspace
    return output


def build_spaces(entity: Entity) -> T.Tuple[str, spaces.Space]:
    subspaces: T.List[T.Tuple[str, spaces.Space]] = []
    for field in entity._MAP._FIELDS:
        if field._type == "buffer" or field.is_text:
            # ignore these since i don't know what we'd do with it
            pass
        #elif field.is_text:
        #    # use a text field
        #    subspaces.append((field.label, spaces.Text(256)))
        elif field.is_struct_type:
            # assume integer, probably safe to just use 8 or 16-bit representation?
            # use width * 8
            subspaces.append((field.label, spaces.MultiBinary(struct.calcsize(field._type) * 8)))
        else:
            print(f"Unhandled field type {field.label} - {field._type}")

    return subspaces


def populate_space_from_mmap(memory_map: MemoryMap) -> T.Dict[str, T.Any]:
    output = dict()
    for attrname in dir(memory_map):
        if isinstance(getattr(memory_map, attrname), Entity):
            for label, subfield in populate_space(getattr(memory_map, attrname)):
                # TODO: wow this is so shitty
                output[f"{attrname}_{label}"] = subfield
    return output


def populate_space(entity: Entity) -> T.Tuple[str, T.Any]:
    subfields = []
    for field in entity._MAP._FIELDS:
        if field._type == "buffer" or field.is_text:
            # TODO: why doesn't text work with PPO...
            pass
        #elif field.is_text:
        #    subfields.append((field.label, getattr(entity, field.label)))
        elif field.is_struct_type:
            fieldsize = struct.calcsize(field._type)
            padded_array = BitArray(length=fieldsize * 8)
            value = getattr(entity, field.label)
            padded_array.reverse()
            padded_array.overwrite(BitArray(value).reverse())
            padded_array.reverse()
            subfields.append((field.label, padded_array))
    return subfields


if __name__ == "__main__":
    client = CommandClient("localhost", 10018)
    memory = client.do_data_command(b"dump_wram")
    mmap = MemoryMap.hydrate_from_memory(memory)
    out = create_spaces_from_mmap(mmap)
    other = populate_space_from_mmap(mmap)
    import IPython; IPython.embed()
