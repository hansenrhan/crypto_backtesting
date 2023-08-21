import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime

def merge_and_convert_to_hourly(minute_data, hourly_data):
    # Convert timestamp column to datetime format
    minute_data['timestamp'] = pd.to_datetime(minute_data['timestamp'], format='%Y-%m-%d %H:%M:%S')
    hourly_data['timestamp'] = pd.to_datetime(hourly_data['timestamp'], format='%Y-%m-%d %H:%M:%S')

    # Filter minute_data to only include data from 2014 to 2018
    minute_data = minute_data[minute_data['timestamp'].dt.year < 2019]

    # Round minute_data timestamp to nearest hour
    minute_data['timestamp'] = minute_data['timestamp'].dt.floor('H')

    # Find the latest timestamp in minute_data
    latest_minute_timestamp = minute_data['timestamp'].max()

    # Filter hourly_data to only include data from after the latest timestamp in minute_data
    hourly_data = hourly_data[hourly_data['timestamp'] > latest_minute_timestamp]

    # Combine the two dataframes
    combined_data = pd.concat([minute_data, hourly_data])

    # Drop any duplicates
    combined_data = combined_data.drop_duplicates(subset='timestamp', keep='last')

    # Sort by timestamp
    combined_data = combined_data.sort_values('timestamp')

    # Set the timestamp column as the index
    combined_data = combined_data.set_index('timestamp')

    # Resample to hourly data
    combined_data = combined_data.resample('H').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    })

    # Reset the index
    combined_data = combined_data.reset_index()

    return combined_data

def add_quarter_annotation(crypto_df):
    # add quarters to the data

    # Make sure the 'Datetime' column is in datetime format
    crypto_df['Datetime'] = pd.to_datetime(crypto_df['timestamp'])

    # Calculate the start date and year of the first entry
    start_date = crypto_df['Datetime'].min()
    start_year = start_date.year

    # Create a function to calculate the quarter
    def calculate_quarter(row):
        months_passed = (row['Datetime'].year - start_year) * 12 + row['Datetime'].month - start_date.month
        return (months_passed // 3) + 1

    # Apply the function to create the 'quarter' column
    crypto_df['quarter'] = crypto_df.apply(calculate_quarter, axis=1)
    
    # make sure the quarter assignments look right...
    return crypto_df


def get_bitcoin_data(years):
    """
    Gets bitcoin price data for a set number of years

    Arguments:
        years: list of years 
    Returns:
        crypto_df: pandas dataframe of price data
    """

    # validation step
    valid_years = [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]

    if not years:
        raise Exception("No years provided")
    for year in years:
        if year not in valid_years:
            raise Exception(year, "is not available, please select a year from 2014-2023.")


    # Load 1 min BTC data from 2013 to 2019

    # handle minute data from 2014 to 2019
    df2019 = pd.read_csv("BTC_1min_bitfinex/2019.txt", header=None)
    df2018 = pd.read_csv("BTC_1min_bitfinex/2018.txt", header=None)
    df2017 = pd.read_csv("BTC_1min_bitfinex/2017.txt", header=None)
    df2016 = pd.read_csv("BTC_1min_bitfinex/2016.txt", header=None)
    df2015 = pd.read_csv("BTC_1min_bitfinex/2015.txt", header=None)
    df2014 = pd.read_csv("BTC_1min_bitfinex/2014.txt", header=None)

    # handle hourly data from 2018 to 2023
    df2018_2023 = pd.read_csv("BTC_1min_bitfinex/2018_2023.csv", skiprows=[0])
    df2018_2023['volume'] = df2018_2023['Volume USD']
    df2018_2023['timestamp'] = df2018_2023['date']
    df2018_2023.drop(['unix', 'symbol', 'Volume BTC', 'Volume USD', 'date'], axis=1, inplace=True)

    # removed 2013 data
    #df2013 = pd.read_csv("BTC_1min_bitfinex/2013.txt", header=None)
    #frames = [df2013, df2014, df2015, df2016, df2017, df2018, df2019]

    frames = [df2014, df2015, df2016, df2017, df2018, df2019]

    crypto_df = pd.concat(frames)
    crypto_df.rename(columns = {0: 'timestamp', 1: 'open', 2: 'close', 3: 'high', 4: 'low', 5: 'volume'}, inplace=True)

    # Convert UTC timestamp to readable 
    crypto_df['timestamp'] = [datetime.utcfromtimestamp(int(ts)/1000).strftime('%Y-%m-%d %H:%M:%S') for ts in crypto_df['timestamp']]


    crypto_df = merge_and_convert_to_hourly(crypto_df, df2018_2023)

    # fitler out, only select the dates that we want

    # Extract the year from the timestamp
    crypto_df['year'] = crypto_df['timestamp'].dt.year

    #Filter the rows with years in the list
    filtered_crypto_df = crypto_df[crypto_df['year'].isin(years)]

    # Drop the 'year' column if you don't need it anymore
    filtered_crypto_df = filtered_crypto_df.drop(columns='year')

    # add quarter information to it
    filtered_crypto_df = add_quarter_annotation(filtered_crypto_df)

    return filtered_crypto_df

def plot_quarterly_data(backtest_results):
    '''
    Visualize quarterly data from a backtest run.

    Parameters:
        backtest_results: dict generated by sma_crossover_backtester()
    Returns:
        None
    '''

    from matplotlib import rcParams
    rcParams['figure.figsize'] = 15,8
    
    quarterly_data = pd.DataFrame()
    quarterly_data['quarter'] = [x + 1 for x in range(0, len(backtest_results["quarter_return_rates"]))]
    quarterly_data['return'] = [x*100 for x in backtest_results["quarter_return_rates"]]
    quarterly_data['trades'] = backtest_results["quarter_trades"]
    quarterly_data['hit_rate'] = backtest_results["quarter_hit_rates"]
    quarterly_data['baseline'] = [x*100 for x in backtest_results["baseline_return_rates"]]

    # Hit Rate
    # if there are NAs in the hit rate, ignore it.
    if 'N/A' not in backtest_results['quarter_hit_rates']:
        clrs = ['green' if (x > 0) else 'red' for x in quarterly_data['return']]
        graph = sns.barplot(x="quarter",y="hit_rate",data=quarterly_data,palette=clrs)
        #Drawing a horizontal line at 0.5
        graph.axhline(0.5)
        plt.show()

    # Returns
    clrs = ['green' if (x > 0) else 'red' for x in quarterly_data['return']]
    graph = sns.barplot(x="quarter",y="return",data=quarterly_data,palette=clrs)
    plt.show()

    # Number of trades
    graph = sns.barplot(x="quarter",y="trades",data=quarterly_data,palette=clrs)
    plt.show()

    # Comparing quarterly returns
    comparison_df = pd.DataFrame()
    comparison_df['Return (%)']  = list(quarterly_data['return']) + list(quarterly_data['baseline'])
    comparison_df['Quarter'] = [x for x in quarterly_data['quarter']] + [x for x in quarterly_data['quarter']]
    comparison_df['Strategy'] = ["Mean Reversion" for x in quarterly_data['quarter']] + ["Buy and Hold" for x in quarterly_data['quarter']]

    sns.barplot(data=comparison_df, x='Quarter', y='Return (%)', hue='Strategy')
    plt.show()