import requests
import json

class FinancialModelingPrep:
    def __init__(self, logger):
        self.base_url = "https://financialmodelingprep.com"
        self.logger = logger

    def get_quotes(self, symbol):
        """
        Fetches quote data for a company.

        Parameters
        ----------
        symbol : str
            ticker symbol

        Returns
        -------
        array<dict> of size 1
            dictionary holding all quote data for the ticker symbol. For some reason,
            the api returns an array always of size 1.

            structure of dict can be found in `financial_modeling_api.constants.Constants.QUOTES`
        """
        self.logger.debug("--- FinancialModelingPrep.get_quotes ---")

        url = f"{self._version()}quote/{symbol.upper()}"

        self.logger.debug(f"url -> {url}")

        quote_response, err = self._call_api(url)
        if err:
            raise Exception(f"Failed to fetch quote data for ticker symbol {symbol}.")

        self.logger.debug(f"quote_response -> {json.dumps(quote_response, indent=2)}\n")

        return quote_response

    def get_financials(self, symbol, minimum_years, maximum_years):
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
        def _has_more_than_minimum(minimum_years, data):
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
        
        def _cut_data_to_maximum_years(maximum_years, data):
            """
            Cuts the data to the maximum amount of years specified.

            Parameters
            ----------
            maximum_years : int
                max years of historical data to use

            data : dict
                financial data from api call

                structure of dict:
                {
                    "symbol": "AAPL",
                    "financials": [
                        {...},
                        ...
                    ]
                }

            Returns
            -------
            dict
                data input modified

                structure of dict:
                {
                    "symbol": "AAPL",
                    "financials": [
                        {...},
                        ...
                    ]
                }
            """
            financials = data["financials"]
            cut_financials = financials[:maximum_years] if maximum_years < len(financials) else financials
            data["financials"] = cut_financials
            return data

        self.logger.debug("--- FinancialModelingPrep.get_financials ---")

        financials = {}

        income_statement_response, income_err = self._get_income_statement(symbol)
        if income_err:
            raise Exception(f"Failed to fetch income statement for ticker symbol {symbol}.")
        if not _has_more_than_minimum(minimum_years, income_statement_response):
            raise Exception(f"Not enough data found in the income statement for ticker symbol {symbol}.")
        financials["income_statement"] = _cut_data_to_maximum_years(maximum_years, income_statement_response)
        
        self.logger.debug(f"income_statement_response -> {json.dumps(financials['income_statement'], indent=2)}\n")

        balance_sheet_response, balance_err = self._get_balance_sheet(symbol)
        if balance_err:
            raise Exception(f"Failed to fetch balance sheet for ticker symbol {symbol}")
        if not _has_more_than_minimum(minimum_years, balance_sheet_response):
            raise Exception(f"Not enough data found in the balance sheet for ticker symbol {symbol}.")
        financials["balance_sheet"] = _cut_data_to_maximum_years(maximum_years, balance_sheet_response)

        self.logger.debug(f"balance_sheet_response -> {json.dumps(financials['balance_sheet'], indent=2)}\n")

        cash_flow_statement_response, cash_flow_err = self._get_cash_flow_statement(symbol)
        if cash_flow_err:
            raise Exception(f"Failed to fetch cash flow statement for ticker symbol {symbol}")
        if not _has_more_than_minimum(minimum_years, cash_flow_statement_response):
            raise Exception(f"Not enough data found in the cash flow statement for ticker symbol {symbol}.")
        financials["cash_flow_statement"] = _cut_data_to_maximum_years(maximum_years, cash_flow_statement_response)

        self.logger.debug(f"cash_flow_statement_response -> {json.dumps(financials['cash_flow_statement'], indent=2)}\n")

        return financials

    def _version(self):
        """
        Combines the `self.base_url` with the API version.

        Returns
        -------
        str
            base url + api version
        """
        return self.base_url + "/api/v3/"

    def _financials(self):
        """
        Combines the `self._version` with financials.

        Returns
        -------
        str
            base url + version + financials
        """
        return self._version() + "/financials/"

    def _call_api(self, url):
        """
        Performs a GET request using the requests module.

        Parameters
        ----------
        url : str
            url to be called

        Returns
        -------
        dict, Exception
            dict represents the json response coming from the api call. if there is an error, this will be None.
            Exception is an error object where if the api call is successful, this will be none
        """
        try:
            response = requests.get(url)
            return response.json(), None
        except Exception as e:
            return None, e

    def _get_income_statement(self, symbol):
        """
        Makes a GET request for the income statement using the ticker symbol.

        Parameters
        ----------
        symbol : str
            ticker symbol

        Returns
        -------
        dict, Exception
            dict represents the json response coming from the api call. if there is an error, this will be None.
            Exception is an error object where if the api call is successful, this will be none
        """
        self.logger.debug("--- FinancialModelingPrep._get_income_statement ---")

        url = f"{self._financials()}income-statement/{symbol.upper()}"
        self.logger.debug(f"url -> {url}")

        return self._call_api(url)

    def _get_balance_sheet(self, symbol):
        """
        Makes a GET request for the balance sheet statement using the ticker symbol.

        Parameters
        ----------
        symbol : str
            ticker symbol

        Returns
        -------
        dict, Exception
            dict represents the json response coming from the api call. if there is an error, this will be None.
            Exception is an error object where if the api call is successful, this will be none
        """
        self.logger.debug("--- FinancialModelingPrep._get_balance_sheet ---")

        url = f"{self._financials()}balance-sheet-statement/{symbol.upper()}"
        self.logger.debug(f"url -> {url}")

        return self._call_api(url)

    def _get_cash_flow_statement(self, symbol):
        """
        Makes a GET request for the cash flow statement using the ticker symbol.

        Parameters
        ----------
        symbol : str
            ticker symbol

        Returns
        -------
        dict, Exception
            dict represents the json response coming from the api call. if there is an error, this will be None.
            Exception is an error object where if the api call is successful, this will be none
        """
        self.logger.debug("--- FinancialModelingPrep._get_cash_flow_statement ---")

        url = f"{self._financials()}cash-flow-statement/{symbol.upper()}"
        self.logger.debug(f"url -> {url}")

        return self._call_api(url)

