import io
import os
from correpy.parsers.brokerage_notes.parser_factory import ParserFactory

PDF_PASSWORD = '910'

class Ticker:
    def __init__(self, ticker, total_cost, amount):
        self.ticker = ticker
        self.total_cost = total_cost
        self.amount = amount
        self.average_traded_price = self.total_cost / self.amount

    def update_for_buy(self, total_cost, amount):
        self.total_cost += total_cost
        self.amount += amount
        self.average_traded_price = self.total_cost / self.amount

    def update_for_sell(self, amount):
        self.amount -= amount

def ticker_exists(ticker, tickers):
    for i in tickers:
        if (i.ticker == ticker): return True

    return False

def get_ticker_from_list(ticker, tickers) -> Ticker:
    for i in tickers:
        if (ticker == i.ticker): return i
     
    return None

# Itera todos os arquivos em /files e calcula o preço médio, o total gasto e a quantidade de todos os ativos negociados
# e os armazena em tickers[].
tickers = []

directory = os.fsencode('files/')
for file in os.listdir(directory):
    filename = os.fsdecode(file)
    with open('files/' + filename, 'rb') as f:

        content = io.BytesIO(f.read())
        content.seek(0)

        response = ParserFactory(brokerage_note=content, password=PDF_PASSWORD).parse()
        transactions = response[0].transactions

        for t in transactions:
            ticker = get_ticker_from_list(t.security.name, tickers)

            match t.transaction_type.name:
                case 'BUY':
                    if (ticker is None):
                        tickers.append(Ticker(t.security.name, (t.unit_price * t.amount), t.amount))
                        continue
                    ticker.update_for_buy((t.unit_price * t.amount), t.amount)
                case 'SELL':
                    if (ticker.amount == 0): 
                        tickers.remove(ticker)
                        continue
                    ticker.update_for_sell((t.unit_price * t.amount), t.amount)

for t in tickers:
    print('\n')
    print('Ticker: ' + t.ticker)
    print('Total gasto: ' + str(t.total_cost))
    print('Quantidade: ' + str(t.amount))
    print('Preço médio: ' + str(t.average_traded_price))