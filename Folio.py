# TODOS;
# change total invested amount to current invested amount and make a seperate total
# integrate folio with trade

class Holding:
    def __init__(self, name='', type='Equity'):
        self.name = name
        self.type = type
        self.quantity = 0
        self.total_invested = 0
        self.buy_price = []
        self.buy_quantity = []
        self.net_profit_loss = 0

    def Buy(self, quantity, price):
        self.total_invested += quantity * price
        self.quantity += quantity
        self.buy_price.append(price)
        self.buy_quantity.append(quantity)

    def Sell(self, quantity, price):
        if quantity.lower() == 'all':
            quantity = self.quantity
        elif quantity > self.quantity:
            raise ValueError(f"Not enough quantity to sell. Available: {self.quantity}, use ALL")

        self.quantity -= quantity
        remaining = quantity
        i = 0

        while remaining > 0 and i < len(self.buy_quantity):
            if self.buy_quantity[i] <= remaining:
                cost_removed = self.buy_price[i] * self.buy_quantity[i]
                self.total_invested -= cost_removed
                remaining -= self.buy_quantity[i]
                i += 1
            else:
                cost_removed = self.buy_price[i] * remaining
                self.total_invested -= cost_removed
                self.buy_quantity[i] -= remaining
                remaining = 0

        self.buy_price = self.buy_price[i:] if i < len(self.buy_price) else []
        self.buy_quantity = self.buy_quantity[i:] if i < len(self.buy_quantity) else []

        profit = quantity * price - cost_removed
        self.net_profit_loss += profit

    def Query(self, price):
        if self.quantity == 0:
            avg_price = 0
        else:
            total_qty_price = sum(p * q for p, q in zip(self.buy_price, self.buy_quantity))
            avg_price = total_qty_price / self.quantity

        print(f'Asset: {self.name}')
        print(f'Total invested amount: {self.total_invested:.2f}')
        print(f'Average buy price: {avg_price:.2f}')
        print(f'Current price: {price:.2f}')
        print(f'Current holding quantity: {self.quantity}')
        print(f'Current market value: {price * self.quantity:.2f}')
        print(f'Unrealized P/L: {price * self.quantity - self.total_invested:.2f}')
        print(f'Net realized P/L: {self.net_profit_loss:.2f}')

class Portfolio:
    def __init__(self):
        self.holdings : dict[str, Holding]= {}
    def Add(self, name, quantity, price):
        if name not in self.holdings:
            self.holdings[name] = Holding(name)
        self.holdings[name].Buy(quantity, price)
    def Sell(self, name, quantity, price):
        if name not in self.holdings:
            raise ValueError(f'Could not find {name}')
        else:
            self.holdings[name].Sell(quantity, price)
    def Query(self, name, price):
        if name.lower() == 'all':
            for k, v in self.holdings.items():
                v.Query(price)
                print('\n')

