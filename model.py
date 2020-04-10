from discounted_cash_flow_model.discounted_cash_flow_model import DiscountedCashFlowModel
from financial_modeling_prep.financial_modeling_prep import FinancialModelingPrep
import argparse

class NumberAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if values < 1:
            parser.error(f"{option_string} must be greater than 0.")
        
        setattr(namespace, self.dest, values)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Use the DCF model for various companies.')
    parser.add_argument('--ticks', nargs='+', help='Specify ticker symbols (1 or more).', required=True)
    parser.add_argument('--return_percentage', action=NumberAction, help='Specify the required rate of return in terms of a percentage.', type=int, default=8)
    parser.add_argument('--minimum_years', action=NumberAction, help='Specify the minimum amount of years of data points needed to perform the DCF calculation.', type=int, default=4)
    parser.add_argument('--years_to_project', action=NumberAction, help='Specify the number of years to project future earnings.', type=int, default=4)
    args = parser.parse_args()

    print(f"Ticker symbols -> {'\t'.join(args.ticks)}")
    print(f"Required rate of return -> {args.return_percentage} %")
    print(f"Minimum amount of years of data -> {args.minimum_years} {'year' if args.minimum_years == 1 else 'years'}")
    print(f"Number of years to project future earnings -> {args.years_to_project} {'year' if args.years_to_project else 'years'}")

    api = FinancialModelingPrep()
    model = DiscountedCashFlowModel(args.return_percentage)

    for tick in args.ticks:
        print(f"Analyzing ticker symbol {tick}")

        print("Fetching financial statements...")
        income_statement = api.get_income_statement(tick)
        balance_sheet = api.get_balance_sheet(tick)
        cash_flow_statement = api.get_cash_flow_statement(tick)

        print("Calculating DCF...")
        data = model.calculate(income_statement, balance_sheet, cash_flow_statement, tick)
