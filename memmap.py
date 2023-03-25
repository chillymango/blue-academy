import typing as T

from models import *


class MemoryMap:
    """
    Manually assign slots

    Top-level object is not a pydantic model so I can retain my sanity
    """

    REGION_START_ADDR = 0xC000

    sprites: T.List[Sprite] = list()
    tile: Tile = None
    menu: Menu = None
    battle: Battle = None
    pokemart: PokemonMart = None
    name_rater: NameRater = None
    battle2: Battle2 = None
    battle3: Battle3 = None
    battle_pokemon: BattlePokemon = None
    battle4: Battle4 = None
    battle_status: BattleStatus = None
    game_corner: GameCorner = None
    player: Player = None
    pokedex: PokedexCompletion = None
    inventory: Inventory = None
    badges: Badges = None
    location: Location = None
    events: EventFlags = None
    pokemon: T.List[Pokemon] = list()

    @classmethod
    def apply_offset(cls, memory: bytes, model_klass: T.Type["Entity"], start_addr: int) -> "Entity":
        return model_klass.hydrate_from_memory(memory, start_addr - cls.REGION_START_ADDR)

    @classmethod
    def hydrate_from_memory(cls, memory: bytes) -> "MemoryMap":
        mmap = cls()

        # Build Singletons
        cls.tile = Tile.hydrate_from_memory(memory, 0xC3A0 - cls.REGION_START_ADDR)
        cls.menu = Menu.hydrate_from_memory(memory, 0xCC24 - cls.REGION_START_ADDR)
        cls.battle = Battle.hydrate_from_memory(memory, 0xCCD5 - cls.REGION_START_ADDR)
        cls.pokemart = PokemonMart.hydrate_from_memory(memory, 0xCF7B - cls.REGION_START_ADDR)
        cls.name_rater = NameRater.hydrate_from_memory(memory, 0xCF92 - cls.REGION_START_ADDR)
        cls.battle2 = Battle2.hydrate_from_memory(memory, 0xCCDC - cls.REGION_START_ADDR)
        cls.battle3 = Battle3.hydrate_from_memory(memory, 0xCFCC - cls.REGION_START_ADDR)
        cls.battle_pokemon = BattlePokemon.hydrate_from_memory(memory, 0xD009 - cls.REGION_START_ADDR)
        cls.battle4 = Battle4.hydrate_from_memory(memory, 0xD05A - cls.REGION_START_ADDR)
        cls.battle_status = BattleStatus.hydrate_from_memory(memory, 0xD062 - cls.REGION_START_ADDR)
        cls.game_corner = GameCorner.hydrate_from_memory(memory, 0xD13D - cls.REGION_START_ADDR)
        cls.player = Player.hydrate_from_memory(memory, 0xD158 - cls.REGION_START_ADDR)
        cls.pokedex = PokedexCompletion.hydrate_from_memory(memory, 0xD2F7 - cls.REGION_START_ADDR)
        cls.inventory = Inventory.hydrate_from_memory(memory, 0xD31D - cls.REGION_START_ADDR)
        cls.badges = Badges.hydrate_from_memory(memory, 0xD356 - cls.REGION_START_ADDR)
        cls.location = Location.hydrate_from_memory(memory, 0xD35E - cls.REGION_START_ADDR)
        cls.events = EventFlags.hydrate_from_memory(memory, 0xD5A6 - cls.REGION_START_ADDR)
        cls.tileset_header = TilesetHeader.hydrate_from_memory(memory, 0xD52B - cls.REGION_START_ADDR)

        # Build Sprites
        sprite_base_addr = 0xC100
        sprite_incr_addr = 0x0010
        for sprite_idx in range(16):
            addr = sprite_base_addr + sprite_incr_addr * sprite_idx
            mmap.sprites.append(Sprite.hydrate_from_memory(memory, addr - cls.REGION_START_ADDR))

        # Build Pokemon
        pokemon_base_addr = 0xD16B
        pokemon_incr_addr = 0x002C
        for pokemon_idx in range(6):
            addr = pokemon_base_addr + pokemon_incr_addr * pokemon_idx
            mmap.pokemon.append(Pokemon.hydrate_from_memory(memory, addr - cls.REGION_START_ADDR))

        return mmap
