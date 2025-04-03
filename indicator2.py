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
                                   'ttm_ProfitMarginChg1y',
                                   'ttm_ProfitMarginChg2y',
                                   'ttm_ProfitMarginChg3y',
                                   'ttm_ProfitMarginChg4y',
                                   'ttm_ProfitMarginChg5y',
                                   'ttm_ProfitMargin3yAvg',
                                   'ttm_ProfitMargin5yAvg',
                                   'ttm_RevenueGrowth1y',
                                   'ttm_RevenueGrowth3y',
                                   'ttm_RevenueGrowth5y',
                                   'RevenueAAGR3y',
                                   'RevenueAAGR5y',
                                   'RevenueCAGR2y',
                                   'RevenueCAGR3y',
                                   'RevenueCAGR4y',
                                   'RevenueCAGR5y',
                                   'RevenueCAGR10y',
                                   'Future1yRevenue_Real',
                                   'Future2yRevenue_Real',
                                   'Future3yRevenue_Real',
                                   'Future4yRevenue_Real',
                                   'Future5yRevenue_Real',
                                   'Future1yRevenue_on_ttm_RevenueGrowth1y',
                                   'Future2yRevenue_on_ttm_RevenueGrowth1y',
                                   'Future3yRevenue_on_ttm_RevenueGrowth1y',
                                   'Future4yRevenue_on_ttm_RevenueGrowth1y',
                                   'Future5yRevenue_on_ttm_RevenueGrowth1y',
                                   'Future1yRevenue_on_RevenueCAGR3y',
                                   'Future2yRevenue_on_RevenueCAGR3y',
                                   'Future3yRevenue_on_RevenueCAGR3y',
                                   'Future4yRevenue_on_RevenueCAGR3y',
                                   'Future5yRevenue_on_RevenueCAGR3y',
                                   'Future1yRevenue_on_RevenueCAGR5y',
                                   'Future2yRevenue_on_RevenueCAGR5y',
                                   'Future3yRevenue_on_RevenueCAGR5y',
                                   'Future4yRevenue_on_RevenueCAGR5y',
                                   'Future5yRevenue_on_RevenueCAGR5y',
                                   'ttm_NetIncomeGrowth1y',
                                   'ttm_NetIncomeGrowth3y',
                                   'ttm_NetIncomeGrowth5y',
                                   'ttm_NetIncome_3y_mean',
                                   'ttm_NetIncome_5y_mean',
                                   'ttm_NetIncome_7y_mean',
                                   'ttm_NetIncome_10y_mean',
                                   'NetIncomeAAGR3y',
                                   'NetIncomeAAGR5y',
                                   'NetIncomeCAGR2y',
                                   'NetIncomeCAGR3y',
                                   'NetIncomeCAGR4y',
                                   'NetIncomeCAGR5y',
                                   'NetIncomeCAGR10y',
                                   'Future1yNetIncome_Real',
                                   'Future2yNetIncome_Real',
                                   'Future3yNetIncome_Real',
                                   'Future4yNetIncome_Real',
                                   'Future5yNetIncome_Real',
                                   'Future1yNetIncome_on_ttm_NetIncomeGrowth1y',
                                   'Future2yNetIncome_on_ttm_NetIncomeGrowth1y',
                                   'Future3yNetIncome_on_ttm_NetIncomeGrowth1y',
                                   'Future4yNetIncome_on_ttm_NetIncomeGrowth1y',
                                   'Future5yNetIncome_on_ttm_NetIncomeGrowth1y',
                                   'Future1yNetIncome_on_NetIncomeCAGR3y',
                                   'Future2yNetIncome_on_NetIncomeCAGR3y',
                                   'Future3yNetIncome_on_NetIncomeCAGR3y',
                                   'Future4yNetIncome_on_NetIncomeCAGR3y',
                                   'Future5yNetIncome_on_NetIncomeCAGR3y',
                                   'Future1yNetIncome_on_NetIncomeCAGR5y',
                                   'Future2yNetIncome_on_NetIncomeCAGR5y',
                                   'Future3yNetIncome_on_NetIncomeCAGR5y',
                                   'Future4yNetIncome_on_NetIncomeCAGR5y',
                                   'Future5yNetIncome_on_NetIncomeCAGR5y']

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
                                 'ttm_P/E_3y_earnings',
                                 'ttm_P/E_5y_earnings',
                                 'ttm_P/E_7y_earnings',
                                 'ttm_P/E_10y_earnings',
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
