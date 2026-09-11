import gymnasium as gym
from gymnasium import spaces
import numpy as np
from hammurabi_env import DemocraticHammurabi

class GymDemocraticHammurabi(gym.Env):
    """
    Custom Environment that follows gymnasium interface.
    Features the 11-dimensional state and 4 continuous action channels.
    """
    metadata = {'render_modes': ['console']}

    def __init__(self, max_years=12):
        super(GymDemocraticHammurabi, self).__init__()
        self.env = DemocraticHammurabi(max_years=max_years)

        # Action space: 6 continuous values between -1 and 1:
        # [0]: Land trade [-1,1], [1]: Civ grain procure [0,1], [2]: Caravan trade [-1,1],
        # [3]: Feed fraction [0,1], [4]: Plant fraction [0,1], [5]: Project choice [0,3]
        self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(6,), dtype=np.float32)

        # Observation space: 20 features (complete Markovian state including class demographics, granaries, and silver vaults)
        self.observation_space = spaces.Box(low=0.0, high=np.inf, shape=(20,), dtype=np.float32)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        obs = self.env.reset()
        return np.array(obs, dtype=np.float32), {}

    def step(self, action):
        action_land = float(action[0])                          # [-1, 1] -> [-1, 1]
        action_civ_procure = float((action[1] + 1.0) / 2.0)    # [-1, 1] -> [0, 1]
        action_caravan_trade = float(action[2])                  # [-1, 1] -> [-1, 1]
        action_feed = float((action[3] + 1.0) / 2.0)            # [-1, 1] -> [0, 1]
        action_plant = float((action[4] + 1.0) / 2.0)           # [-1, 1] -> [0, 1]
        action_project = float((action[5] + 1.0) / 2.0) * 3.0   # [-1, 1] -> [0, 3]

        env_actions = [action_land, action_civ_procure, action_caravan_trade,
                       action_feed, action_plant, action_project]

        obs, reward, done, info = self.env.step(env_actions)
        terminated = done
        truncated = False

        return np.array(obs, dtype=np.float32), float(reward), terminated, truncated, info

    def render(self):
        print(self.env._get_state())