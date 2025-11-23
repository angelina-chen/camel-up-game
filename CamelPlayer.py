class CamelPlayer:
    def __init__(self, name: str, starting_money: int = 3):
        self.name = name
        self.amount_of_money = starting_money
        self.bets = list()
        self.is_ai = True if self.name.lower() == "ai" else False #chec if AI player
        pass
    def __str__(self):
        return self.name
