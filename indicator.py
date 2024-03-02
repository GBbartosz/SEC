class Indicators:
    def __init__(self):
        self.summarizing_indicators = ['Revenues', 'SalesRevenueNet', 'NetIncomeLoss']
        self.not_summarizing_indicators = []

        self.units_dict = {'Revenues': 'USD',
                           'SalesRevenueNet': 'USD',
                           'NetIncomeLoss': 'USD'}

        self.indicators = self.summarizing_indicators + self.not_summarizing_indicators
        self.valid_indicators = []
