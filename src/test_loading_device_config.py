from config import load_config, Config

config_path = '/Users/akashprasad/src/protocol-development/example_configs/config.centralManager.yaml'

with open( config_path, "r") as file:
    config = load_config(file)
