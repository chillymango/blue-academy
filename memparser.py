"""
Parse Pokemon State Objects from RAM
"""
import struct
import typing as T
from pydantic import BaseModel
from pydantic import PrivateAttr


TEXT_LOOKUP = {
    b'\x4F': "",
    b'\x57': "#",
    b'\x51': "*",
    b'\x52': "A1",
    b'\x53': "A2",
    b'\x54': "POKé",
    b'\x55': "+",
    b'\x58': "$",
    b'\x75': "…",
    b'\x7F': " ",
    b'\x80': "A",
    b'\x81': "B",
    b'\x82': "C",
    b'\x83': "D",
    b'\x84': "E",
    b'\x85': "F",
    b'\x86': "G",
    b'\x87': "H",
    b'\x88': "I",
    b'\x89': "J",
    b'\x8A': "K",
    b'\x8B': "L",
    b'\x8C': "M",
    b'\x8D': "N",
    b'\x8E': "O",
    b'\x8F': "P",
    b'\x90': "Q",
    b'\x91': "R",
    b'\x92': "S",
    b'\x93': "T",
    b'\x94': "U",
    b'\x95': "V",
    b'\x96': "W",
    b'\x97': "X",
    b'\x98': "Y",
    b'\x99': "Z",
    b'\x9A': "(",
    b'\x9B': ")",
    b'\x9C': ":",
    b'\x9D': ";",
    b'\x9E': "[",
    b'\x9F': "]",
    b'\xA0': "a",
    b'\xA1': "b",
    b'\xA2': "c",
    b'\xA3': "d",
    b'\xA4': "e",
    b'\xA5': "f",
    b'\xA6': "g",
    b'\xA7': "h",
    b'\xA8': "i",
    b'\xA9': "j",
    b'\xAA': "k",
    b'\xAB': "l",
    b'\xAC': "m",
    b'\xAD': "n",
    b'\xAE': "o",
    b'\xAF': "p",
    b'\xB0': "q",
    b'\xB1': "r",
    b'\xB2': "s",
    b'\xB3': "t",
    b'\xB4': "u",
    b'\xB5': "v",
    b'\xB6': "w",
    b'\xB7': "x",
    b'\xB8': "y",
    b'\xB9': "z",
    b'\xBA': "é",
    b'\xBB': "'d",
    b'\xBC': "'l",
    b'\xBD': "'s",
    b'\xBE': "'t",
    b'\xBF': "'v",
    b'\xE0': "'",
    b'\xE1': "PK",
    b'\xE2': "MN",
    b'\xE3': "-",
    b'\xE4': "'r",
    b'\xE5': "'m",
    b'\xE6': "?",
    b'\xE7': "!",
    b'\xE8': ".",
    b'\xED': "→",
    b'\xEE': "↓",
    b'\xEF': "♂",
    b'\xF0': "¥",
    b'\xF1': "x",
    b'\xF3': "/",
    b'\xF4': ",",
    b'\xF5': "♀",
    b'\xF6': "0",
    b'\xF7': "1",
    b'\xF8': "2",
    b'\xF9': "3",
    b'\xFA': "4",
    b'\xFB': "5",
    b'\xFC': "6",
    b'\xFD': "7",
    b'\xFE': "8",
    b'\xFF': "9",
}

class MemoryRegion:

    def __init__(self, label: str, addr: int, len: int = 1, type_: str = None) -> None:
        self._label = label
        self._addr = addr
        self._len = len
        self._type = type_ or "B"  # default to uint8

    @property
    def is_struct_type(self) -> bool:
        return self._type in (
            "c",
            "b",
            "B",
            "?",
            "h",
            "H",
            "i",
            "I",
            "l",
            "L",
            "q",
            "Q",
            "n",
            "N",
            "e",
            "f",
            "d",
            "s",
            "p",
            "P",
        )

    @property
    def label(self) -> str:
        return self._label

    @property
    def addr(self) -> int:
        return self._addr

    @property
    def len(self) -> int:
        if self.is_struct_type:
            return struct.calcsize(self._type)
        return self._len

    @property
    def is_text(self) -> bool:
        return self._type == "text"


class Entity(BaseModel):
    """
    This is an object that is represented in remote system memory.

    Inheriting objects should specify data fields and how they can be populated
    through reading memory fields.

    This object is capable of computing deltas so we don't need to instantiate
    anew each time.
    """

    _MAP: "AddressMap" = PrivateAttr(None)

    @classmethod
    def hydrate_from_memory(cls, memory: bytes, start_addr: int) -> "Entity":
        """
        Hydrate the entity given some memory values
        """

        # isolate the actual chunk of memory we want
        entity = cls()
        if not cls._MAP:
            print(f"Hydrating {cls.__name__} from default since no memory map was provided")
            return entity
        read_range = (start_addr, start_addr + max([reg.addr + reg.len for reg in entity._MAP._FIELDS]))
        entity.update_from_buffer(memory[read_range[0]:read_range[1]])
        return entity

    @classmethod
    def hydrate_from_buffer(cls, buffer: bytes) -> "Entity":
        """
        Hydrate the entity given the buffer of values directly corresponding to data
        """
        entity = cls()
        entity.update_from_buffer(buffer)
        return entity

    def update_from_buffer(self, buffer: bytes) -> None:
        # TODO: block reads when possible?!
        # this probably isn't significantly slower I would think, but unsure
        for field in self._MAP._FIELDS:
            value = struct.unpack(
                f">{field._type if field.is_struct_type else 'c' * field.len}",
                buffer[field.addr:field.addr + field.len]
            )

            # TODO: slooooowwwww
            if field._type == "buffer":
                value = b''.join(value)
            elif field.is_text:
                value = ''.join([TEXT_LOOKUP.get(x, " ") for x in value])
            else:
                value = value[0]

            setattr(self, field.label, value)


class AddressMap:
    """
    This specifies how to build an Entity object class.

    We generate these files manually for typing.
    """

    _FIELDS: T.List[MemoryRegion] = []
    SINGLETON = True

    # TODO: might be better to use struct.unpack

    @classmethod
    def write_class(cls) -> str:
        """
        Write the address map as a new class
        """
        kls_name = cls.__name__.replace('Map', '')
        output = f"""
class {kls_name}(Entity):
    \"\"\"
    {cls.__doc__}
    \"\"\"

    _MAP = PrivateAttr(default_factory={cls.__name__})

"""
        for field in cls._FIELDS:
            type_ = bytes if field._type == "buffer" else str if field.is_text else int
            default = 0 if type_ == int else None
            output += f"    {field.label}: {type_.__name__} = {default}\n"

        output += "\n"
        return output

    @classmethod
    def fmt_struct_unpack(cls) -> str:
        """
        Unpack struct format spec
        """
        out = "<"  # GB docs say memory is little endian
        for field in cls._FIELDS:
            if field.is_struct_type:
                out += field._type
        return out


class SpriteMap(AddressMap):

    SINGLETON = False

    _FIELDS = [
        MemoryRegion("picture_id", 0x000),
        MemoryRegion("movement_status", 0x001),
        MemoryRegion("image_idx", 0x002),
        MemoryRegion("y_screen_delta", 0x003),
        MemoryRegion("y_screen_pos", 0x004),
        MemoryRegion("x_screen_delta", 0x005),
        MemoryRegion("x_screen_pos", 0x006),
        MemoryRegion("intra_animation_frame_counter", 0x007),
        MemoryRegion("animation_frame_counter", 0x008),
        MemoryRegion("facing_direction", 0x009),
        MemoryRegion("walk_animation_counter", 0x100),
        MemoryRegion("y_displacement", 0x102),
        MemoryRegion("x_displacement", 0x103),
        MemoryRegion("y_position", 0x104),
        MemoryRegion("x_position", 0x105),
        MemoryRegion("movement_byte", 0x106),
        MemoryRegion("in_grass", 0x107),
        MemoryRegion("delay_until_next_movement", 0x108),
        MemoryRegion("sprite_image_base_offset", 0x10E)
    ]


class TileMap(AddressMap):

    _FIELDS = [
        MemoryRegion("onscreen_tiles", 0x000, 0x167, type_="buffer"),  # C3A0 to C507
        MemoryRegion("copy_buffer", 0x168, 0x0c7, type_="buffer"),  # C508 to C5CF
    ]


class MenuMap(AddressMap):

    _FIELDS = [
        MemoryRegion("y_position", 0x000),
        MemoryRegion("x_position", 0x001),
        MemoryRegion("selected_item", 0x002),
        MemoryRegion("hidden_tile", 0x003),
        MemoryRegion("last_menu_tile_id", 0x004),
        MemoryRegion("bitmask_key_port", 0x005),
        MemoryRegion("id_prev_selected_item", 0x006),
        MemoryRegion("last_cursor_position_party_bills_pc", 0x007),
        MemoryRegion("last_cursor_position_item_screen", 0x008),
        MemoryRegion("last_cursor_position_start_battle_menu", 0x009),
        MemoryRegion("index_pokemon_active", 0x00A),
        MemoryRegion("pointer_cursor_tile", 0x00B, type_="H"),
        MemoryRegion("id_displayed_menu_item", 0x00D),
        MemoryRegion("item_highlighted_select", 0x00E)
    ]


class BattleMap(AddressMap):
    """
    Starts at 0xCCD5
    """

    _FIELDS = [
        MemoryRegion("number_of_turns", 0x00),
        MemoryRegion("player_sub_hp", 0x02),
        MemoryRegion("enemy_sub_hp", 0x03),
        MemoryRegion("move_menu_type", 0x04),
        MemoryRegion("player_selected_move", 0x05),
        MemoryRegion("enemy_selected_move", 0x06),
        MemoryRegion("payday_money", 0x10, 0x03, type_="buffer"),  # this is bizarre, 24 bits?!
        MemoryRegion("opponent_escape_factor", 0x13),
        MemoryRegion("opponent_bait_factor", 0x14),
        MemoryRegion("disobedient", 0x15),
        MemoryRegion("enemy_disabled_move", 0x16),
        MemoryRegion("player_disabled_move", 0x17),
        MemoryRegion("low_health", 0x18),
        MemoryRegion("bide_damage", 0x19, 0x02),
        MemoryRegion("pokemon_atk_mod", 0x45),
        MemoryRegion("pokemon_def_mod", 0x46),
        MemoryRegion("pokemon_spd_mod", 0x47),
        MemoryRegion("pokemon_spc_mod", 0x48),
        MemoryRegion("pokemon_acc_mod", 0x49),
        MemoryRegion("pokemon_eva_mod", 0x4A),
        MemoryRegion("engaged_trainer_class", 0x58),
        MemoryRegion("enemy_atk_mod", 0x59),  # wtf is going on, double?
        MemoryRegion("enemy_def_mod", 0x5A),
        MemoryRegion("enemy_spd_mod", 0x5B),
        MemoryRegion("enemy_spc_mod", 0x5C),
        MemoryRegion("enemy_acc_mod", 0x5D),
        MemoryRegion("enemy_eva_mod", 0x5E),
    ]


class PokemonMartMap(AddressMap):
    """
    Starts at 0xCF7B
    """

    _FIELDS = [
        MemoryRegion("total_items", 0x00),
        MemoryRegion("item_1", 0x01),
        MemoryRegion("item_2", 0x02),
        MemoryRegion("item_3", 0x03),
        MemoryRegion("item_4", 0x04),
        MemoryRegion("item_5", 0x05),
        MemoryRegion("item_6", 0x06),
        MemoryRegion("item_7", 0x07),
        MemoryRegion("item_8", 0x08),
        MemoryRegion("item_9", 0x09),
        MemoryRegion("item_10", 0x0A),
    ]


class NameRaterMap(AddressMap):
    """
    Starts at 0xCF92
    """

    _FIELDS = [
        MemoryRegion("target_pokemon", 0x00)
    ]


class BattleMap2(AddressMap):
    """
    Battle is partitioned in several locations

    Starts at 0xCCDC
    """

    _FIELDS = [
        MemoryRegion("your_move_used", 0x000),
        MemoryRegion("your_move_effect", 0x2F7),
        MemoryRegion("your_move_type", 0x2F9),
    ]


class BattleMap3(AddressMap):
    """
    Battle is partitioned in several locations

    Starts at 0xCFCC
    """

    _FIELDS = [
        MemoryRegion("enemy_move_id", 0x000),
        MemoryRegion("enemy_move_effect", 0x001),
        MemoryRegion("enemy_move_power", 0x002),
        MemoryRegion("enemy_move_type", 0x003),
        MemoryRegion("enemy_move_accuracy", 0x004),
        MemoryRegion("enemy_move_max_pp", 0x005),
        MemoryRegion("player_move_id", 0x006),
        MemoryRegion("player_move_effect", 0x007),
        MemoryRegion("player_move_power", 0x008),
        MemoryRegion("player_move_type", 0x009),
        MemoryRegion("player_move_accuracy", 0x00A),
        MemoryRegion("player_move_max_pp", 0x00B),
        MemoryRegion("enemy_pokemon_id", 0x00C),
        MemoryRegion("player_pokemon_id", 0x00D),
        MemoryRegion("enemy_name", 0x00E, type_="text", len=10),
        MemoryRegion("enemy_pokemon_id2", 0x019),
        MemoryRegion("enemy_hp", 0x01A, type_="H"),
        MemoryRegion("enemy_level", 0x01C),
        MemoryRegion("enemy_status", 0x01D),
        MemoryRegion("enemy_type_1", 0x01E),
        MemoryRegion("enemy_type_2", 0x01F),
        MemoryRegion("enemy_catch_rate", 0x020),
        MemoryRegion("enemy_move_1", 0x021),
        MemoryRegion("enemy_move_2", 0x022),
        MemoryRegion("enemy_move_3", 0x023),
        MemoryRegion("enemy_move_4", 0x024),
        MemoryRegion("enemy_atk_def_dvs", 0x025),
        MemoryRegion("enemy_spd_spc_dvs", 0x026),
        MemoryRegion("enemy_level2", 0x027),
        MemoryRegion("enemy_max_hp", 0x028, type_="H"),
        MemoryRegion("enemy_atk", 0x02A, type_="H"),
        MemoryRegion("enemy_def", 0x02C, type_="H"),
        MemoryRegion("enemy_spd", 0x02E, type_="H"),
        MemoryRegion("enemy_spc", 0x030, type_="H"),
        MemoryRegion("enemy_pp_1", 0x032),
        MemoryRegion("enemy_pp_2", 0x033),
        MemoryRegion("enemy_pp_3", 0x034),
        MemoryRegion("enemy_pp_4", 0x035),
        MemoryRegion("enemy_base_stats", 0x036, type_="buffer", len=5),
        MemoryRegion("enemy_catch_rate", 0x03B),
        MemoryRegion("enemy_base_experience", 0x03C),
    ]


class BattlePokemonMap(AddressMap):
    """
    Starts at 0xD009
    """

    _FIELDS = [
        MemoryRegion("name", 0x000, 11),
        MemoryRegion("number", 0x00B),
        MemoryRegion("current_hp", 0x00C, type_="H"),
        MemoryRegion("status", 0x00F),
        MemoryRegion("type_1", 0x010),
        MemoryRegion("type_2", 0x011),
        MemoryRegion("move_1", 0x013),
        MemoryRegion("move_2", 0x014),
        MemoryRegion("move_3", 0x015),
        MemoryRegion("move_4", 0x016),
        MemoryRegion("atk_def_dvs", 0x17),
        MemoryRegion("spd_spc_dvs", 0x18),
        MemoryRegion("level", 0x019),
        MemoryRegion("max_hp", 0x01A, type_="H"),
        MemoryRegion("atk_", 0x01C, type_="H"),
        MemoryRegion("def_", 0x01E, type_="H"),
        MemoryRegion("spd_", 0x020, type_="H"),
        MemoryRegion("spc_", 0x022, type_="H"),
        MemoryRegion("pp_1", 0x024),
        MemoryRegion("pp_2", 0x025),
        MemoryRegion("pp_3", 0x026),
        MemoryRegion("pp_4", 0x027),
    ]


class BattleMap4(AddressMap):
    """
    Why is this partitioned so badly

    Starts at 0xD05A
    """

    _FIELDS = [
        MemoryRegion("battle_type", 0x00),
        MemoryRegion("critical_strike", 0x04)
    ]


class BattleStatusMap(AddressMap):
    """
    Starts at 0xD062
    """

    _FIELDS = [
        MemoryRegion("battle_status", 0x00, type_="buffer", len=3),
        MemoryRegion("stat_to_double_cpu", 0x03),
        MemoryRegion("stat_to_halve_cpu", 0x04),
        MemoryRegion("battle_status_cpu", 0x05, type_="buffer", len=3),
        MemoryRegion("player_multi_hit_move_counter", 0x08),
        MemoryRegion("player_confusion_counter", 0x09),
        MemoryRegion("player_toxic_counter", 0x0A),
        MemoryRegion("player_disable_counter", 0x0B, type_="H"),
        MemoryRegion("enemy_multi_hit_move_counter", 0x0D),
        MemoryRegion("enemy_confusion_counter", 0x0E),
        MemoryRegion("enemy_toxic_counter", 0x0F),
        MemoryRegion("enemy_disable_counter", 0x10, type_="H"),
    ]


class GameCornerMap(AddressMap):
    """
    Starts at 0xD13D
    """

    _FIELDS = [
        MemoryRegion("prize_1", 0x00),
        MemoryRegion("prize_2", 0x01),
        MemoryRegion("prize_3", 0x02),
    ]


class PlayerMap(AddressMap):
    """
    Starts at 0xD158
    """

    _FIELDS = [
        MemoryRegion("name", 0x00, type_="text", len=10),
        MemoryRegion("pokemon_in_party", 0x0B),
        MemoryRegion("pokemon_1", 0x0C),
        MemoryRegion("pokemon_2", 0x0D),
        MemoryRegion("pokemon_3", 0x0E),
        MemoryRegion("pokemon_4", 0x0F),
        MemoryRegion("pokemon_5", 0x0A),
        MemoryRegion("pokemon_6", 0x0B),
        MemoryRegion("end_of_list_huh", 0x0D)
    ]


class PokemonMap(AddressMap):
    """
    1. 0xD16B
    2. 0xD197
    3. 0xD1C3
    4. 0xD1EF
    5. 0xD21B
    6. 0xD247
    """

    _FIELDS = [
        MemoryRegion("pokemon", 0x00),
        MemoryRegion("current_hp", 0x01, type_="H"),
        MemoryRegion("int_level", 0x03),
        MemoryRegion("status", 0x04),
        MemoryRegion("type_1", 0x05),
        MemoryRegion("type_2", 0x06),
        MemoryRegion("catch_rate", 0x07),
        MemoryRegion("move_1", 0x08),
        MemoryRegion("move_2", 0x09),
        MemoryRegion("move_3", 0x0A),
        MemoryRegion("move_4", 0x0B),
        MemoryRegion("trainer_id", 0x0C, type_="H"),
        MemoryRegion("experience", 0x0E, type_="buffer", len=3),  # TODO: looks like we need to handle 3-length ints
        MemoryRegion("hp_ev", 0x11, type_="H"),
        MemoryRegion("atk_ev", 0x13, type_="H"),
        MemoryRegion("def_ev", 0x15, type_="H"),
        MemoryRegion("spd_ev", 0x17, type_="H"),
        MemoryRegion("spc_ev", 0x19, type_="H"),
        MemoryRegion("atk_def_iv", 0x1B),
        MemoryRegion("spd_spc_iv", 0x1C),
        MemoryRegion("pp_move_1", 0x1D),
        MemoryRegion("pp_move_2", 0x1E),
        MemoryRegion("pp_move_3", 0x1F),
        MemoryRegion("pp_move_4", 0x20),
        MemoryRegion("level", 0x21),
        MemoryRegion("max_hp", 0x22, type_="H"),
        MemoryRegion("atk_", 0x24, type_="H"),
        MemoryRegion("def_", 0x26, type_="H"),
        MemoryRegion("spd_", 0x28, type_="H"),
        MemoryRegion("spc_", 0x2A, type_="H"),
    ]


class PokedexCompletionMap(AddressMap):
    """
    Starts at 0xD2F7
    """

    _FIELDS = [
        MemoryRegion("caught_1_8", 0x00),
        MemoryRegion("caught_9_16", 0x01),
        MemoryRegion("caught_17_24", 0x02),
        MemoryRegion("caught_25_32", 0x03),
        MemoryRegion("caught_33_40", 0x04),
        MemoryRegion("caught_41_48", 0x05),
        MemoryRegion("caught_49_56", 0x06),
        MemoryRegion("caught_57_64", 0x07),
        MemoryRegion("caught_65_72", 0x08),
        MemoryRegion("caught_73_80", 0x09),
        MemoryRegion("caught_81_88", 0x0A),
        MemoryRegion("caught_89_96", 0x0B),
        MemoryRegion("caught_97_104", 0x0C),
        MemoryRegion("caught_105_112", 0x0D),
        MemoryRegion("caught_113_120", 0x0E),
        MemoryRegion("caught_121_128", 0x0F),
        MemoryRegion("caught_129_136", 0x10),
        MemoryRegion("caught_137_144", 0x11),
        MemoryRegion("caught_145_152", 0x12),
        MemoryRegion("seen_1_8", 0x13),
        MemoryRegion("seen_9_16", 0x14),
        MemoryRegion("seen_17_24", 0x15),
        MemoryRegion("seen_25_32", 0x16),
        MemoryRegion("seen_33_40", 0x17),
        MemoryRegion("seen_41_48", 0x18),
        MemoryRegion("seen_49_56", 0x19),
        MemoryRegion("seen_57_64", 0x1A),
        MemoryRegion("seen_65_72", 0x1B),
        MemoryRegion("seen_73_80", 0x1C),
        MemoryRegion("seen_81_88", 0x1D),
        MemoryRegion("seen_89_96", 0x1E),
        MemoryRegion("seen_97_104", 0x1F),
        MemoryRegion("seen_105_112", 0x20),
        MemoryRegion("seen_113_120", 0x21),
        MemoryRegion("seen_121_128", 0x22),
        MemoryRegion("seen_129_136", 0x23),
        MemoryRegion("seen_137_144", 0x24),
        MemoryRegion("seen_145_152", 0x25),
    ]


class InventoryMap(AddressMap):
    """
    Starts at 0xD31D
    """

    _FIELDS = [
        MemoryRegion("total_items", 0x00),
        MemoryRegion("id_item_1", 0x01),
        MemoryRegion("qty_item_1", 0x02),
        MemoryRegion("id_item_2", 0x03),
        MemoryRegion("qty_item_2", 0x04),
        MemoryRegion("id_item_3", 0x05),
        MemoryRegion("qty_item_3", 0x06),
        MemoryRegion("id_item_4", 0x07),
        MemoryRegion("qty_item_4", 0x08),
        MemoryRegion("id_item_5", 0x09),
        MemoryRegion("qty_item_5", 0x0A),
        MemoryRegion("id_item_6", 0x0B),
        MemoryRegion("qty_item_6", 0x0C),
        MemoryRegion("id_item_7", 0x0D),
        MemoryRegion("qty_item_7", 0x0E),
        MemoryRegion("id_item_8", 0x0F),
        MemoryRegion("qty_item_8", 0x10),
        MemoryRegion("id_item_9", 0x11),
        MemoryRegion("qty_item_9", 0x12),
        MemoryRegion("id_item_10", 0x13),
        MemoryRegion("qty_item_10", 0x14),
        MemoryRegion("id_item_11", 0x15),
        MemoryRegion("qty_item_11", 0x16),
        MemoryRegion("id_item_12", 0x17),
        MemoryRegion("qty_item_12", 0x18),
        MemoryRegion("id_item_13", 0x19),
        MemoryRegion("qty_item_13", 0x1A),
        MemoryRegion("id_item_14", 0x1B),
        MemoryRegion("qty_item_14", 0x1C),
        MemoryRegion("id_item_15", 0x1D),
        MemoryRegion("qty_item_15", 0x1E),
        MemoryRegion("id_item_16", 0x1F),
        MemoryRegion("qty_item_16", 0x20),
        MemoryRegion("id_item_17", 0x21),
        MemoryRegion("qty_item_17", 0x22),
        MemoryRegion("id_item_18", 0x23),
        MemoryRegion("qty_item_18", 0x24),
        MemoryRegion("id_item_19", 0x25),
        MemoryRegion("qty_item_19", 0x26),
        MemoryRegion("id_item_20", 0x27),
        MemoryRegion("qty_item_20", 0x28),
        MemoryRegion("money", 0x2A, type_="buffer", len=3),
    ]


class BadgesMap(AddressMap):
    """
    Starts at 0xD356
    """

    _FIELDS = [
        MemoryRegion("badges", 0x00)
    ]


class LocationMap(AddressMap):
    """
    This really should be called Map lol...

    Starts at 0xD35E
    """

    _FIELDS = [
        MemoryRegion("map_number", 0x00),
        MemoryRegion("event_displacement", 0x01, type_="H"),
        MemoryRegion("y_position", 0x03),
        MemoryRegion("x_position", 0x04),
        MemoryRegion("y_position2", 0x05),
        MemoryRegion("x_position2", 0x06),
        MemoryRegion("last_map_exit", 0x07),
    ]


class EventFlagsMap(AddressMap):
    """
    Starts at 0xD5A6
    """

    _FIELDS = [
        MemoryRegion("disappearing_sprites", 0x000, type_="buffer", len=31),
        MemoryRegion("starters_back", 0x005),
        MemoryRegion("have_town_map", 0x04D),
        MemoryRegion("have_oaks_parcel", 0x067),
        MemoryRegion("ss_anne_here", 0x15D),
        MemoryRegion("fossilized_pokemon", 0x16A),
        MemoryRegion("lapras_acquired", 0x188),
        MemoryRegion("fought_giovanni", 0x1AB),
        MemoryRegion("fought_brock", 0x1AF),
        MemoryRegion("fought_misty", 0x1B8),
        MemoryRegion("fought_surge", 0x1CD),
        MemoryRegion("fought_erika", 0x1D6),
        MemoryRegion("fought_articuno", 0x1DC),
        MemoryRegion("fought_koga", 0x1EC),
        MemoryRegion("fought_blaine", 0x1F4),
        MemoryRegion("fought_sabrina", 0x20D),
        MemoryRegion("fought_zapdos", 0x22E),
        MemoryRegion("fought_snorlax_vermillion", 0x230),
        MemoryRegion("fought_snorlax_celadon", 0x23A),
        MemoryRegion("fought_moltres", 0x248),
    ]


if __name__ == "__main__":
    with open("models.py", "w+") as output:
        output.write("""# This is an auto-generated file
# Oh the insane things we do for type annotations
import typing as T
from memparser import *  # TODO: wildcard imports are sus

""")
        output.write(SpriteMap.write_class())
        output.write(TileMap.write_class())
        output.write(MenuMap.write_class())
        output.write(BattleMap.write_class())
        output.write(PokemonMartMap.write_class())
        output.write(NameRaterMap.write_class())
        output.write(BattleMap2.write_class())
        output.write(BattleMap3.write_class())
        output.write(BattlePokemonMap.write_class())
        output.write(BattleMap4.write_class())
        output.write(BattleStatusMap.write_class())
        output.write(GameCornerMap.write_class())
        output.write(PlayerMap.write_class())
        output.write(PokemonMap.write_class())
        output.write(PokedexCompletionMap.write_class())
        output.write(InventoryMap.write_class())
        output.write(BadgesMap.write_class())
        output.write(LocationMap.write_class())
        output.write(EventFlagsMap.write_class())
