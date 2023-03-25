# This is an auto-generated file
# Oh the insane things we do for type annotations
import typing as T
from memparser import *  # TODO: wildcard imports are sus


class Sprite(Entity):
    """
    None
    """

    _MAP = PrivateAttr(default_factory=SpriteMap)

    picture_id: int = 0
    movement_status: int = 0
    image_idx: int = 0
    y_screen_delta: int = 0
    y_screen_pos: int = 0
    x_screen_delta: int = 0
    x_screen_pos: int = 0
    intra_animation_frame_counter: int = 0
    animation_frame_counter: int = 0
    facing_direction: int = 0
    walk_animation_counter: int = 0
    y_displacement: int = 0
    x_displacement: int = 0
    y_position: int = 0
    x_position: int = 0
    movement_byte: int = 0
    in_grass: int = 0
    delay_until_next_movement: int = 0
    sprite_image_base_offset: int = 0


class Tile(Entity):
    """
    None
    """

    _MAP = PrivateAttr(default_factory=TileMap)

    onscreen_tiles: bytes = None
    onscreen_text: str = None
    copy_buffer: bytes = None
    copy_text: str = None
    total_buffer: bytes = None


class Menu(Entity):
    """
    None
    """

    _MAP = PrivateAttr(default_factory=MenuMap)

    y_position: int = 0
    x_position: int = 0
    selected_item: int = 0
    hidden_tile: int = 0
    last_menu_tile_id: int = 0
    bitmask_key_port: int = 0
    id_prev_selected_item: int = 0
    last_cursor_position_party_bills_pc: int = 0
    last_cursor_position_item_screen: int = 0
    last_cursor_position_start_battle_menu: int = 0
    index_pokemon_active: int = 0
    pointer_cursor_tile: int = 0
    id_displayed_menu_item: int = 0
    item_highlighted_select: int = 0


class Battle(Entity):
    """
    
    Starts at 0xCCD5
    
    """

    _MAP = PrivateAttr(default_factory=BattleMap)

    number_of_turns: int = 0
    player_sub_hp: int = 0
    enemy_sub_hp: int = 0
    move_menu_type: int = 0
    player_selected_move: int = 0
    enemy_selected_move: int = 0
    payday_money: bytes = None
    opponent_escape_factor: int = 0
    opponent_bait_factor: int = 0
    disobedient: int = 0
    enemy_disabled_move: int = 0
    player_disabled_move: int = 0
    low_health: int = 0
    bide_damage: int = 0
    pokemon_atk_mod: int = 0
    pokemon_def_mod: int = 0
    pokemon_spd_mod: int = 0
    pokemon_spc_mod: int = 0
    pokemon_acc_mod: int = 0
    pokemon_eva_mod: int = 0
    engaged_trainer_class: int = 0
    enemy_atk_mod: int = 0
    enemy_def_mod: int = 0
    enemy_spd_mod: int = 0
    enemy_spc_mod: int = 0
    enemy_acc_mod: int = 0
    enemy_eva_mod: int = 0


class PokemonMart(Entity):
    """
    
    Starts at 0xCF7B
    
    """

    _MAP = PrivateAttr(default_factory=PokemonMartMap)

    total_items: int = 0
    item_1: int = 0
    item_2: int = 0
    item_3: int = 0
    item_4: int = 0
    item_5: int = 0
    item_6: int = 0
    item_7: int = 0
    item_8: int = 0
    item_9: int = 0
    item_10: int = 0


class NameRater(Entity):
    """
    
    Starts at 0xCF92
    
    """

    _MAP = PrivateAttr(default_factory=NameRaterMap)

    target_pokemon: int = 0


class Battle2(Entity):
    """
    
    Battle is partitioned in several locations

    Starts at 0xCCDC
    
    """

    _MAP = PrivateAttr(default_factory=BattleMap2)

    your_move_used: int = 0
    your_move_effect: int = 0
    your_move_type: int = 0


class Battle3(Entity):
    """
    
    Battle is partitioned in several locations

    Starts at 0xCFCC
    
    """

    _MAP = PrivateAttr(default_factory=BattleMap3)

    enemy_move_id: int = 0
    enemy_move_effect: int = 0
    enemy_move_power: int = 0
    enemy_move_type: int = 0
    enemy_move_accuracy: int = 0
    enemy_move_max_pp: int = 0
    player_move_id: int = 0
    player_move_effect: int = 0
    player_move_power: int = 0
    player_move_type: int = 0
    player_move_accuracy: int = 0
    player_move_max_pp: int = 0
    enemy_pokemon_id: int = 0
    player_pokemon_id: int = 0
    enemy_name: str = None
    enemy_pokemon_id2: int = 0
    enemy_hp: int = 0
    enemy_level: int = 0
    enemy_status: int = 0
    enemy_type_1: int = 0
    enemy_type_2: int = 0
    enemy_catch_rate: int = 0
    enemy_move_1: int = 0
    enemy_move_2: int = 0
    enemy_move_3: int = 0
    enemy_move_4: int = 0
    enemy_atk_def_dvs: int = 0
    enemy_spd_spc_dvs: int = 0
    enemy_level2: int = 0
    enemy_max_hp: int = 0
    enemy_atk: int = 0
    enemy_def: int = 0
    enemy_spd: int = 0
    enemy_spc: int = 0
    enemy_pp_1: int = 0
    enemy_pp_2: int = 0
    enemy_pp_3: int = 0
    enemy_pp_4: int = 0
    enemy_base_stats: bytes = None
    enemy_catch_rate: int = 0
    enemy_base_experience: int = 0


class BattlePokemon(Entity):
    """
    
    Starts at 0xD009
    
    """

    _MAP = PrivateAttr(default_factory=BattlePokemonMap)

    name: int = 0
    number: int = 0
    current_hp: int = 0
    status: int = 0
    type_1: int = 0
    type_2: int = 0
    move_1: int = 0
    move_2: int = 0
    move_3: int = 0
    move_4: int = 0
    atk_def_dvs: int = 0
    spd_spc_dvs: int = 0
    level: int = 0
    max_hp: int = 0
    atk_: int = 0
    def_: int = 0
    spd_: int = 0
    spc_: int = 0
    pp_1: int = 0
    pp_2: int = 0
    pp_3: int = 0
    pp_4: int = 0


class Battle4(Entity):
    """
    
    Why is this partitioned so badly

    Starts at 0xD05A
    
    """

    _MAP = PrivateAttr(default_factory=BattleMap4)

    battle_type: int = 0
    critical_strike: int = 0


class BattleStatus(Entity):
    """
    
    Starts at 0xD062
    
    """

    _MAP = PrivateAttr(default_factory=BattleStatusMap)

    battle_status: bytes = None
    stat_to_double_cpu: int = 0
    stat_to_halve_cpu: int = 0
    battle_status_cpu: bytes = None
    player_multi_hit_move_counter: int = 0
    player_confusion_counter: int = 0
    player_toxic_counter: int = 0
    player_disable_counter: int = 0
    enemy_multi_hit_move_counter: int = 0
    enemy_confusion_counter: int = 0
    enemy_toxic_counter: int = 0
    enemy_disable_counter: int = 0


class GameCorner(Entity):
    """
    
    Starts at 0xD13D
    
    """

    _MAP = PrivateAttr(default_factory=GameCornerMap)

    prize_1: int = 0
    prize_2: int = 0
    prize_3: int = 0


class Player(Entity):
    """
    
    Starts at 0xD158
    
    """

    _MAP = PrivateAttr(default_factory=PlayerMap)

    name: str = None
    pokemon_in_party: int = 0
    pokemon_1: int = 0
    pokemon_2: int = 0
    pokemon_3: int = 0
    pokemon_4: int = 0
    pokemon_5: int = 0
    pokemon_6: int = 0
    end_of_list_huh: int = 0


class Pokemon(Entity):
    """
    
    1. 0xD16B
    2. 0xD197
    3. 0xD1C3
    4. 0xD1EF
    5. 0xD21B
    6. 0xD247
    
    """

    _MAP = PrivateAttr(default_factory=PokemonMap)

    pokemon: int = 0
    current_hp: int = 0
    int_level: int = 0
    status: int = 0
    type_1: int = 0
    type_2: int = 0
    catch_rate: int = 0
    move_1: int = 0
    move_2: int = 0
    move_3: int = 0
    move_4: int = 0
    trainer_id: int = 0
    experience: bytes = None
    hp_ev: int = 0
    atk_ev: int = 0
    def_ev: int = 0
    spd_ev: int = 0
    spc_ev: int = 0
    atk_def_iv: int = 0
    spd_spc_iv: int = 0
    pp_move_1: int = 0
    pp_move_2: int = 0
    pp_move_3: int = 0
    pp_move_4: int = 0
    level: int = 0
    max_hp: int = 0
    atk_: int = 0
    def_: int = 0
    spd_: int = 0
    spc_: int = 0


class PokedexCompletion(Entity):
    """
    
    Starts at 0xD2F7
    
    """

    _MAP = PrivateAttr(default_factory=PokedexCompletionMap)

    caught_1_8: int = 0
    caught_9_16: int = 0
    caught_17_24: int = 0
    caught_25_32: int = 0
    caught_33_40: int = 0
    caught_41_48: int = 0
    caught_49_56: int = 0
    caught_57_64: int = 0
    caught_65_72: int = 0
    caught_73_80: int = 0
    caught_81_88: int = 0
    caught_89_96: int = 0
    caught_97_104: int = 0
    caught_105_112: int = 0
    caught_113_120: int = 0
    caught_121_128: int = 0
    caught_129_136: int = 0
    caught_137_144: int = 0
    caught_145_152: int = 0
    seen_1_8: int = 0
    seen_9_16: int = 0
    seen_17_24: int = 0
    seen_25_32: int = 0
    seen_33_40: int = 0
    seen_41_48: int = 0
    seen_49_56: int = 0
    seen_57_64: int = 0
    seen_65_72: int = 0
    seen_73_80: int = 0
    seen_81_88: int = 0
    seen_89_96: int = 0
    seen_97_104: int = 0
    seen_105_112: int = 0
    seen_113_120: int = 0
    seen_121_128: int = 0
    seen_129_136: int = 0
    seen_137_144: int = 0
    seen_145_152: int = 0


class Inventory(Entity):
    """
    
    Starts at 0xD31D
    
    """

    _MAP = PrivateAttr(default_factory=InventoryMap)

    total_items: int = 0
    id_item_1: int = 0
    qty_item_1: int = 0
    id_item_2: int = 0
    qty_item_2: int = 0
    id_item_3: int = 0
    qty_item_3: int = 0
    id_item_4: int = 0
    qty_item_4: int = 0
    id_item_5: int = 0
    qty_item_5: int = 0
    id_item_6: int = 0
    qty_item_6: int = 0
    id_item_7: int = 0
    qty_item_7: int = 0
    id_item_8: int = 0
    qty_item_8: int = 0
    id_item_9: int = 0
    qty_item_9: int = 0
    id_item_10: int = 0
    qty_item_10: int = 0
    id_item_11: int = 0
    qty_item_11: int = 0
    id_item_12: int = 0
    qty_item_12: int = 0
    id_item_13: int = 0
    qty_item_13: int = 0
    id_item_14: int = 0
    qty_item_14: int = 0
    id_item_15: int = 0
    qty_item_15: int = 0
    id_item_16: int = 0
    qty_item_16: int = 0
    id_item_17: int = 0
    qty_item_17: int = 0
    id_item_18: int = 0
    qty_item_18: int = 0
    id_item_19: int = 0
    qty_item_19: int = 0
    id_item_20: int = 0
    qty_item_20: int = 0
    money: bytes = None


class Badges(Entity):
    """
    
    Starts at 0xD356
    
    """

    _MAP = PrivateAttr(default_factory=BadgesMap)

    badges: int = 0


class Location(Entity):
    """
    
    This really should be called Map lol...

    Starts at 0xD35E
    
    """

    _MAP = PrivateAttr(default_factory=LocationMap)

    map_number: int = 0
    event_displacement: int = 0
    y_position: int = 0
    x_position: int = 0
    y_position2: int = 0
    x_position2: int = 0
    last_map_exit: int = 0


class EventFlags(Entity):
    """
    
    Starts at 0xD5A6
    
    """

    _MAP = PrivateAttr(default_factory=EventFlagsMap)

    disappearing_sprites: bytes = None
    starters_back: int = 0
    have_town_map: int = 0
    have_oaks_parcel: int = 0
    ss_anne_here: int = 0
    fossilized_pokemon: int = 0
    lapras_acquired: int = 0
    fought_giovanni: int = 0
    fought_brock: int = 0
    fought_misty: int = 0
    fought_surge: int = 0
    fought_erika: int = 0
    fought_articuno: int = 0
    fought_koga: int = 0
    fought_blaine: int = 0
    fought_sabrina: int = 0
    fought_zapdos: int = 0
    fought_snorlax_vermillion: int = 0
    fought_snorlax_celadon: int = 0
    fought_moltres: int = 0


class TilesetHeader(Entity):
    """
    
    Starts at 0xD52B
    
    """

    _MAP = PrivateAttr(default_factory=TilesetHeaderMap)

    tileset_bank: int = 0
    pointer_to_blocks: int = 0
    pointer_to_gfx: int = 0
    pointer_to_collision_data: int = 0
    talking_over_tiles: bytes = None
    grass_tile: int = 0

