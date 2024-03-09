class Coalesce:
    def __init__(self):
        self.ttm_revenue_coalesce = ['ttm_Revenues',
                                     'ttm_SalesRevenueNet',
                                     'ttm_RevenueFromContractWithCustomerExcludingAssessedTax']  # obliczany tylko dla odmian ttm wskaznikow z listy


class Indicators:
    def __init__(self):
        self.summarizing_indicators = ['Revenues',
                                       'SalesRevenueNet',
                                       'RevenueFromContractWithCustomerExcludingAssessedTax',
                                       'NetIncomeLoss']

        self.not_summarizing_indicators = []
        self.coalesce = Coalesce()
        self.coalesce_indicators = list(self.coalesce.__dict__.keys())

        self.metrics_indicators = ['ttm_ProfitMargin',
                                   'ttm_revenue_coalesce_growth_1y']

        self.units_dict = {'Revenues': 'USD',
                           'SalesRevenueNet': 'USD',
                           'RevenueFromContractWithCustomerExcludingAssessedTax': 'USD',
                           'NetIncomeLoss': 'USD'}

        self.indicators = self.summarizing_indicators + self.not_summarizing_indicators
        self.valid_indicators = []
        self.ttm_indicators = [f'ttm_{i}' for i in self.indicators]
        self.valid_ttm_indicators = []

        self.price = ['close', 'Volume']
        self.price_indicators = ['close_1y_avg',
                                 'close_3y_avg',
                                 'close_5y_avg',
                                 'market_capitalization',
                                 'ttm_P/E',
                                 'ttm_P/E_1y_avg',
                                 'ttm_P/E_3y_avg',
                                 'ttm_P/E_5y_avg'
                                 'ttm_P/S',
                                 'ttm_P/S_1y_avg',
                                 'ttm_P/S_3y_avg',
                                 'ttm_P/S_5y_avg']

        self.all_indicators = self.price + self.ttm_indicators + self.coalesce_indicators + self.metrics_indicators + self.price_indicators
