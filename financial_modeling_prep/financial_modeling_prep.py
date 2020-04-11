import requests

class FinancialModelingPrep:
    def __init__(self):
        self.base_url = "financialmodelingprep.com"

    def get_financials(self, symbol, minimum_years):
        """
        Fetches the income, balance, and cash flow statement 
        using the given ticket symbol.

        Parameters
        ----------
        symbol : str
            ticker symbol
        minimum_years : int
            minimum amount of years of data needed 

        Returns
        -------
        dict
            dictionary holding all financial data for the ticker symbol

            structure of the dict:
            {
                "income_statement": {...},
                "balance_sheet": {...},
                "cash_flow_statement: {...}
            }
        """
        def has_more_than_minimum(minimum_years, data):
            """
            Determines if we have enough data to perform DCF calculation.

            Parameters
            ----------
            minimum_years : int
                minimum amount of years of data needed
            data : dict
                financial data

                structure of data:
                {
                    "symbol": "XYZ",
                    "financials": [
                        {...},
                        ...
                    ]
                }
            
            Returns
            -------
            bool
                true if we have enough data, false otherwise
            """
            return len(data["financials"]) >= minimum_years

        financials = {}

        income_statement_response, income_err = self._get_income_statement(symbol)
        if income_err:
            raise Exception(f"Failed to fetch income statement for ticker symbol {symbol}.")
        if not has_more_than_minimum(minimum_years, income_statement_response):
            raise Exception(f"Not enough data found in the income statement for ticker symbol {symbol}.")
        financials["income_statement"] = income_statement_response

        balance_sheet_response, balance_err = self._get_balance_sheet(symbol)
        if balance_err:
            raise Exception(f"Failed to fetch balance sheet for ticker symbol {symbol}")
        if not has_more_than_minimum(minimum_years, balance_sheet_response):
            raise Exception(f"Not enough data found in the balance sheet for ticker symbol {symbol}.")
        financials["balance_sheet"] = balance_sheet_response

        cash_flow_statement_response, cash_flow_err = self._get_cash_flow_statement(symbol)
        if cash_flow_err:
            raise Exception(f"Failed to fetch cash flow statement for ticker symbol {symbol}")
        if not has_more_than_minimum(minimum_years, cash_flow_statement_response):
            raise Exception(f"Not enough data found in the cash flow statement for ticker symbol {symbol}.")
        financials["cash_flow_statement"] = cash_flow_statement_response

        return financials

    def _version(self):
        return self.base_url + "/api/v3/"

    def _financials(self):
        return self._version + "/financials/"

    def _call_api(self, url):
        try:
            response = requests.get(url)
            return response.json(), None
        except Exception as e:
            return None, e

    def _get_income_statement(self, symbol):
        url = f"{self._financials}income-statement/{symbol.upper()}"
        return self._call_api(url)

    def _get_balance_sheet(self, symbol):
        url = f"{self._financials}balance-sheet-statement/{symbol.upper()}"
        return self._call_api(url)

    def _get_cash_flow_statement(self, symbol):
        url = f"{self._financials}cash-flow-statement/{symbol.upper()}"
        return self._call_api(url)

