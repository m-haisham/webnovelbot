from dataclasses import dataclass


@dataclass
class WebnovelProfile:
    coins: int
    fastpass: int
    power_stone: int
    energy_stone: int

    fields = ['coins', 'fastpass', 'power_stone', 'energy_stone']
