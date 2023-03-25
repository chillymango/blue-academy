import time
import gymnasium as gym
from environment import BlueEnvironment
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env

env = BlueEnvironment()

model = PPO("MultiInputPolicy", env, verbose=1, learning_rate=0.0005)
model.learn(total_timesteps=100000, progress_bar=True)
model.save("ppo_blue")

obs, _ = env.reset()
while True:
    action, _states = model.predict(obs)
    obs, rewards, _, _, _ = env.step(action)
