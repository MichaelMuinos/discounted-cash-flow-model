from financial_modeling_prep.constants import Constants
from risk import Risk

class DiscountedCashFlowModel:
    def __init__(self, return_percentage, years_to_project, risk):
        self.return_percentage = return_percentage
        self.years_to_project = years_to_project
        self.risk = risk

    def calculate(self, symbol, financials):
        # step 1 : combine revenue, net income, and free cash flow
        metrics = self._combine_metrics(financials)

        # step 2 : calculate percentage from FCF to Net Income
        free_cash_flow_rate_percentage = self._calculate_free_cash_flow_rate(fcf_and_net_income)

        # step 3 : calculate the revenue growth rate estimate
        revenue_growth_rate = self._calculate_revenue_growth_rate(metrics)

        # step 4 : apply revenue growth rate to add future revenue estimates to our metrics
        metrics = self._calculate_future_revenue(metrics, revenue_growth_rate)

        # step 4 : calculate net income margins percentage

        # step 5 : calculate future net income estimates

        # step 6 : calculate future free cash flow estimates

        free_cash_flow_with_projected_revenue = self._calculate_projected_revenue(free_cash_flow)

    def _combine_metrics(financials):
        """
        Combines the revenue, net income, and free cash flow using the income
        and cash flow statement.

        Parameters
        ----------
        financials : dict
            api data coming directly from `financial_modeling_prep.py`

            structure of dict:
            {
                "income_statement": {...},
                "balance_sheet": {...},
                "cash_flow_statement": {...}
            }

        Returns
        -------
        array<dict>
            An aggregation of revenue, net income, and free cash flow for all available data.
            Array is sorted in ascending order by year

            structure of array:
            [
                {
                    "year": 2019,
                    "revenue": 2000,
                    "net_income": 1000,
                    "free_cash_flow": 1500
                },
                ...
            ]
        """
        def _calculate_free_cash_flow(cash_flow_year):
            """
            Calculates free cash flow using the cash flow statement.
            FCF = Cash Flow from Operations - Capex

            Parameters
            ----------
            cash_flow_year : dict
                cash flow metrics from the financials

            Returns
            -------
            float
                free cash flow calculation
            """
            return float(cash_flow_year[Constants.CASH_FLOW_STATEMENT.OPERATING_CASH_FLOW]) - float(cash_flow_year[Constants.CASH_FLOW_STATEMENT.CAPITAL_EXPENDITURE])

        income_statement = financials[Constants.FINANCIALS.INCOME_STATEMENT]
        cash_flow_statement = financials[Constants.FINANCIALS.CASH_FLOW_STATEMENT]

        metrics = []
        for income_year, cash_flow_year in zip(income_statement["financials"], cash_flow_statement["financials"]):
            date = income_year[Constants.INCOME_STATEMENT.DATE]
            year = int(date.split("-")[0])

            revenue = float(income_statement[Constants.INCOME_STATEMENT.REVENUE])
            net_income = float(income_statement[Constants.INCOME_STATEMENT.NET_INCOME])
            free_cash_flow = _calculate_free_cash_flow(cash_flow_year)

            metrics.append({"year" : year, "revenue" : revenue, "net_income" : net_income, "free_cash_flow" : free_cash_flow })

        # ensure it is sorted in ascending order by year
        return sorted(metrics, lambda x : x["year"])

    def _calculate_free_cash_flow_rate(self, metrics):
        """
        Calculates the free cash flow rate based on historical FCF and net income.
        FCFR = FCF / Net Income

        Parameters
        ----------
        metrics : array<dict>
            An aggregation of revenue, net income, and free cash flow for all available data.
            Array is sorted in ascending order by year

            structure of array:
            [
                {
                    "year": 2019,
                    "revenue": 2000,
                    "net_income": 1000,
                    "free_cash_flow": 1500
                },
                ...
            ]

        Returns
        -------
        float
            free cash flow rate to be used
        """
        ratios = [float(metric["free_cash_flow"] / metric["net_income"]) for metric in metrics]

        # choose ratio to use based on risk arg
        return self._choose_percentage_based_on_risk(ratios)

    def _calculate_revenue_growth_rate(self, metrics):
        """
        Calculates the revenue growth rate to project future earnings. It is 
        calculated based on `self.risk`.

        Parameters
        ----------
        metrics : array<dict>
            An aggregation of revenue, net income, and free cash flow for all available data.
            Array is sorted in ascending order by year

            structure of array:
            [
                {
                    "year": 2019,
                    "revenue": 2000,
                    "net_income": 1000,
                    "free_cash_flow": 1500
                },
                ...
            ]

        Returns
        -------
        float
            Revenue growth rate percentage
        """
        percentage_changes = []
        for i in range(1, len(metrics)):
            curr_cash = metrics[i]["revenue"]
            prev_cash = metrics[i - 1]["revenue"]
            change = self._percentage_change(prev_cash, curr_cash)
            percentage_changes.append(change)

        # get our growth rate depending on our risk arg
        return self._choose_percentage_based_on_risk(percentage_changes)

    def _calculate_future_revenue(self, metrics, revenue_growth_rate):
 
    def _calculate_projected_revenue(self, metrics):
        """
        TODO
        """
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

    def _choose_percentage_based_on_risk(percentages):
        if self.risk == Risk.CONSERVATIVE:
            # grab the minimum percentage change
            return min(percentages)
        elif self.risk == Risk.MODERATE:
            # calculate the average of the percentages
            return sum(percentages) / len(percentages)
        else:
            # bullish estimate requires the maximum percentage change
            return max(percentages)

    def _apply_percentage(self, num, percentage):
        return float(num * percentage + num)

    def _percentage_change(self, old, new):
        return float((new - old) / old)
