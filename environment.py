"""
Game Environment
"""
import typing as T

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from command import CommandClient
from memmap import MemoryMap
from reward import ActionRanges
from reward import RewardManager
from spaces import create_spaces_from_mmap
from spaces import populate_space_from_mmap
from spaces import create_reduced_space_from_mmap
from spaces import populate_reduced_space_from_mmap

if T.TYPE_CHECKING:
    from gymnasium.core import ActType
    from gymnasium.core import ObsType
    from gymnasium.core import SupportsFloat



class BlueEnvironment(gym.Env):
    """
    Primary Pokemon Blue Gym Environment
    """

    metadata = {"render_modes": ["ansi"], "render_fps": 1}

    def __init__(self, render_mode: str = "ansi", size = 5) -> None:
        self.size = size
        self._client = CommandClient('localhost', 10018)
        if not self._client._connected:
            raise ValueError("Game does not seem to be running")
        self.mmap = self.read_game_state()

        self.observation_space = create_reduced_space_from_mmap(self.mmap)

        # action space is a single dimension discrete vector
        # this is because we do not want to toggle options at the same time
        # 0: Select
        # 1: A
        # 2: B
        # 3: Up
        # 4: Left
        # 5: Down
        # 6: Right
        # 7: Start
        self.action_space = spaces.Discrete(31)

        self.reward_manager = RewardManager()

    def read_game_state(self) -> MemoryMap:
        return MemoryMap.hydrate_from_memory(self._client.do_data_command(b"dump_wram"))

    def reset(self, **kwargs) -> T.Tuple["ObsType", T.Dict[str, T.Any]]:
        super().reset(**kwargs)
        self.mmap = self.read_game_state()
        observation = populate_reduced_space_from_mmap(self.mmap)
        return (observation, {})

    def step(self, action: "ActType") -> T.Tuple["ObsType", "SupportsFloat", bool, bool, dict[str, T.Any]]:
        """
        Issue action and read state
        """
        # issue action
        button = ActionRanges.get_button(action)
        if button in "ULDR":
            # just issue it twice dammit
            self._client.dispatch(button)
        self._client.dispatch(button)

        self.mmap = self.read_game_state()
        observation = populate_reduced_space_from_mmap(self.mmap)
        reward = self.reward_manager.calculate_reward(self.mmap, action)
        terminated = False
        truncated = False
        info = dict()

        return (observation, reward, terminated, truncated, info)
