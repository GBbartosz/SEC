class Indicators2:
    def __init__(self, currency='USD'):

        self.summarizing_indicators_to_download = ['Revenue',
                                                   'NetIncome']
        self.not_summarizing_indicators_to_download = []
        self.indicators_to_download = self.summarizing_indicators_to_download + self.not_summarizing_indicators_to_download

        # used in dataprocessing
        self.summarizing_indicators = ['Revenue',
                                       'NetIncome']
        #self.not_summarizing_indicators = ['Revenue',  # quarterly
        #                                   'NetIncome']  # quarterly
        self.not_summarizing_indicators = []

        self.metrics_indicators = ['SharesChg1q',
                                   'SharesChg1y',
                                   'SharesChg3y',
                                   'SharesChg5y',
                                   'ttm_ProfitMargin',
                                   'ttm_ProfitMargin3yAvg',
                                   'ttm_ProfitMargin5yAvg',
                                   'ttm_RevenueGrowth1y',
                                   'ttm_RevenueGrowth3y',
                                   'ttm_RevenueGrowth5y',
                                   'RevenueAAGR3y',
                                   'RevenueAAGR5y',
                                   'RevenueCAGR3y',
                                   'RevenueCAGR5y',
                                   'ttm_NetIncomeGrowth1y',
                                   'ttm_NetIncomeGrowth3y',
                                   'ttm_NetIncomeGrowth5y',
                                   'NetIncomeAAGR3y',
                                   'NetIncomeAAGR5y',
                                   'NetIncomeCAGR3y',
                                   'NetIncomeCAGR5y']

        self.indicators = self.summarizing_indicators + self.not_summarizing_indicators
        self.valid_indicators = []
        self.ttm_indicators = [f'ttm_{i}' for i in self.indicators]
        self.valid_ttm_indicators = []

        self.price = ['close', 'Volume']

        self.price_indicators = ['PriceChangeDaily',
                                 'close_1y_avg',
                                 'close_3y_avg',
                                 'close_5y_avg',
                                 'price_to_1y_avg_ratio',
                                 'price_to_3y_avg_ratio',
                                 'price_to_5y_avg_ratio',
                                 'market_capitalization',
                                 'market_capitalization_growth_1y',
                                 'market_capitalization_growth_3y',
                                 'market_capitalization_growth_5y',
                                 'ttm_P/E',
                                 'ttm_P/E_1y_avg',
                                 'ttm_P/E_3y_avg',
                                 'ttm_P/E_5y_avg',
                                 'ttm_PE_to_1y_ratio',
                                 'ttm_PE_to_3y_ratio',
                                 'ttm_PE_to_5y_ratio',
                                 'ttm_PEG_historical_3y',
                                 'ttm_PEG_historical_5y',
                                 'ttm_P/S',
                                 'ttm_P/S_1y_avg',
                                 'ttm_P/S_3y_avg',
                                 'ttm_P/S_5y_avg',
                                 'ttm_PS_to_1y_ratio',
                                 'ttm_PS_to_3y_ratio',
                                 'ttm_PS_to_5y_ratio',
                                 'ttm_PSG_historical_3y',
                                 'ttm_PSG_historical_5y']
        self.all_indicators = ['Shares'] + self.price + self.summarizing_indicators + self.ttm_indicators + self.metrics_indicators + self.price_indicators
        #self.all_indicators = ['shares']

        self.alerts = ['Price < 3 year average',
                       'Price < 5 year average',
                       'ProfitMargin > 3 year average',
                       'ProfitMargin > 5 year average',
                       'P/E < 3 year average',
                       'P/E < 5 year average',
                       'P/S < 3 year average',
                       'P/S < 5 year average']

        self.correlation_indicators_daily = ['PriceChangeDaily',
                                             'ttm_P/S',
                                             'ttm_P/E']

        self.correlation_indicators_quarterly = ['ttm_RevenueGrowth1y',
                                                 'ttm_NetIncomeGrowth1y']
