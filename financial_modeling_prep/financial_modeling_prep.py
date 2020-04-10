import requests

class FinancialModelingPrep:
    def __init__(self):
        self.base_url = "financialmodelingprep.com"

    def _version(self):
        return self.base_url + "/api/v3/"

    def _financials(self):
        return self._version + "/financials/"

    def get_income_statement(self, symbol):
        url = f"{self._financials}income-statement/{symbol.upper()}"
        response = requests.get(url)
        return response.json()

    def get_balance_sheet(self, symbol):
        url = f"{self._financials}balance-sheet-statement/{symbol.upper()}"
        response = requests.get(url)
        return response.json()

    def get_cash_flow_statement(self, symbol):
        url = f"{self._financials}cash-flow-statement/{symbol.upper()}"
        response = requests.get(url)
        return response.json()
