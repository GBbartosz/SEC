class Coalesce:
    def __init__(self):
        self.ttm_revenue_coalesce = ['ttm_Revenues',
                                     'ttm_SalesRevenueNet',
                                     'ttm_RevenueFromContractWithCustomerExcludingAssessedTax',
                                     'ttm_SalesRevenueGoodsNet']  # obliczany tylko dla odmian ttm wskaznikow z listy
        self.ttm_net_income_coalesce = ['ttm_NetIncomeLoss',
                                        'ttm_ProfitLoss']  # pamiętać o dodaniu ttm


class Indicators:
    def __init__(self, currency='USD'):
        self.summarizing_indicators = ['Revenues',
                                       'SalesRevenueNet',
                                       'RevenueFromContractWithCustomerExcludingAssessedTax',
                                       'SalesRevenueGoodsNet',
                                       'NetIncomeLoss',
                                       'ProfitLoss']

        self.not_summarizing_indicators = []
        self.coalesce = Coalesce()
        self.coalesce_indicators = list(self.coalesce.__dict__.keys())

        self.metrics_indicators = ['ttm_ProfitMargin',
                                   'ttm_ProfitMargin_3y_avg',
                                   'ttm_ProfitMargin_5y_avg',
                                   'ttm_revenue_coalesce_growth_1y',
                                   'ttm_revenue_coalesce_growth_3y',
                                   'ttm_revenue_coalesce_growth_5y',
                                   'ttm_revenue_coalesce_growth_3y_avg',
                                   'ttm_revenue_coalesce_growth_5y_avg',
                                   'ttm_net_income_coalesce_growth_1y',
                                   'ttm_net_income_coalesce_growth_3y',
                                   'ttm_net_income_coalesce_growth_5y',
                                   'ttm_net_income_coalesce_growth_3y_avg',
                                   'ttm_net_income_coalesce_growth_5y_avg']

        self.units_dict = {'Revenues': currency,
                           'SalesRevenueNet': currency,
                           'RevenueFromContractWithCustomerExcludingAssessedTax': currency,
                           'SalesRevenueGoodsNet': currency,
                           'NetIncomeLoss': currency,
                           'ProfitLoss': currency}

        self.indicators = self.summarizing_indicators + self.not_summarizing_indicators
        self.valid_indicators = []
        self.ttm_indicators = [f'ttm_{i}' for i in self.indicators]
        self.valid_ttm_indicators = []

        self.price = ['close', 'Volume']
        self.price_indicators = ['close_1y_avg',
                                 'close_3y_avg',
                                 'close_5y_avg',
                                 'market_capitalization',
                                 'market_capitalization_growth_1y',
                                 'market_capitalization_growth_3y',
                                 'market_capitalization_growth_5y',
                                 'ttm_P/E',
                                 'ttm_P/E_1y_avg',
                                 'ttm_P/E_3y_avg',
                                 'ttm_P/E_5y_avg',
                                 'ttm_PEG_historical_3y',
                                 'ttm_PEG_historical_5y',
                                 'ttm_P/S',
                                 'ttm_P/S_1y_avg',
                                 'ttm_P/S_3y_avg',
                                 'ttm_P/S_5y_avg',
                                 'ttm_PSG_historical_3y',
                                 'ttm_PSG_historical_5y']

        self.all_indicators = ['shares'] + self.price + self.ttm_indicators + self.coalesce_indicators + self.metrics_indicators + self.price_indicators
