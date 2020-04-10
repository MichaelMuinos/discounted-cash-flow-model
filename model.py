from discounted_cash_flow_model.discounted_cash_flow_model import DiscountedCashFlowModel
from financial_modeling_prep.financial_modeling_prep import FinancialModelingPrep
import argparse

class NumberAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if values < 1:
            parser.error(f"{option_string} must be greater than 0.")
        
        setattr(namespace, self.dest, values)

class GrowthRateEstimateAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if values not in ["conservative", "moderate", "bullish"]:
            parser.error(f"{option_string} must be 1 of the 3 following options...\n1. conservative\n2. moderate\n3. bullish")

        setattr(namespace, self.dest, values)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Use the DCF model for various companies.')
    parser.add_argument('--ticks', nargs='+', help='Specify ticker symbols (1 or more).', required=True)
    parser.add_argument('--return_percentage', action=NumberAction, help='Specify the required rate of return in terms of a percentage.', type=int, default=8)
    parser.add_argument('--minimum_years', action=NumberAction, help='Specify the minimum amount of years of data points needed to perform the DCF calculation.', type=int, default=4)
    parser.add_argument('--years_to_project', action=NumberAction, help='Specify the number of years to project future earnings.', type=int, default=4)
    parser.add_argument('--growth_rate_estimate', action=GrowthRateEstimateAction, help='Specify the type of estimation you would like to do. Choose between `conservative` (minimum percentage change), `moderate` (average percentage change), or `bullish` (max percentage change).', default='conservative')
    args = parser.parse_args()

    print(f"Ticker symbols -> {'\t'.join(args.ticks)}")
    print(f"Required rate of return -> {args.return_percentage} %")
    print(f"Minimum amount of years of data -> {args.minimum_years} {'year' if args.minimum_years == 1 else 'years'}")
    print(f"Number of years to project future earnings -> {args.years_to_project} {'year' if args.years_to_project == 1 else 'years'}")
    print(f"Growth rate estimation -> {args.growth_rate_estimate}")

    api = FinancialModelingPrep()
    model = DiscountedCashFlowModel(args.return_percentage, args.years_to_project)

    for tick in args.ticks:
        print(f"Analyzing ticker symbol {tick}")

        print("Fetching financial statements...")
        financials = api.get_financials(symbol, args.minimum_years)

        print("Calculating DCF...")
        data = model.calculate(tick, financials)
