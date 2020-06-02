from dataclasses import dataclass


@dataclass
class Profile:
    coins: int = None
    fastpass: int = None
    power_stone: int = None
    energy_stone: int = None

    fields = ['coins', 'fastpass', 'power_stone', 'energy_stone']
