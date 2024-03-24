import os
import pandas as pd
from datetime import timedelta
from matplotlib import pyplot as plt
from sklearn.decomposition import PCA
from sklearn import preprocessing
from functions import pandas_df_display_options
from indicator import Indicators
import plotly.graph_objects as go
import seaborn as sns

def current_data(main_folder_path):
    processed_folder_path = f'{main_folder_path}processed_data\\'
    current_data_folder = f'{main_folder_path}current_data\\'
    files = os.listdir(processed_folder_path)

    current_df = None
    for f in files:
        ticker = f[:f.find('_')]
        stock_df = pd.read_csv(f'{processed_folder_path}{f}')
        stock_series = stock_df.ffill().iloc[-1]
        stock_series = stock_series.rename(ticker)
        if current_df is None:
            current_df = stock_series
        else:
            current_df = pd.concat([current_df, stock_series], axis=1)

    current_df = current_df.drop(['Volume',
                                  'dividends',
                                  'stock_splits'])
    current_df = current_df.T
    current_df = current_df.rename_axis('Stock')

    # print(current_df)

    current_df.to_csv(f'{current_data_folder}current_data.csv')


def correlation(main_folder_path):
    processed_folder_path = f'{main_folder_path}processed_data\\'
    correlation_folder_path = f'{main_folder_path}correlation_data\\'
    files = os.listdir(processed_folder_path)

    indicators = Indicators()
    period_years = [1, 2, 3, 5, 10, 'all']
    year_window = 252

    #for indicator in [indicators.all_indicators[0]]:
    for indicator in indicators.all_indicators:
        indicator_for_csv_file_name = indicator.replace('/', '')
        print(indicator)
        values_df = None
        for f in files:
            ticker = f[:f.find('_')]
            df = pd.read_csv(f'{processed_folder_path}{f}')[['date', indicator]]
            df[indicator] = df[indicator].bfill()
            df = df.rename(columns={indicator: ticker})

            values_df = df if values_df is None else pd.merge(values_df, df, on='date', how='outer')

        values_df['date'] = pd.to_datetime(values_df['date'])
        values_df = values_df.set_index('date')
        tickers = values_df.columns  # omitting dates

        for correlation_type in ['pearson', 'spearman']:
            for period_year in period_years:
                corr_df = pd.DataFrame(index=tickers, columns=tickers)
                for tic1 in tickers:
                    tic1_min_index = values_df[tic1].dropna().index.min()
                    tic1_max_index = values_df[tic1].dropna().index.max()
                    for tic2 in tickers:
                        if tic1 != tic2:
                            tic2_min_index = values_df[tic2].dropna().index.min()
                            tic2_max_index = values_df[tic2].dropna().index.max()
                            min_index = max(tic1_min_index, tic2_min_index)
                            max_index = min(tic1_max_index, tic2_max_index)
                            if period_year == 'all':  # correlation for all available values for both companies not nan
                                corr_calculation_df = values_df[[tic1, tic2]][min_index:max_index]  # selecting period
                                corr_calculation_df = corr_calculation_df.bfill()  # fulfilling nan values inbetween
                                correlation = corr_calculation_df[tic1].corr(corr_calculation_df[tic2], method=correlation_type)
                            else:  # correlation for selected period
                                period_ago = max_index - timedelta(days=period_year * 365)
                                if period_ago >= min_index:
                                    corr_calculation_df = values_df[(values_df.index >= period_ago) & (values_df.index <= max_index)][[tic1, tic2]]  # selecting period
                                    corr_calculation_df = corr_calculation_df.bfill()  # fulfilling nan values inbetween
                                    correlation = corr_calculation_df[tic1].corr(corr_calculation_df[tic2], method=correlation_type)
                                else:  # available data is too short compared to demanded period
                                    correlation = None
                        else:  # case when correlation AAPL: AAPL
                            correlation = 1
                        corr_df.loc[tic1, tic2] = correlation

                corr_df.to_csv(f'{correlation_folder_path}correlation_{correlation_type}_{indicator_for_csv_file_name}_{period_year}.csv')


def pca_calculation(main_folder_path):
    processed_folder_path = f'{main_folder_path}processed_data\\'
    files = os.listdir(processed_folder_path)
    #files = [files[0]]
    total_df = None
    for f in files:
        ticker = f[:f.find('_')]
        df = pd.read_csv(f'{processed_folder_path}{f}')
        df = df.dropna(subset=['end'])
        df = df.drop(['date', 'end', 'year', 'quarter'], axis=1)
        df = df.iloc[[-1]]
        df = df[['ttm_net_income_coalesce',
                 'ttm_revenue_coalesce',
                 'ttm_ProfitMargin',
                 'ttm_revenue_coalesce_growth_1y',
                 'Revenue_CAGR_3y',
                 'ttm_net_income_coalesce_growth_1y',
                 'Net_Income_CAGR_3y',
                 'ttm_P/E',
                 'ttm_P/S']]
        df.index = [ticker]
        if total_df is None:
            total_df = df
        else:
            total_df = pd.concat([total_df, df])


    total_df = total_df.dropna()
    print(total_df)
    print(total_df.info())
    scaler = preprocessing.StandardScaler()
    scaled_df = scaler.fit_transform(total_df)

    pca = PCA(n_components=2)
    X = pca.fit_transform(scaled_df)
    print(X)
    print(pca.get_feature_names_out)
    print(pca.components_)
    print(pca.explained_variance_ratio_)
    print(pca.explained_variance_)

    fig = plt.figure(figsize=(6, 6))
    plt.bar(pca.get_feature_names_out(), pca.explained_variance_ratio_)
    plt.xticks(rotation=80)
    plt.subplots_adjust(bottom=0.5)
    plt.show()

    sns.heatmap(pca.components_**2,
                    yticklabels=["PCA" + str(x) for x in range(1, pca.n_components_ + 1)],
                    xticklabels=list(total_df.columns),
                    annot=True,
                    fmt='.2f',
                    square=True,
                    linewidths=0.05)
    plt.show()

    #fig = go.Figure()
    #for i in list(range(len(X))):
    #    fig.add_trace(go.Scatter(x=[X[i][0]], y=[X[i][1]], name=total_df.index[i]))
    #fig.show()



pandas_df_display_options()
main_folder_path = 'C:\\Users\\barto\\Desktop\\SEC2024\\'
##current_data(main_folder_path)
#correlation(main_folder_path)
pca_calculation(main_folder_path)
