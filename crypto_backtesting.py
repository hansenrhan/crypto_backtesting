import random
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import statistics 
import numpy as np
from concurrent.futures import ProcessPoolExecutor
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


def mean_reversion_backtester(sampled_data, 
                            order_sizing, 
                            ma_length, 
                            starting_capital,
                            buy_threshold,
                            take_profit,
                            stop_loss,
                            shorting_allowed,
                            fixed_fee,
                            display_results,
                            record_balance,
                            show_moving_averages,
                            annual_taxes,
                            tax_percentage = 0,
                            fee=0
                            ):
    """ 
    Parameters:
        sampled_data: pandas dataframe that must have columns 'timestamp' and 'price'
        order_sizing: how much of available capital to use on a given trade (betwen 0 and 1)
        ma_length: moving average length (in hours)
        starting_capital: how much capital to start with (USD)
        buy_threshold: at what % below the moving average to buy (if 5%, should be 0.05)
        take_profit: at what % gain to sell and take the profit (if 5%, should be 0.05)
        stop_loss: at what % to sell and stop losses (if 5%, should be 0.05)
        shorting_allowed: whether or not to short or sell regularly (true or false)
        fee: the % charged per transaction by the exchange (in %, so 0.01 = 1%)
        record_balance: whether or not to track the balance over the whole period
        show_moving_averages: whether or not to show the moving averages in the plot displayed (true or false)
        annual_taxes: whether or not to take annual taxes on gains (true or false)
        tax_percentage: if taxes are enabled, what % of taxes to pay on gains (0.01 = 1%), default = 0
    Returns:
        backtest_results: dictionary that contains backtest result metrics and balance information 
    """

    # for figuring out how much a fee is
    # we are taking the average of maker and taker fees on coinbase pro starting on 6/5/23
    def find_fee(thirty_day_volume):
        volume_fee_table = {
            10000: 0.005,
            50000: 0.00325,
            100000: 0.002,
            1000000: 0.0015,
            15000000: 0.0013,
            75000000: 0.0011,
            250000000: 0.00075,
            400000000: 0.0004,
        }
        
        for volume, fee in volume_fee_table.items():
            if thirty_day_volume <= volume:
                return fee
        
        # If the volume is greater than the largest key, return the fee for the largest key
        return volume_fee_table[400000000]
    
    
    # Ensure inputs are valid
    if "timestamp" not in sampled_data.columns:
        return "Could not run ma_crossover_backtester(), 'timestamp' column missing from data."
    if "price" not in sampled_data.columns:
        return "Could not run ma_crossover_backtester(), 'price' column missing from data."
    if starting_capital <= 0:
        return "Could not run ma_crossover_backtester(), starting_capital must be greater than zero."
    if order_sizing > 1 or order_sizing <= 0:
        return "Could not run ma_crossover_backtester(), order_sizing must be between 1 and 0."
    
    
    fiat = starting_capital
    position_size = 0
    baseline_position_size = 0
    portfolio_balance = [] #keeps track of the total portfolio worth
    baseline_balance = [] #keeps track of the buy and hold balance
    moves = [] #keep track of buys and sells
    trades = 0
    purchase_price = 0
    wins = 0
    losses = 0

    # setup for keeping track of quarterly results
    three_month_hours = 2191
    one_month_hours = 730 #actually 730.5 
    quarter_numbers = []
    quarter_return_rates = []
    quarter_trades = []
    quarter_hit_rates = []
    baseline_return_rates = []

    monthly_return_rates = []

    # calculate the total number of quarters in the dataset
    total_quarters = max(list(sampled_data['quarter']))
    # total_months = math.floor(len(sampled_data.index)/one_month_hours)

    # calculate quarter intervals
    # quarter_intervals = [three_month_hours*x for x in range(0, total_quarters)]
    # monthly_intervals = [one_month_hours*x for x in range(0, total_months)]

    # convert to get the corresponding timestamps
    # quarter_intervals = [crypto_df.iloc[x]['timestamp'] for x in quarter_intervals]
    # monthly_intervals = [crypto_df.iloc[x]['timestamp'] for x in monthly_intervals]
    
    current_price = sampled_data['price'][0]
    baseline_position_size = starting_capital/current_price
    baseline_initial = current_price

    ma = sampled_data.price.rolling(ma_length).mean()

    #truncate the data so they all are aligned 
    ma = list(ma[ma_length:])
    sampled_data = sampled_data[ma_length:]
    last_average_higher = "None"

    # set up shorting mechanism
    short_position = None
    short_results = []

    # set up volume data
    thirty_day_volume = 0
    volume_data = []

    # set up tax information, when the year changes, we check if we gained or lost for the year, and then put that aside for taxes
    sampled_data['timestamp'] = pd.to_datetime(sampled_data['timestamp'])

    past_year = sampled_data.iloc[0]['timestamp'].year
    annual_change = 0
    past_quarter = 1
    
    #now run through each moment in the data and check if there is a crossover
    for x in range(0, len(sampled_data['price'])):

        # calculate the fee using the thirty_day_volume
        if not fixed_fee:
            fee = find_fee(thirty_day_volume)

        #get the current price
        current_price = sampled_data.iloc[x]['price']
        current_quarter = sampled_data.iloc[x]['quarter']

        if x == 0:
            #baseline_initial = current_price
            #baseline_position_size = starting_capital/current_price
            quarter_initial = current_price

            monthly_initial_balance = starting_capital
            quarter_initial_balance = starting_capital
            quarter_baseline_initial_balance = starting_capital

            annual_baseline_balance = starting_capital
        
        # if the year has changed, calculate how much has happened
        if annual_taxes == True:
            current_year = sampled_data.iloc[x]['timestamp'].year
            if current_year != past_year:
                # the year has changed
                if short_position == True:
                    short_delta = (purchase_price*position_size - current_price*position_size)
                    current_balance = (purchase_price*position_size + short_delta + fiat)
                else:
                    current_balance = current_price*position_size + fiat

                annual_change = current_balance - annual_baseline_balance

                # if we had a gain that year, you need to pay taxes
                if annual_change > 0:
                    taxes_due = annual_change*tax_percentage
                    
                    # if currently holding a position, will need to sell some of it to make up for the taxes...(since fiat is probably low)
                    if position_size != 0:
                        taxes_due = annual_change*tax_percentage - fiat #use all fiat first
                        amount_to_sell = taxes_due/current_price # find out how many shares will cover the amount due
                        position_size = position_size - amount_to_sell # reduce that many shares from the amount due
                    else:
                        fiat = fiat - taxes_due
                
                # reset the new amount
                annual_baseline_balance = position_size*current_price + fiat
            
            past_year = current_year
        
        # if a new month begins, calculate the return for that month (for sharpe ratio calculations)
        # if sampled_data.iloc[x]['timestamp'] in monthly_intervals:
        #     monthly_return_rate = ((fiat + current_price*position_size)/monthly_initial_balance) - 1
        #     monthly_return_rates.append(monthly_return_rate)
        #     monthly_initial_balance = fiat + current_price*position_size

        # If a new quarter begins, calculate metrics for the quarter
        if current_quarter != past_quarter:
            quarter_return_rate = ((fiat + current_price*position_size)/quarter_initial_balance) - 1
            quarter_return_rates.append(quarter_return_rate)
            quarter_trades.append(trades)
            baseline_return_rate = ((baseline_position_size*current_price)/quarter_baseline_initial_balance) - 1
            baseline_return_rates.append(baseline_return_rate)

            if (losses + wins) > 0:
                hit_rate = wins/(losses + wins)
            else:
                hit_rate = "N/A"

            quarter_hit_rates.append(hit_rate)

            # reset initial price for the quarter
            quarter_initial = current_price

            # reset number of trades, losses, wins
            trades = 0
            losses = 0
            wins = 0

            # calculate the new initial portfolio worth to be used for the new quarter
            quarter_initial_balance = fiat + current_price*position_size
            quarter_baseline_initial_balance = current_price*baseline_position_size

        past_quarter = current_quarter
            
        #keep track of which one was higher previously
        if x == 0:
            last_move = "Pass"

        else:
            #begin the trading mechanism

            #if the price dips below a set % from the moving average - BUY
            if last_move != "Buy" and current_price <= ma[x]*(1-buy_threshold):
                if shorting_allowed == True:
                    if short_position == True:
                        # if there is a short position, exit out of it
                        short_delta = (purchase_price*position_size - current_price*position_size) # calculate the delta for the short
                        short_results.append(short_delta)
                        fiat = fiat + (purchase_price*position_size + short_delta)*(1 - fee) # sell the position and the short
                        position_size = 0 # set the position to zero
                    short_position = False 

                #add the btc amount to the position
                position_size = position_size + (order_sizing*fiat*(1 - fee))/current_price #add the btc purchased
                fiat = fiat - order_sizing*fiat #subtract the amount of capital used
                last_move = "Buy"
                trades = trades + 1
                purchase_price = current_price

            #if the take profit or stop loss threshold is crossed - SELL
            elif last_move == "Buy" and (current_price >= ma[x]*(1+take_profit) or current_price <=ma[x]*(1-stop_loss)):
                fiat = fiat + position_size*current_price*(1 - fee)
                position_size = 0

                if shorting_allowed == True:
                    position_size = (order_sizing*fiat*(1 - fee))/current_price
                    fiat = fiat - position_size*current_price
                    last_move = "Short-Sell"
                    short_position = True
                    purchase_price = current_price
                else:
                    last_move = "Sell"
                    # reset the purchase price
                    purchase_price = 0

                trades = trades + 1

                # record whether the trade was profitable
                if purchase_price < current_price:
                    wins = wins + 1 
                else:
                    losses = losses + 1
                
            else:
                pass
                #moves.append("Pass")
        
        if shorting_allowed == True:
            #record the portfolio information
            if short_position == False or short_position == None:
                if record_balance == True:
                    portfolio_balance.append(position_size*current_price + fiat)
            if short_position == True:
                short_delta = (purchase_price*position_size - current_price*position_size)
                if record_balance == True:
                    portfolio_balance.append(purchase_price*position_size + short_delta + fiat)
        else:
            #record the portfolio information
            if record_balance == True:
                portfolio_balance.append(position_size*current_price + fiat)
            
        if record_balance == True:
            baseline_balance.append(baseline_position_size*current_price)

        # go through the volume data
        thirty_day_volume = 0 # re-calculate the current thirty_day_volume
        new_volume_data = []
        for volume_data_entry in volume_data:
            if volume_data_entry[0] < 720: # 720 hours in thirty days
                thirty_day_volume = thirty_day_volume + volume_data_entry[1]
                new_volume_data.append([volume_data_entry[0] + 1, volume_data_entry[1]])
        
        volume_data = new_volume_data
        
    
    # compute final results
    baseline_final = current_price
    baseline_return_rate = (baseline_final/baseline_initial) - 1  
    final_return_rate = ((position_size*current_price + fiat)/starting_capital) - 1
    if (losses + wins) > 0:
        hit_rate = wins/(losses + wins)
    else:
        hit_rate = "N/A"

    # calculate sharpe ratio (using 0% as the risk-free return benchmark)
    #sharpe_ratio = (statistics.mean(monthly_return_rates)-0)/(statistics.stdev(monthly_return_rates)*np.sqrt(12))
    sharpe_ratio = None

    if display_results == True and record_balance == True:
        plot_data = pd.DataFrame()
        plot_data['time'] = sampled_data['timestamp']
        plot_data['Mean Reversion'] = portfolio_balance
        plot_data['Baseline'] = baseline_balance
        plot_data.plot(x = "time")
        plt.xticks(rotation="vertical")
        plt.show()
    else:
        plot_data = "Could not generate plot_data: display_results and/or record_balance was set to False."

    # calculate quarters_beating_baseline
    count = 0
    for x in range(0, len(quarter_return_rates)):
        # we round so that a difference of 0.0000000001, etc. won't bring it over the edge.
        if round(quarter_return_rates[x],2) > round(baseline_return_rates[x],2):
            count = count + 1

    quarters_beating_baseline = round(count/len(quarter_return_rates), 2)

    # return the results
    backtest_results = {"final_return_rate" : final_return_rate,
               "hit_rate": hit_rate,
               "baseline_return_rate": baseline_return_rate,
               "quarter_return_rates": quarter_return_rates, 
               "quarter_trades": quarter_trades,
               "quarter_hit_rates": quarter_hit_rates,
               "baseline_return_rates": baseline_return_rates,
               "balance_data": plot_data,
               "sharpe_ratio": sharpe_ratio,
                "quarters_beating_baseline": quarters_beating_baseline,
               "strategy_quarterly_stdev": statistics.stdev(quarter_return_rates),
               "baseline_quarterly_stdev": statistics.stdev(baseline_return_rates)

    }
    
    return backtest_results


def sma_crossover_backtester(sampled_data, 
                            order_sizing, 
                            ma1_length, 
                            ma2_length, 
                            starting_capital,
                            display_results,
                            shorting_allowed,
                            fixed_fee,
                            record_balance,
                            show_moving_averages,
                            annual_taxes,
                            tax_percentage = 0,
                            fee=0
                            ):
    """ 
    Parameters:
        sampled_data: pandas dataframe that must have columns 'timestamp' and 'price'
        order_sizing: how much of available capital to use on a given trade (betwen 0 and 1)
        ma1_length: moving average 1 length (in hours)
        ma2_length: moving average 2 length (in hours, must be longer than ma1_length)
        starting_capital: how much capital to start with (USD)
        display_results: plot the portfolio value over time (true or false)
        shorting_allowed: whether or not to short or sell regularly (true or false)
        fixed_fee: whether to use volume based fee or a fixed fee (true or false)
        fee: if fixed fee, the % charged per transaction by the exchange (0.01 = 1%), default = 0
        record_balance: whether or not to track the balance over the whole period
        show_moving_averages: whether or not to show the moving averages in the plot displayed (true or false)
        annual_taxes: whether or not to take annual taxes on gains (true or false)
        tax_percentage: if taxes are enabled, what % of taxes to pay on gains (0.01 = 1%), default = 0
    Returns:
        backtest_results: dictionary that contains backtest result metrics and balance information 
    """

    # for figuring out how much a fee is
    # we are taking the average of maker and taker fees on coinbase pro starting on 6/5/23
    def find_fee(thirty_day_volume):
        volume_fee_table = {
            10000: 0.005,
            50000: 0.00325,
            100000: 0.002,
            1000000: 0.0015,
            15000000: 0.0013,
            75000000: 0.0011,
            250000000: 0.00075,
            400000000: 0.0004,
        }
        
        for volume, fee in volume_fee_table.items():
            if thirty_day_volume <= volume:
                return fee
        
        # If the volume is greater than the largest key, return the fee for the largest key
        return volume_fee_table[400000000]

    
    import math 
    import statistics 
    import numpy as np
    from matplotlib import rcParams
    rcParams['figure.figsize'] = 15,8
    
    # Ensure inputs are valid
    if "timestamp" not in sampled_data.columns:
        return "Could not run ma_crossover_backtester(), 'timestamp' column missing from data."
    if "price" not in sampled_data.columns:
        return "Could not run ma_crossover_backtester(), 'price' column missing from data."
    if ma2_length < ma1_length:
        return "Could not run ma_crossover_backtester(), ma1_length is larger than ma2_length."
    if starting_capital <= 0:
        return "Could not run ma_crossover_backtester(), starting_capital must be greater than zero."
    if order_sizing > 1 or order_sizing <= 0:
        return "Could not run ma_crossover_backtester(), order_sizing must be between 1 and 0."
    
    
    fiat = starting_capital
    position_size = 0
    baseline_position_size = 0
    portfolio_balance = [] #keeps track of the total portfolio worth
    baseline_balance = [] #keeps track of the buy and hold balance
    moves = [] #keep track of buys and sells
    trades = 0
    purchase_price = 0
    wins = 0
    losses = 0

    # setup for keeping track of quarterly results
    three_month_hours = 2191
    one_month_hours = 730 #actually 730.5 
    quarter_numbers = []
    quarter_return_rates = []
    quarter_trades = []
    quarter_hit_rates = []
    baseline_return_rates = []

    monthly_return_rates = []

    # calculate the total number of quarters in the dataset
    # calculate the total number of quarters in the dataset
    total_quarters = max(list(sampled_data['quarter']))
    # total_quarters = math.floor(len(sampled_data.index)/three_month_hours)
    # total_months = math.floor(len(sampled_data.index)/one_month_hours)

    # # calculate quarter intervals
    # quarter_intervals = [three_month_hours*x for x in range(0, total_quarters)]
    # monthly_intervals = [one_month_hours*x for x in range(0, total_months)]

    # # convert to get the corresponding timestamps
    # quarter_intervals = [sampled_data.iloc[x]['timestamp'] for x in quarter_intervals]
    # monthly_intervals = [sampled_data.iloc[x]['timestamp'] for x in monthly_intervals]
    
    current_price = sampled_data['price'][0]
    baseline_position_size = starting_capital/current_price
    baseline_initial = current_price

    ma1 = sampled_data.price.rolling(ma1_length).mean()
    ma2 = sampled_data.price.rolling(ma2_length).mean()

    #truncate the data so they all are aligned 
    ma1 = list(ma1[ma2_length:])
    ma2 = list(ma2[ma2_length:])
    sampled_data = sampled_data[ma2_length:]
    last_average_higher = "None"

    # set up shorting mechanism
    short_position = None
    short_results = []

    # set up volume data
    thirty_day_volume = 0
    volume_data = []

    # set up tax information, when the year changes, we check if we gained or lost for the year, and then put that aside for taxes
    sampled_data['timestamp'] = pd.to_datetime(sampled_data['timestamp'])

    past_year = sampled_data.iloc[0]['timestamp'].year
    annual_change = 0
    past_quarter = 1
    
    #now run through each moment in the data and check if there is a crossover
    for x in range(0, len(sampled_data['price'])):

        # calculate the fee using the thirty_day_volume
        if not fixed_fee:
            fee = find_fee(thirty_day_volume)

        #get the current price
        current_price = sampled_data.iloc[x]['price']
        current_quarter = sampled_data.iloc[x]['quarter']

        if x == 0:
            #baseline_initial = current_price
            #baseline_position_size = starting_capital/current_price
            quarter_initial = current_price

            monthly_initial_balance = starting_capital
            quarter_initial_balance = starting_capital
            quarter_baseline_initial_balance = starting_capital

            annual_baseline_balance = starting_capital

        # if the year has changed, calculate how much has happened
        if annual_taxes == True:
            current_year = sampled_data.iloc[x]['timestamp'].year
            if current_year != past_year:
                # the year has changed
                if short_position == True:
                    short_delta = (purchase_price*position_size - current_price*position_size)
                    current_balance = (purchase_price*position_size + short_delta + fiat)
                else:
                    current_balance = current_price*position_size + fiat

                annual_change = current_balance - annual_baseline_balance

                # if we had a gain that year, you need to pay taxes
                if annual_change > 0:
                    taxes_due = annual_change*tax_percentage
                    
                    # if currently holding a position, will need to sell some of it to make up for the taxes...(since fiat is probably low)
                    if position_size != 0:
                        taxes_due = annual_change*tax_percentage - fiat #use all fiat first
                        amount_to_sell = taxes_due/current_price # find out how many shares will cover the amount due
                        position_size = position_size - amount_to_sell # reduce that many shares from the amount due
                    else:
                        fiat = fiat - taxes_due
                
                # reset the new amount
                annual_baseline_balance = position_size*current_price + fiat
            
            past_year = current_year
        
        # if a new month begins, calculate the return for that month (for sharpe ratio calculations)
        # if sampled_data.iloc[x]['timestamp'] in monthly_intervals:
        #     monthly_return_rate = ((fiat + current_price*position_size)/monthly_initial_balance) - 1
        #     monthly_return_rates.append(monthly_return_rate)
        #     monthly_initial_balance = fiat + current_price*position_size

        # If a new quarter begins, calculate metrics for the quarter
        if current_quarter != past_quarter:
            quarter_return_rate = ((fiat + current_price*position_size)/quarter_initial_balance) - 1
            quarter_return_rates.append(quarter_return_rate)
            quarter_trades.append(trades)
            baseline_return_rate = ((baseline_position_size*current_price)/quarter_baseline_initial_balance) - 1
            baseline_return_rates.append(baseline_return_rate)

            if (losses + wins) > 0:
                hit_rate = wins/(losses + wins)
            else:
                hit_rate = "N/A"

            quarter_hit_rates.append(hit_rate)

            # reset initial price for the quarter
            quarter_initial = current_price

            # reset number of trades, losses, wins
            trades = 0
            losses = 0
            wins = 0

            # calculate the new initial portfolio worth to be used for the new quarter
            quarter_initial_balance = fiat + current_price*position_size
            quarter_baseline_initial_balance = current_price*baseline_position_size
        
        past_quarter = current_quarter
            
        #keep track of which one was higher previously
        if ma1[x] > ma2[x]:
            current_average_higher = "MA1"
        elif ma1[x] < ma2[x]:
            current_average_higher = "MA2"
        else:
            current_average_higher = "None"

        if x == 0:
            pass
            #moves.append("Pass")
        else:
            #begin the trading mechanism

            #if the shorter average crosses over the longer average - BUY
            if current_average_higher == "MA1" and last_average_higher == "MA2":
                if shorting_allowed == True:
                    if short_position == True:
                        # if there is a short position, exit out of it
                        short_delta = (purchase_price*position_size - current_price*position_size) # calculate the delta for the short
                        short_results.append(short_delta)
                        fiat = fiat + (purchase_price*position_size + short_delta)*(1 - fee) # sell the position and the short
                        position_size = 0 # set the position to zero
                    
                    short_position = False


                #add the btc amount to the position
                position_size = position_size + (order_sizing*fiat*(1 - fee))/current_price #add the btc purchased
                
                # record the volume information (the amount purchased)
                volume_data.append([
                    0,(order_sizing*fiat*(1 - fee))/current_price
                ])

                fiat = fiat - order_sizing*fiat #subtract the amount of capital used
                #moves.append("Buy")
                trades = trades + 1
                purchase_price = current_price

                

            #if the shorter average goes under the longer average - SELL
            elif current_average_higher == "MA2" and last_average_higher == "MA1":
                fiat = fiat + position_size*current_price*(1 - fee)
                position_size = 0

                # record the volume information (the amount sold)
                volume_data.append([
                    0,position_size*current_price*(1 - fee)
                ])

                if shorting_allowed == True:
                    position_size = (order_sizing*fiat*(1 - fee))/current_price
                    fiat = fiat - position_size*current_price
                    short_position = True
                    purchase_price = current_price
                    #moves.append("Short-Sell")
                else:
                    pass
                    purchase_price = 0
                    #moves.append("Sell")

                trades = trades + 1

                # record whether the trade was profitable
                if purchase_price < current_price:
                    wins = wins + 1 
                else:
                    losses = losses + 1
                

            else:
                pass
                #moves.append("Pass")

        if shorting_allowed == True:
            #record the portfolio information
            if short_position == False or short_position == None:
                if record_balance == True:
                    portfolio_balance.append(position_size*current_price + fiat)
            if short_position == True:
                short_delta = (purchase_price*position_size - current_price*position_size)
                if record_balance == True:
                    portfolio_balance.append(purchase_price*position_size + short_delta + fiat)
        else:
            #record the portfolio information
            if record_balance == True:
                portfolio_balance.append(position_size*current_price + fiat)
            
        if record_balance == True:
            baseline_balance.append(baseline_position_size*current_price)
        
        #record which moving average was higher this moment
        last_average_higher = current_average_higher

        # go through the volume data
        thirty_day_volume = 0 # re-calculate the current thirty_day_volume
        new_volume_data = []
        for volume_data_entry in volume_data:
            if volume_data_entry[0] < 720: # 720 hours in thirty days
                thirty_day_volume = thirty_day_volume + volume_data_entry[1]
                new_volume_data.append([volume_data_entry[0] + 1, volume_data_entry[1]])
        
        volume_data = new_volume_data

    
    # compute final results
    baseline_final = current_price
    baseline_return_rate = (baseline_final/baseline_initial) - 1    
    final_return_rate = ((position_size*current_price + fiat)/starting_capital) - 1
    if (losses + wins) > 0:
        hit_rate = wins/(losses + wins)
    else:
        hit_rate = "N/A"

    # calculate sharpe ratio (using 0% as the risk-free return benchmark)
    #sharpe_ratio = (statistics.mean(monthly_return_rates)-0)/(statistics.stdev(monthly_return_rates)*np.sqrt(12))
    sharpe_ratio = None

    if display_results == True and record_balance == True:
        plot_data = pd.DataFrame()
        plot_data['time'] = sampled_data['timestamp']
        plot_data['Baseline'] = baseline_balance
        plot_data['SMA Crossover'] = portfolio_balance
        if show_moving_averages:
            plot_data["MA1"] = [i*baseline_position_size for i in ma1]
            plot_data["MA2"] = [i*baseline_position_size for i in ma2]
        plot_data.plot(x = "time")
        plt.xticks(rotation="vertical")
        plt.show()
    else:
        plot_data = "Could not generate plot_data: display_results and/or record_balance was set to False."

    # calculate quarters_beating_baseline
    count = 0
    for x in range(0, len(quarter_return_rates)):
        # we round so that a difference of 0.0000000001, etc. won't bring it over the edge.
        if round(quarter_return_rates[x],2) > round(baseline_return_rates[x],2):
            count = count + 1
    
    quarters_beating_baseline = round(count/len(quarter_return_rates), 2)

    # return the results
    backtest_results = {"final_return_rate" : final_return_rate,
               "hit_rate": hit_rate,
               "baseline_return_rate": baseline_return_rate,
               "quarter_return_rates": quarter_return_rates, 
               "quarter_trades": quarter_trades,
               "quarter_hit_rates": quarter_hit_rates,
               "baseline_return_rates": baseline_return_rates,
               "balance_data": plot_data,
               "sharpe_ratio": sharpe_ratio,
               "quarters_beating_baseline": quarters_beating_baseline,
               "strategy_quarterly_stdev": statistics.stdev(quarter_return_rates),
               "baseline_quarterly_stdev": statistics.stdev(baseline_return_rates)

    }
    
    return backtest_results


def random_ma_length_generator():
    """
    Generate random moving averages for optimization purposes.
    """
    import random
    num1 = random.randrange(0, round(2191/2))
    num2 = random.randrange(0, round(2191/2))
    while num2 < num1:
        num2 = random.randrange(0, round(2191/2))
    
    return num1, num2

def run_single_backtest_mean_reversion(x, crypto_df, shorting_allowed, fixed_fee):
    stop_loss = round(random.randrange(0, 100),2)/100
    buy_threshold = round(random.randrange(0, 100),2)/100
    take_profit = round(random.randrange(0, 100),2)/100
    ma_length = random.randrange(0, round(2191/2))

    backtest_results = mean_reversion_backtester(
                sampled_data = crypto_df,
                order_sizing = 1,
                ma_length = ma_length,
                buy_threshold = buy_threshold,
                take_profit = take_profit, 
                stop_loss = stop_loss,
                starting_capital = 10000,
                shorting_allowed=shorting_allowed,
                fixed_fee=fixed_fee,
                record_balance=False,
                fee = 0,
                display_results = False,
                show_moving_averages = False,
                annual_taxes = True,
                tax_percentage = 0.3
            )
    
    # Extract and return relevant results
    return (stop_loss, buy_threshold, take_profit, ma_length, backtest_results)

def run_single_backtest_sma_crossover(x, crypto_df, shorting_allowed, fixed_fee):
    ma1_length, ma2_length = random_ma_length_generator()

    backtest_results = sma_crossover_backtester(
        sampled_data=crypto_df,
        order_sizing=1,
        ma1_length=ma1_length,
        ma2_length=ma2_length,
        starting_capital=10000,
        display_results=False,
        shorting_allowed=shorting_allowed,
        fixed_fee=fixed_fee,
        record_balance=True,
        show_moving_averages=False,
        annual_taxes=True,
        tax_percentage=0.3,
        fee=0
    )
    
    # Extract and return relevant results
    return (ma1_length, ma2_length, backtest_results)

def run_multiple_backtests(shorting_allowed, num_runs, fixed_fee, crypto_df, strategy):

    if strategy == "mean reversion":
        with ProcessPoolExecutor() as executor:
            results = list(executor.map(run_single_backtest_mean_reversion, range(num_runs), [crypto_df] * num_runs, [shorting_allowed] * num_runs, [fixed_fee] * num_runs))
        
        
        # compile results into a table for exploration
        result_dict = {
            "ma_length": [],
            "stop_loss": [],
            "buy_threshold": [],
            "take_profit": [],
            "cumulative_return": [],
            "cumulative_baseline_return": [],
            "profitable_quarters": [],
            "total_trades": [],
            "quarters_beating_baseline_results": [],
            "strategy_quarterly_stdev": [],
            "baseline_quarterly_stdev": []
        }


        for res in results:
            stop_loss, buy_threshold, take_profit, ma_length, backtest_results = res

            result_dict['ma_length'].append(ma_length)
            result_dict['stop_loss'].append(stop_loss)
            result_dict['buy_threshold'].append(buy_threshold)
            result_dict['take_profit'].append(take_profit)
            result_dict['cumulative_return'].append(backtest_results['final_return_rate'])
            result_dict['cumulative_baseline_return'].append(backtest_results['baseline_return_rate'])
            result_dict['profitable_quarters'].append(len([x for x in backtest_results['quarter_return_rates'] if x > 0]))
            result_dict['total_trades'].append(sum([x for x in backtest_results['quarter_trades']]))
            result_dict['quarters_beating_baseline_results'].append(backtest_results['quarters_beating_baseline'])
            result_dict['strategy_quarterly_stdev'].append(backtest_results['strategy_quarterly_stdev'])
            result_dict['baseline_quarterly_stdev'].append(backtest_results['baseline_quarterly_stdev'])


        optimization_results = pd.DataFrame(result_dict)

    elif strategy == "simple moving average crossover":

        with ProcessPoolExecutor() as executor:
            results = list(executor.map(run_single_backtest_sma_crossover, range(num_runs), [crypto_df] * num_runs, [shorting_allowed] * num_runs, [fixed_fee] * num_runs))
        
        
        # compile results into a table for exploration
        
        result_dict = {
            "ma1_length": [],
            "ma2_length": [],
            "cumulative_return": [],
            "cumulative_baseline_return": [],
            "profitable_quarters": [],
            "total_trades": [],
            "quarters_beating_baseline_results": [],
            "strategy_quarterly_stdev": [],
            "baseline_quarterly_stdev": []
        }


        for res in results:
            ma1_length, ma2_length, backtest_results = res

            result_dict['ma1_length'].append(ma1_length)
            result_dict['ma2_length'].append(ma2_length)
            result_dict['cumulative_return'].append(backtest_results['final_return_rate'])
            result_dict['cumulative_baseline_return'].append(backtest_results['baseline_return_rate'])
            result_dict['profitable_quarters'].append(len([x for x in backtest_results['quarter_return_rates'] if x > 0]))
            result_dict['total_trades'].append(sum([x for x in backtest_results['quarter_trades']]))
            result_dict['quarters_beating_baseline_results'].append(backtest_results['quarters_beating_baseline'])
            result_dict['strategy_quarterly_stdev'].append(backtest_results['strategy_quarterly_stdev'])
            result_dict['baseline_quarterly_stdev'].append(backtest_results['baseline_quarterly_stdev'])


        optimization_results = pd.DataFrame(result_dict)
    else:
        raise Exception("Error:", strategy, "is not valid, please select either 'simple moving average' or 'mean reversion'.")

        
        
    return optimization_results
