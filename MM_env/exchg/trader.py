import random
import numpy as np

from .account import Account

class Trader(object):
    def __init__(self, ID, cash=0, nav=0, cash_on_hold=0, position_val=0, live_order=[], trade_rec=[], net_position=0, net_price=0):
        self.ID = ID # trader unique ID
        self.live_order = live_order # live order in LOB
        self.trade_rec = trade_rec # record of trades executed
        self.net_price = net_price # net_price paid for net_position (VWAP)
        self.acc = Account(cash, nav, cash_on_hold, position_val, net_position)

    def order_approved(self, cash, size, price):
        if self.acc.cash >= size * price:
            return True
        else:
            return False

    def create_order(self, type, side, size, price):
        if type == 'market':
            order = {'type': 'market',
                     'side': side,
                     'quantity': size,
                     'trade_id': self.ID}
        elif type == 'limit':
            order = {'type': 'limit',
                     'side': side,
                     'quantity': size,
                     'price': price,
                     'trade_id': self.ID}
        else:
            order = {}
        return order

    # pass action to step
    def select_random_action(self, exchg):
        #type = np.random.randint(0, 1, size=1) # type, draw 1 int, 0(market) to 1(limit)
        type = random.choice(['market','limit'])
        #type = random.choice(['limit'])
        #side = np.random.randint(-1, 1, size=1) # side, draw 1 int, -1(ask), 0(None), 1(bid)
        side = random.choice(['bid',None,'ask'])
        size = random.randrange(1, 100, 100) # size in 100s from 0(min) to 1000(max)
        price = random.randrange(1, 10, 1) # price from 1(min) to 100(max)
        action = {"type": type,
                  "side": side,
                  "size": size,
                  "price": price}
        return action

    def process_counter_party(self, agents, trade):
        for counter_party in agents: # search for counter_party
            if counter_party.ID == trade.get('counter_party').get('ID'):
                counter_party.acc.process_acc(trade, 'counter_party')

                counter_party.acc.print_acc()

                break

    def process_trades(self, trades, agents):
        for trade in trades:

            print('trades:', trades)

            trade_val = trade.get('quantity') * trade.get('price')
            # init_party is not counter_party
            if trade.get('counter_party').get('ID') != trade.get('init_party').get('ID'):
                self.process_counter_party(agents, trade)
                self.acc.process_acc(trade, 'init_party')

                self.acc.print_acc()

            else: # init_party is also counter_party
                # ****************************** TODO ******************************
                self.acc.cash_on_hold -= trade_val
                self.acc.cash += trade_val
        return 0

    # take or execute action
    def place_order(self, type, side, size, price, LOB, agents):
        trades, order_in_book = [],[]
        if(side == None): # do nothing to LOB
            return trades, order_in_book
        # normal execution
        if self.order_approved(self.acc.cash, size, price):
            order = self.create_order(type, side, size, price)
            if order == {}: # do nothing to LOB
                return trades, order_in_book
            trades, order_in_book = LOB.process_order(order, False, False)
            if trades != []:
                self.process_trades(trades, agents)
            self.acc.order_in_book_init_party(order_in_book) # if there's any unfilled
            return trades, order_in_book
        else: # not enough cash to place order
            print('Invalid order: order value > cash available.', trader.ID)
            return trades, order_in_book
