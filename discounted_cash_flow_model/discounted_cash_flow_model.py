from financial_modeling_prep.constants import Constants

class DiscountedCashFlowModel:
    def __init__(self, return_percentage):
        self.return_percentage = return_percentage

    def calculate(self, income_statement, balance_sheet, cash_flow_statement, symbol):
        # step 1 : calculate free cash flow for however many years of data we have
        free_cash_flow = self._calculate_free_cash_flow(symbol)

        # step 2 : determine future revenue estimates

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

        # we could do warnings if we dont have say at least 4 years of data

        free_cash_flows = {}
        for year_financial in cash_flow_statement["financials"]:
            date = year_financial[Constants.CASH_FLOW_STATEMENT.DATE]
            year = date.split("-")[0]
            free_cash_flow = year_financial[Constants.CASH_FLOW_STATEMENT.OPERATING_CASH_FLOW] - year_financial[Constants.CASH_FLOW_STATEMENT.CAPITAL_EXPENDITURE]
            free_cash_flows[int(date)] = float(free_cash_flow)

        return free_cash_flows

    def _percentage_change(old, new):
        return float((new - old) / old)
