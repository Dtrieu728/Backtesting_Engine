#contains types such as (MARKET,SIGNAL,ORDER) or FILL
class Event:
    pass 

class MarketEvent(Event):
    def __init__(self):
        self.type = 'MARKET'

class SignalEvent(Event):
    def __init__(self,symbol,datetime,signal_type,quantity):
        """_summary_

        Args:
            symbol (_type_): Ticker Symbol / company name
            datetime (_type_): Timestamp when the signal was generated
            signal_type (_type_): Long or Short
            quantity (_type_): Quantity 
        """
        self.type = 'SIGNAL'
        self.symbol = symbol
        self.datetime = datetime
        self.signal_type = signal_type
        self.quantity = quantity


class OrderEvent(Event):
    def __init__(self, symbol, order_type, quantity, direction):
        """_summary_

        Args:
            symbol (_type_): Ticker Symbol / company name
            order_type (_type_): MKT or LMT for market or limits
            quantity (_type_): Non-negative int for quantity 
            directon (_type_): Buy or Sell for long or short
        """
        
        self.type = 'ORDER'
        self.symbol = symbol
        self.order_type = order_type
        self.quantity = quantity
        self.direction = direction
        
    def print_order(self):
        """
        Outputs the vales within the order
        """
        print ("Order: Symbol=%s, Type=%s, Quantity=%s, Direction=%s" % \
            (self.symbol, self.order_type, self.quantity, self.direction))
            
class FillEvent(Event):
    def __init__(self, timeindex, symbol, exchange, quantity, direction, fill_cost, commission=None):
        """_summary_

        Args:
            timeindex (_type_): Bar resolution when the order was filled
            symbol (_type_): Ticker symbol
            exchange (_type_): The exchange where the order was filled
            quantity (_type_): The filled quantity 
            direction (_type_): The direction of fill (Buy or Sell)
            fill_cost (_type_): _description_
            commission (_type_, optional): optional commission (Interactive Broker)
        """
        
        self.type = 'FILL'
        self.timeindex = timeindex
        self.symbol = symbol
        self.exchange = exchange
        self.quantity = quantity
        self.direction = direction
        self.fill_cost = fill_cost
        self.commission = commission

        # Calc. Commission if not provided
        if self.commission is None:
            self.commission = self.calculate_ib_commission()
        else:
            self.commission = commission
            
    def calculate_ib_commission(self):
        # https://www.interactivebrokers.com/en/index.php?f=commission&p=stocks2
        full_cost = 1.3
        if self.quantity <=500:
            full_cost = max(1.3, 0.013 * self.quantity)
        else:
            full_cost = max(1.3, 0.008 * self.quantity)
        full_cost = min(full_cost, 0.5/100.0 * self.quantity * self.fill_cost)
        
        return full_cost