class WebnovelProfile:
    coins: int
    fastpass: int
    power_stone: int
    energy_stone: int

    fields = ['coins', 'fastpass', 'power_stone', 'energy_stone']

    def __init__(self, **kwargs):
        """
        :param kwargs: coins, fastpass, power_stone, energy_stone
        """

        # update attributes
        for key, value in kwargs.items():
            if key in self.fields:
                setattr(self, key, value)
