import io
import os
import re
from correpy.parsers.brokerage_notes.parser_factory import ParserFactory

## Altere a senha do PDF aqui. Geralmente são os últimos 3 dígitos do CPF do investidor.
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

# As notas de corretagem da B3 não são padronizadas (assim como tudo o que eles fazem).
# Por isso, é necessário: remover espaços em branco extras; e obter apenas as duas primeiras palavras de um ativo, pois o mesmo
# ativo pode ter nomes diferentes. O BOVA 11, por exemplo, pode ser ISHARES BOVA ATZ ou ISHARES BOVA.
def clean_string(s):
    white_space_removed = re.sub(r'\s+', ' ', s).strip()  # Remove espaços extras
    words = white_space_removed.split()
    return ' '.join(words[:2])  # Retorna apenas as duas primeiras palavras


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

        for transaction in response:
            for t in transaction.transactions:
              ticker = get_ticker_from_list(clean_string(t.security.name), tickers)
              print('Processando ativo ' +  clean_string(t.security.name))

              match t.transaction_type.name:
                  case 'BUY':
                      if (ticker is None):
                          tickers.append(Ticker(clean_string(t.security.name), (t.unit_price * t.amount), t.amount))
                          continue
                      ticker.update_for_buy((t.unit_price * t.amount), t.amount)
                  case 'SELL':
                      if (ticker.amount == 0): 
                          tickers.remove(ticker)
                          continue
                      ticker.update_for_sell(t.amount)

for t in tickers:
    print('\n')
    print('\033[31mTicker\033[0m: ' + t.ticker)
    print('\033[32mTotal gasto\033[0m: ' + str(t.total_cost))
    print('\033[31mQuantidade\033[0m: ' + str(t.amount))
    print('\033[32mPreço médio\033[0m: ' + str(t.average_traded_price))
