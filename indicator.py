class Coalesce:
    def __init__(self):
        self.revenue = ['Revenues', 'SalesRevenueNet', 'RevenueFromContractWithCustomerExcludingAssessedTax']


class Indicators:
    def __init__(self):
        self.summarizing_indicators = ['Revenues', 'SalesRevenueNet', 'RevenueFromContractWithCustomerExcludingAssessedTax', 'NetIncomeLoss']
        self.coalesce = Coalesce()
        self.not_summarizing_indicators = []

        self.units_dict = {'Revenues': 'USD',
                           'SalesRevenueNet': 'USD',
                           'RevenueFromContractWithCustomerExcludingAssessedTax': 'USD',
                           'NetIncomeLoss': 'USD'}

        self.indicators = self.summarizing_indicators + self.not_summarizing_indicators
        self.valid_indicators = []

