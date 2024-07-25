import io
from correpy.parsers.brokerage_notes.parser_factory import ParserFactory

PDF_PASSWORD = '910'

class Ticker:
    def __init__(self, ticker, total_cost, amount):
        self.ticker = ticker
        self.total_cost = total_cost
        self.amount = amount
        self.average_traded_price = self.total_cost / self.amount

    def update_average_price(self, total_cost, amount):
        self.total_cost += total_cost
        self.amount += amount
        self.average_traded_price = self.total_cost / self.amount

def ticker_exists(ticker, tickers):
    for i in tickers:
        if (i.ticker == ticker): return True

    return False

def get_ticker_from_list(ticker, tickers):
    for i in tickers:
        if (ticker == i): return i
     
    return None

with open('files/NotaCorretagem.pdf', 'rb') as f:
    tickers = []

    content = io.BytesIO(f.read())
    content.seek(0)
    
    response = ParserFactory(brokerage_note=content, password=PDF_PASSWORD).parse()
    transactions = response[0].transactions

    for t in transactions:
        if (not ticker_exists(t.security.name, tickers)):
            tickers.append(Ticker(t.security.name, (t.unit_price * t.amount), t.amount))
            continue

        ticker = get_ticker_from_list(t.security.name, tickers)
        ticker.update_average_price((t.unit_price * t.amount), t.amount)
