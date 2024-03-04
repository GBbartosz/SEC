class Coalesce:
    def __init__(self):
        self.ttm_revenue_coalesce = ['ttm_Revenues', 'ttm_SalesRevenueNet', 'ttm_RevenueFromContractWithCustomerExcludingAssessedTax']  # obliczany tylko dla odmian ttm wskaznikow z listy


class Indicators:
    def __init__(self):
        self.summarizing_indicators = ['Revenues', 'SalesRevenueNet', 'RevenueFromContractWithCustomerExcludingAssessedTax', 'NetIncomeLoss']
        self.not_summarizing_indicators = []
        self.coalesce = Coalesce()
        self.coalesce_indicators = list(self.coalesce.__dict__.keys())
        self.metrics_indicators = []

        self.units_dict = {'Revenues': 'USD',
                           'SalesRevenueNet': 'USD',
                           'RevenueFromContractWithCustomerExcludingAssessedTax': 'USD',
                           'NetIncomeLoss': 'USD'}

        self.indicators = self.summarizing_indicators + self.not_summarizing_indicators
        self.valid_indicators = []
        self.ttm_indicators = [f'ttm_{i}' for i in self.indicators]
        self.valid_ttm_indicators = []

        self.price_indicators = []
