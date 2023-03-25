"""
Calculate rewards from game state
"""
from collections import Counter
from collections import defaultdict
import re
import typing as T
from memmap import MemoryMap


class ActionRanges:

    @staticmethod
    def get_button(action: int) -> str:
        DELTA = 5
        if action == 0:
            return "select"
        if action in range(1, 1 + DELTA):
            return "A"
        if action in range(1 + DELTA, 1 + 2 * DELTA):
            return "B"
        if action in range(2 * DELTA, 3 * DELTA):
            return "U"
        if action in range(3 * DELTA, 4 * DELTA):
            return "L"
        if action in range(4 * DELTA, 5 * DELTA):
            return "D"
        if action in range(5 * DELTA, 6 * DELTA):
            return "R"
        if action in range(6 * DELTA, 6 * DELTA + 1):
            return "start"


class RewardTrigger:
    """
    Specifies a condition on memory map
    """

    ONE_TIME = False

    def __init__(self) -> None:
        self._mem = None
        self.initialize()

    def initialize(self) -> None:
        """
        Child classes can override if desired
        """

    def evaluate_with_mmap(self, next_mem: MemoryMap, *args, **kwargs) -> float:
        # always fail on first evaluation
        if self._mem is None:
            self._mem = next_mem
            return 0.0
        result = self.evaluate(next_mem, *args, **kwargs)
        self._mem = next_mem
        return result

    def evaluate(self, next_mem: MemoryMap, *args, **kwargs) -> float:
        raise NotImplementedError("Inheriting classes must define")


class Dialogue(RewardTrigger):
    """
    Agent should be intrinsically curious to explore and see new text.

    If agent continues to visit the same text, should penalize.
    """

    def initialize(self) -> None:
        self._seen_dialogue = defaultdict(set)

    def evaluate(self, next_mem: MemoryMap, action: int, *args, **kwargs) -> float:
        # look at what text is currently on the screen
        # if we've never seen this combination of text before, add points
        # if we have, subtract points
        # NOTE: i think this will discourage opening the Menu so we probably
        # need a way to handle that separately???
        if ActionRanges.get_button(action) not in ("A", "B"):
            return 0.0

        if next_mem.battle.number_of_turns > 0:
            return 0.0

        text = ' '.join(next_mem.tile.onscreen_text.split())
        if not text:
            return 0.0

        valid_words = []
        for word in text.split():
            word = re.sub(r'\W+', '', word)
            if word and 'A1' not in word and 'A2' not in word and 'POKé' not in word:
                valid_words.append(word.strip())
        text = ' '.join(valid_words)

        if 'BADGES' in text or 'SAVE' in text or 'TEXT' in text:  # TODO: nasty hardcode
            return 0.0

        if text in self._seen_dialogue[next_mem.location.map_number]:
            prev_text = ' '.join(self._mem.tile.onscreen_text.split())
            if prev_text == text:
                return 0.0
            for seen in self._seen_dialogue[next_mem.location.map_number]:
                if text in seen:
                    return -5.0  # TODO: hardcoding is probably not correct???
        print(f"Have not seen {text} before")
        self._seen_dialogue[next_mem.location.map_number].add(text)
        return 25.0


class Hovering(RewardTrigger):
    """
    Issue a penalty for staying in the same 5x5 box for some time 
    """


class NewLocation(RewardTrigger):
    """
    If the agent is in a location that it has never been before, reward a small amount.
    If the agent is in a location that it has been before, do not modify reward.
    """

    def initialize(self) -> None:
        self._visited_locations: T.Dict[int, T.Dict[T.Tuple[int, int], int]] = defaultdict(lambda: defaultdict(lambda: 0))

    def evaluate(self, next_mem: MemoryMap, *args, **kwargs) -> float:
        loc_tuple = (next_mem.location.y_position, next_mem.location.x_position)
        if loc_tuple in self._visited_locations[next_mem.location.map_number]:
            self._visited_locations[next_mem.location.map_number][loc_tuple] += 1
            # NOTE: maybe after training, we don't want to evaluate it like this?
            return -1.0 / 2.0 * self._visited_locations[next_mem.location.map_number][loc_tuple]

        self._visited_locations[next_mem.location.map_number][loc_tuple] += 1
        print(f"Visited {loc_tuple} for first time")
        return 5.0


class NewRegion(RewardTrigger):
    """
    If the agent has arrived to a new map location, give a larger reward.
    """

    def initialize(self) -> None:
        self._visited_maps = set()

    def evaluate(self, next_mem: MemoryMap, *args, **kwargs) -> float:
        if next_mem.location.map_number not in self._visited_maps:
            self._visited_maps.add(next_mem.location.map_number)
            print("New Region!")
            return 500.0
        return 0.0


class EffectlessButton(RewardTrigger):
    """
    Medium penalties for clicking buttons if there's either no text
    on the screen or there previously was no text on the screen.
    """

    def evaluate(self, next_mem: MemoryMap, action: int, *args, **kwargs) -> float:
        prev_text = tuple(self._mem.tile.onscreen_text.split())
        next_text = tuple(next_mem.tile.onscreen_text.split())
        if not next_text and not prev_text and ActionRanges.get_button(action) in ("A", "B"):
            return -10.0

        if ActionRanges.get_button(action) in ("select", "start"):
            # stop spamming start / select smfh
            return -5.0
        return 0.0


class DialogInteraction(RewardTrigger):
    """
    Penalties on issuing not A or not B during text box
    """

    def evaluate(self, next_mem: MemoryMap, action: int, *args, **kwargs) -> float:
        """
        If there's real dialog on the screen and the action was not an acknowledgement,
        penalize.
        """
        text = ' '.join(next_mem.tile.onscreen_text.split())
        if not text:
            return 0.0

        valid_words = []
        for word in text.split():
            word = re.sub(r'\W+', '', word)
            if 'A1' not in word and 'A2' not in word and 'POKé' not in word:
                valid_words.append(word)
        text = ' '.join(valid_words)
        if text:
            if ActionRanges.get_button(action) not in ("A", "B"):
                return -50.0  # strong learn
        return 0.0


class Moving(RewardTrigger):
    """
    Reward for movement
    Penalties for idle
    """

    def evaluate(self, next_mem: MemoryMap, action: int, *args, **kwargs) -> float:
        prev_pos_y = self._mem.location.y_position
        prev_pos_x = self._mem.location.x_position
        curr_pos_y = next_mem.location.y_position
        curr_pos_x = next_mem.location.x_position
        if (prev_pos_y == curr_pos_y and prev_pos_x == curr_pos_x
            and ActionRanges.get_button(action) in "ULDR"):
            return -5.0
        elif prev_pos_y == curr_pos_y and prev_pos_x == curr_pos_x:
            return 0.0
        return 0.0


class CaughtPokemon(RewardTrigger):
    """
    Large reward for catching a new Popkemon
    """

    def initialize(self) -> None:
        self._pokemon_count = 0

    def evaluate(self, next_mem: MemoryMap, action: int, *args, **kwargs) -> float:
        if next_mem.player.pokemon_in_party > self._pokemon_count:
            print("Caught Pokemon!!!!")
            self._pokemon_count = next_mem.player.pokemon_in_party
            return 1000.0
        return 0.0


class StarterPokemon(RewardTrigger):

    ONE_TIME = True

    def evaluate(self, next_mem: MemoryMap, action: int, *args, **kwargs) -> float:
        if next_mem.player.pokemon_in_party == 1:
            print("CAUGHT STARTER!!!")
            return 1000.0
        return 0.0


class RewardManager:
    """
    Object is stateful so we can keep track of progress over time.

    Lots of rewards will trigger on some differential in state.
    """

    def __init__(self) -> None:
        """
        Initialize rewards management here
        """

        self._triggers_kls = [
            Dialogue,
            NewLocation,
            NewRegion,
            EffectlessButton,
            CaughtPokemon,
            Moving,
            DialogInteraction,
            StarterPokemon,
        ]
        self._triggers: T.List[RewardTrigger] = [kls() for kls in self._triggers_kls]

    def calculate_reward(self, mem: MemoryMap, action: int) -> float:
        """
        Compute the reward function
        """
        score = -1.0  # don't spend too long now...
        to_remove = []
        for trigger in self._triggers:
            evaluated = trigger.evaluate_with_mmap(mem, action)
            score += evaluated
            if evaluated and trigger.ONE_TIME:
                to_remove.append(trigger)

        for remove in to_remove:
            self._triggers.remove(remove)

        return score
