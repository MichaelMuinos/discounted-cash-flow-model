from financial_modeling_prep.api_constants import Constants

class DiscountedCashFlowModel:
    def __init__(self, financial_modeling_prep_api):
        self.financial_modeling_prep_api = financial_modeling_prep_api

    def calculate(self, ticker_symbols):
        if ticker_symbols is None or len(ticker_symbols) == 0:
            raise Exception("No ticker symbols given!")

        return [self._calculate(symbol) for symbol in ticker_symbols]

    def _calculate(self, symbol):
        # step 1: calculate free cash flow for however many years of data we have


    def _calculate_free_cash_flow(self, symbol):
        """
        FCF (simple) -> cash flow from operations - capex

        Parameters
        ----------
        symbol : str
            ticker symbol
        
        Returns
        -------
        dict
            FCF for as many years of data the API gives us.

            Structure of dict:
                {
                    2019 : 200000,
                    2018 : 100000,
                    ...
                }
        """            
        cash_flow_statement = self.financial_modeling_prep_api.get_cash_flow_statement(symbol)

        free_cash_flows = {}
        for year_financial in cash_flow_statement["financials"]:
            date = year_financial[Constants.CASH_FLOW_STATEMENT.DATE]
            free_cash_flow = year_financial[Constants.CASH_FLOW_STATEMENT.OPERATING_CASH_FLOW] - year_financial[Constants.CASH_FLOW_STATEMENT.CAPITAL_EXPENDITURE]
            free_cash_flows[date] = free_cash_flow

        return free_cash_flows
