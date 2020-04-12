from financial_modeling_prep.constants import Constants
from .risk import Risk

class DiscountedCashFlowModel:
    def __init__(self, required_rate_of_return, years_to_project, risk, perpetual_growth_rate, margin_of_safety):
        self.required_rate_of_return = required_rate_of_return
        self.years_to_project = years_to_project
        self.risk = risk
        self.perpetual_growth_rate = perpetual_growth_rate
        self.margin_of_safety = margin_of_safety

    def calculate(self, symbol, financials, quotes):
        """
        Performs the DCF model for a specific company using historical and current
        financial data.

        Parameters
        ----------
        symbol : str
            ticker symbol
        
        financials : dict
            dictionary holding all financial data for the ticker symbol

            structure of the dict:
            {
                "income_statement": {...},
                "balance_sheet": {...},
                "cash_flow_statement: {...}
            }

        quotes : array<dict> of size 1
            dictionary holding all quote data for the ticker symbol. For some reason,
            the api returns an array always of size 1.

            structure of dict can be found in `financial_modeling_api.constants.Constants.QUOTES`
        
        Returns
        -------
        float, float
            first return is the fair value
            second return is the fair value with a margin of safety applied to it
        """
        # step 1 : combine revenue, net income, and free cash flow
        metrics = self._combine_metrics(financials)

        # step 2 : calculate percentage from FCF to Net Income
        free_cash_flow_rate_percentage = self._calculate_free_cash_flow_rate(metrics)

        # step 3 : calculate the revenue growth rate estimate
        revenue_growth_rate = self._calculate_revenue_growth_rate(metrics)

        # step 4 : calculate net income margins percentage
        net_income_margins_percentage = self._calculate_net_income_margins_percentage(metrics)

        # step 5 : apply calculated percentages from step 2, 3, and 4 to estimate future revenue, net income, and free cash flow
        future_metrics = self._estimate_future_metrics(metrics, free_cash_flow_rate_percentage, revenue_growth_rate, net_income_margins_percentage)

        # step 6 : calculate our terminal value
        terminal_value = self._calculate_terminal_value(future_metrics[-1])

        # step 7 : calculate and sum the present value of future cash flow to get today's value
        today_value = self._calculate_today_value(future_metrics, terminal_value)

        # step 8 : calculate fair value
        fair_value = self._calculate_fair_value(quotes, today_value)

        # step 9 : apply our margin of safety
        fair_with_margin_of_safety = self._apply_margin_of_safety(fair_value)

        return fair_value, fair_with_margin_of_safety

    def _combine_metrics(self, financials):
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

            revenue = float(income_year[Constants.INCOME_STATEMENT.REVENUE])
            net_income = float(income_year[Constants.INCOME_STATEMENT.NET_INCOME])
            free_cash_flow = _calculate_free_cash_flow(cash_flow_year)

            metrics.append({"year" : year, "revenue" : revenue, "net_income" : net_income, "free_cash_flow" : free_cash_flow })

        # ensure it is sorted in ascending order by year
        return sorted(metrics, key=lambda x : x["year"])

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
            revenue growth rate percentage
        """
        percentage_changes = []
        for i in range(1, len(metrics)):
            curr_cash = metrics[i]["revenue"]
            prev_cash = metrics[i - 1]["revenue"]
            change = self._percentage_change(prev_cash, curr_cash)
            percentage_changes.append(change)

        # get our growth rate depending on our risk arg
        return self._choose_percentage_based_on_risk(percentage_changes)

    def _calculate_net_income_margins_percentage(self, metrics):
        """
        Calculates the net income margins in order to estimate future net income.
        Net Income Margins = Net Income / Revenue

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
            Net Income Margin percentage chosen based on risk
        """
        net_income_margin_percentages = [float(metric["net_income"] / metric["revenue"]) for metric in metrics]

        # choose ratio to use based on risk arg
        return self._choose_percentage_based_on_risk(net_income_margin_percentages)

    def _estimate_future_metrics(self, metrics, free_cash_flow_rate_percentage, revenue_growth_rate, net_income_margins_percentage):
        """
        Estimate future revenues, net income, and free cash flow.

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

        free_cash_flow_rate_percentage : float
            rate used to estimate future free cash flow

        revenue_growth_rate : float
            rate used to estimate future revenue

        net_income_margins_percentage : float
            rate used to estimate future net income

        Returns
        -------
        array<dict>
            An aggregation of FUTURE revenue, net income, and free cash flow.

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
        def _calculate_future_revenue(metrics, revenue_growth_rate, years_to_project, apply_percentage):
            """
            Calculate the future revenue using the appropriate 
            growth rate for `years_to_project` in the future.

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

            revenue_growth_rate : float
                rate used to estimate future revenue

            years_to_project : int
                number of years in the future to project to

            apply_percentage : func
                function will apply a percentage to the passed in number

            Returns
            -------
            array<dict>
                Future projected revenues

                structure of array:
                [
                    {
                        "year": 2019,
                        "revenue": 2000
                    },
                    ...
                ]
            """
            future_revenue = []

            metric = metrics[-1]
            year = metric["year"]
            curr_revenue = metric["revenue"]
            for future_year in range(year + 1, year + years_to_project + 1):
                curr_revenue = apply_percentage(curr_revenue, revenue_growth_rate)
                future_revenue.append({"year": future_revenue, "revenue": curr_revenue})

            return future_revenue

        def _calculate_future_net_income_and_free_cash_flow(future_revenue, free_cash_flow_rate_percentage, net_income_margins_percentage):
            """
            Calculates the future net income and free cash flow based off of future revenue.

            Parameters
            ----------
            future_revenue : array<dict>
                Future projected revenues

                structure of array:
                [
                    {
                        "year": 2019,
                        "revenue": 2000
                    },
                    ...
                ]

            free_cash_flow_rate_percentage : float
                rate used to estimate future free cash flow

            net_income_margins_percentage : float
                rate used to estimate future net income

            Returns
            -------
            array<dict>
                future metrics for revenue, net income, and free cash flow

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
            future_metrics = []
            for i, estimate in enumerate(future_revenue):
                future_year = estimate["year"]
                future_revenue = estimate["revenue"]

                future_net_income = future_revenue * net_income_margins_percentage
                future_free_cash_flow = future_net_income * free_cash_flow_rate_percentage

                estimate["net_income"] = future_net_income
                estimate["free_cash_flow"] = future_free_cash_flow

                future_metrics.append(estimate)

            return future_metrics

        # get future revenues
        future_revenue = _calculate_future_revenue(metrics, revenue_growth_rate, self.years_to_project, self._add_percentage)

        # from future revenues, calculate future net income / free cash flow
        return _calculate_future_net_income_and_free_cash_flow(future_revenue, free_cash_flow_rate_percentage, net_income_margins_percentage)

    def _calculate_terminal_value(self, last_future_metric):
        """
        Calculate the terminal value based on the last future estimated
        free cash flow.

        TV = (FCF * (1 + g)) / (r - g), where
        FCF = last estimated free cash flow, 
        g = perpetual growth rate, 
        r = required rate of return

        Parameters
        ----------
        last_future_metric : dict
            dictionary containing the future year, revenue, net income, and free cash flow

            structure of dict:
            {
                "year": 2019,
                "revenue": 2000,
                "net_income": 1000,
                "free_cash_flow": 1500
            }

        Returns
        -------
        float
            the terminal value based off of the last free cash flow
        """
        fcf = last_future_metric["free_cash_flow"]
        g = float(self.perpetual_growth_rate / 100)
        r = float(self.required_rate_of_return / 100)

        return (fcf * (1 + g)) / (r - g)
            
    def _calculate_today_value(self, future_metrics, terminal_value):
        """
        Calculate today's value for the company. We must apply a discount factor
        for each future cash flow, then sum up all present value of future cash flow.

        DF = (1 + r) ^ t, where
        r = required rate of return
        t = year in the future -> 1 <= t <= `self.years_to_project`

        PV = FCF / DF

        Parameters
        ----------
        future_metrics : array<dict>
            An aggregation of FUTURE revenue, net income, and free cash flow.

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

        terminal_value : float
            terminal value based on last future free cash flow

        Returns
        -------
        float
            today's total value for the company, i.e. market cap
        """
        def _present_value(fcf, r, t):
            """
            Calculates the present value of free cash flow.

            Parameters
            ----------
            fcf : float
                free cash flow
            r : float
                required rate of return
            t : int
                time

            Returns
            -------
            float
                present value
            """
            def _discount_factor(r, t):
                """
                Calculates the discount factor.

                Parameters
                ----------
                r : float
                    required rate of return
                t : float
                    time

                Returns
                -------
                float
                    discount factor
                """
                return (1 + r) ** t
            return fcf / _discount_factor(r, t)

        r = float(self.required_rate_of_return / 100)

        # must sum our future estimates AND terminal value discounted
        present_values_future_fcf = sum([_present_value(metric["free_cash_flow"], r, i + 1) for i, metric in enumerate(future_metrics)])
        present_value_terminal = _present_value(terminal_value, r, len(future_metrics))

        # return today's value
        return present_values_future_fcf + present_value_terminal

    def _calculate_fair_value(self, quotes, today_value):
        """
        Calculates the fair value for the company.
        FV = shares / value

        Parameters
        ----------
        quotes : array<dict> of size 1
            dictionary holding all quote data for the ticker symbol. For some reason,
            the api returns an array always of size 1.

            structure of dict can be found in `financial_modeling_api.constants.Constants.QUOTES`

        Returns
        -------
        float
            fair value for the company
        """
        shares_outstanding = quotes[0][Constants.QUOTES.SHARES_OUTSTANDING]
        return float(today_value / shares_outstanding)

    def _apply_margin_of_safety(self, fair_value):
        """
        Applies a margin of safety to the fair value calculation.

        Parameters
        ----------
        fair_value : float
            fair value of the company

        Returns
        -------
        float
            fair value accounted by the margin of safety
        """
        margin_of_safety = float(self.margin_of_safety / 100)
        return self._subtract_percentage(fair_value, margin_of_safety)

    def _choose_percentage_based_on_risk(self, percentages):
        """
        Determines the percentage to use based on `self.risk`.
        
        `Conservative` risk means taking the minimum.
        `Moderate` risk means taking the average.
        `Bullish` risk means taking the maximum.

        Parameters
        ----------
        percentages : array<float>
            array representing percentages
        
        Returns
        -------
        float
            percentage to be used for calculation from caller
        """
        if self.risk == Risk.CONSERVATIVE:
            # grab the minimum percentage change
            return min(percentages)
        elif self.risk == Risk.MODERATE:
            # calculate the average of the percentages
            return sum(percentages) / len(percentages)
        else:
            # bullish estimate requires the maximum percentage change
            return max(percentages)

    def _add_percentage(self, num, percentage):
        """
        Adds the percentage change to the original number.

        Parameters
        ----------
        num : float
            number to be added to the percentage change

        percentage : float
            float value to be applied to the number

        Returns
        -------
        float
            added percentage change of `num`
        """
        return float(num + (num * percentage))

    def _subtract_percentage(self, num, percentage):
        """
        Subtracts the percentage change to the original number.

        Parameters
        ----------
        num : float
            number to be subtracted to the percentage change

        percentage : float
            float value to be applied to the number

        Returns
        -------
        float
            subtracted percentage change of `num`
        """
        return (num - (num * percentage))

    def _percentage_change(self, old, new):
        """
        Calculates the percentage change between two numbers.

        Parameters
        ----------
        old : float
            original number
        new : float
            new number
        
        Returns
        -------
        float
            percentage change from `old` to `new`
        """
        return float((new - old) / old)
