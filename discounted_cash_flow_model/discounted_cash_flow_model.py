from financial_modeling_prep.constants import Constants
from growth_rate_estimate import GrowthRateEstimate

class DiscountedCashFlowModel:
    def __init__(self, return_percentage, years_to_project, growth_rate_estimate):
        self.return_percentage = return_percentage
        self.years_to_project = years_to_project
        self.growth_rate_estimate = growth_rate_estimate

    def calculate(self, symbol, financials):
        # step 1 : calculate free cash flow for however many years of data we have
        free_cash_flow = self._calculate_free_cash_flow(symbol, financials)

        # step 2 : calculate percentage from FCF to Net Income
        fcf_to_net_income_percentage = self._calculate_fcf_to_net_income_percentage(free_cash_flow, financials)

        # step 2 : determine future revenue estimates
        free_cash_flow_with_projected_revenue = self._calculate_projected_revenue(free_cash_flow)

        # step 3 : determine future net income estimates
         

    def _calculate_free_cash_flow(self, symbol, financials):
        """
        FCF (simple) -> cash flow from operations - capex

        Parameters
        ----------
        symbol : str
            ticker symbol
        
        Returns
        -------
        array of tuples
            FCF for as many years of data the API 
            gives us in ascensing order by year.

            Structure of array:
                [
                    (2019, 200000),
                    (2018, 100000),
                    ...
                ]
        """            
        cash_flow_statement = financials[Constants.FINANCIALS.CASH_FLOW_STATEMENT]

        free_cash_flows = []
        for year_financial in cash_flow_statement["financials"]:
            date = year_financial[Constants.CASH_FLOW_STATEMENT.DATE]
            year = date.split("-")[0]
            free_cash_flow = year_financial[Constants.CASH_FLOW_STATEMENT.OPERATING_CASH_FLOW] - year_financial[Constants.CASH_FLOW_STATEMENT.CAPITAL_EXPENDITURE]
            free_cash_flows.append(int(year), float(free_cash_flow))

        # ensure it is sorted in ascending order by year
        return sorted(free_cash_flows, key=lambda tup: tup[0])

    def _calculate_fcf_to_net_income_percentage(self, free_cash_flow, financials)
        


    def _calculate_projected_revenue(self, free_cash_flow):
        """
        TODO
        """
        def _get_revenue_growth_rate_percentage(growth_rate_estimate, percentage_changes):
            """
            Based on the growth rate arg, determine the appropriate growth
            rate to use for future revenue projections

            TODO
            """
            if growth_rate_estimate == GrowthRateEstimate.CONSERVATIVE:
                # grab the minimum percentage change
                return min(percentage_changes)
            elif growth_rate_estimate == GrowthRateEstimate.MODERATE:
                # calculate the average of the percentages
                return sum(percentage_changes) / len(percentage_changes)
            else:
                # bullish estimate requires the maximum percentage change
                return max(percentage_changes)

        # calculate all of the percentage changes
        percentage_changes = []
        for i in range(1, len(free_cash_flow)):
            curr_cash = free_cash_flow[i]
            prev_cash = free_cash_flow[i - 1]
            change = self._percentage_change(prev_cash, curr_cash)
            percentage_changes.append(change)

        # get our growth rate depending on `self.growth_rate_estimate`
        growth_rate_percentage = _get_revenue_growth_rate_percentage(self.growth_rate_estimate, percentage_changes)

        # now that we have our growth rate, project the future years of revenue
        year, cash_flow = free_cash_flow[-1]
        for future_year in range(year + 1, year + self.years_to_project + 1):
            cash_flow = self._apply_percentage(cash_flow, growth_rate_percentage)
            free_cash_flow.append((future_year, cash_flow))

        return free_cash_flow

    def _apply_percentage(num, percentage):
        return float(num * percentage + num)

    def _percentage_change(old, new):
        return float((new - old) / old)
