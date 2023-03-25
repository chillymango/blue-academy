"""
High-Level Navigation for Pokemon Red

Since the bot can't seem to learn in reasonable time how to make sense of the
game world, we'll give it more high-level instructions instead of just "UDLR".

To this end, we construct a stateful representation of the game world.
"""
import numpy as np
import struct
import typing as T

from command import CommandClient
from memmap import MemoryMap


# NOTE: if executing this, values may change slightly between rounds.
# This is because the standard python Hash function does not seem to
# do well against the hex values in our game. This means that only
# the relative hashes of the tiles can be used to compare differences.
# TODO: this is actually a pretty good way, it seems, of determining
# objects that are similar to each other. Doing some sort of learning
# on that could be interesting...?
TILE_HASH_BUMP: T.Dict[int, int] = dict()


# Initialize hash bump with zeros
# Zero represents the player character.
SPRITE_HASH_BUMP: T.Dict[int, int] = dict({0: 0})


def populate_occupancy_from_copy_buffer(mem: MemoryMap) -> np.array:
    occ_list = []

    # Terrain tiles are mapped between 256 and 511
    width = 10
    depth = 9
    # j = 0..9
    # i = 0..8
    for j in range(depth):
        # j = 1
        for i in range(width):
            # i = 2
            start1 = 2 * i + 2 * j * 2 * width
            end1 = 2 * i + 2 * j * 2 * width + 2
            start2 = 2 * i + (2 * j + 1) * 2 * width
            end2 = 2 * i + (2 * j + 1) * 2 * width + 2
            print(start1,end1)
            print(start2,end2)
            tile = struct.unpack(
                ">I",
                mem.tile.onscreen_tiles[start1:end1]
                # 24:26
                + mem.tile.onscreen_tiles[start2:end2]
                # 34:36
            )[0]

            if tile in TILE_HASH_BUMP:
                hashed = TILE_HASH_BUMP[tile]
            else:
                hashed = tile % 256
                while True:
                    if hashed not in TILE_HASH_BUMP.values():
                        TILE_HASH_BUMP[tile] = hashed
                        break
                    hashed += 1
                    if hashed == tile % 256:  # we made it a circle
                        print("Tile Hash Bump Full...")
                        break
    
            occ_list.append(hashed + 256)

    occ = np.array(occ_list)
    occ = occ.reshape([depth, width])
    occ = occ[:, 0:10]

    # Place sprites on the map
    # Sprites are mapped between 0 and 255
    me = mem.sprites[0]
    for sprite in mem.sprites[1:]:
        if not sprite.picture_id:
            continue

        x_delta = int((sprite.x_screen_pos - me.x_screen_pos) / 16)
        y_delta = int((sprite.y_screen_pos - me.y_screen_pos) / 16)

        y_idx = 4 + y_delta
        x_idx = 4 + x_delta

        if y_idx < 0 or y_idx >= 9:
            continue
        if x_idx < 0 or x_idx >= 10:
            continue

        # no need to hash, just use picture_id
        occ[4 + y_delta, 4 + x_delta] = sprite.picture_id

    # Set our position
    occ[4, 4] = 0

    return occ


class Navigator:

    def __init__(self, client: "CommandClient", tiles_meta: T.Dict = None) -> None:
        # Command Client is the primary interface for the game.
        # It will issue button commands to the game, and read game RAM to determine
        # game state.
        self._client = client

        # Tile metadata.
        # To save on time (where the computer would theoretically be able to infer this),
        # we keep track of all tiles and check to see whether or not they are interactable,
        # passable, or teleporting.
        #
        # We can cache the results generally, though we may run into some confusion when
        # doors for example do not open unless some state is met. But that's so far in the
        # future and I honestly don't think we'll make it there, so for now we can pass in
        # a base set of tiles meta.
        #
        # It would be pretty cool though if we could make a guess based on what the tile *looks*
        # like, and use a neural network of some sort to make strong predictions about the type
        # of object we are looking at.
        self._tiles_meta = tiles_meta or dict()

        # Occupancy Grid
        # The occupancy grid here should store the makeup of the blocks as four
        # bytes together. This should give the occupancy grid a total size of
        # 9 x 10, where 9 is the vertical and 10 is the horizontal. The upper
        # two bytes are concatenated with the lower two bytes to get the final
        # four byte segment representing the tile.
        mem = MemoryMap.hydrate_from_memory(self._client.dispatch("dump_wram"))
        self._occupancy = populate_occupancy_from_copy_buffer(mem)

    def update_occupancy(self) -> None:
        mem = MemoryMap.hydrate_from_memory(self._client.dispatch("dump_wram"))
        if self._is_text(mem):
            # do not update occupancy if text is on the screen
            return
        self._occupancy = populate_occupancy_from_copy_buffer(mem)

    def _is_text(self, mem: MemoryMap) -> bool:
        return False


if __name__ == "__main__":
    from command import CommandClient
    from memmap import MemoryMap
    client = CommandClient('localhost', 10018)
    mem = MemoryMap.hydrate_from_memory(client.dispatch("dump_wram"))
    out = populate_occupancy_from_copy_buffer(mem)
    print(out)
    #import IPython; IPython.embed()