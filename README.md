# crypto_backtesting_analysis
Back in 2020, I was interested in setting up automated trading systems for cryptocurrency. To start, I explored how well trend following and mean reversion strategies could perform on cryptocurrency trading and wrote these backtesting notebooks. Here, I took 1 minute bitcoin data from 2013 through 2019 and wrote both a simple moving average (SMA) crossover system and a mean reversion system to see how well it would perform. Afterwards, I did a crude optimization to find the best parameters by re-running the algorithms 100 times with random parameters to see how well they affected the returns. 
  
**Results**:
- When trying out 100 random parameter backtests, 77 of the mean reversion backtests had higher cumulative returns higher than baseline buy & hold strategy compared to 32 for the SMA crossover strategy. 
- Across the 100 backtests, the highest cumulative return for each strategy was 860,972.1% for mean reversion and 19,477.7% for SMA crossover compared to 7,640.4% for buy and hold. 

**Limitations**:
- There are gaps in the price data, since this was just exploratory I wrote the code to assume that every 60 entries was an hour even there are gaps (since it is over such a long timeframe, I don't imagine the end result would be dramatically different, but it is well worth looking into if you are seriously planning to run this kind of strategy)
- Does not factor in exchange fees (although the lower trading volume shouldn't affect the result against baseline too much here)
- There is a large, sudden drop in price (flash-crash) in 2013 that is highly skewing the mean reversion data (see this log-scale plot:)

![plot](/images/comparison_log_plot.png)

**Future Directions**: 
- Removing flash-crash incidents
- Does performance improve if you add the ability to short-sell? 
- Adding data from 2019 to 2023 (present day)
- Running on different cryptocurrency coins (and altcoins)
- Trying different moving average approaches like exponential moving average (EMA) or weighted moving average (WMA)
- Adding better metrics to assess model performance (alpha, beta, etc...)
- Reduce overfitting (or understand how much overfitting is occuring) when searching for the best parameters by using cross validation

### Contents
- **simple_moving_average_analysis.ipynb** : trend following backtest 
- **mean_reversion_analysis.ipynb** : mean reversion backtest
- comparison.ipynb: creating a comparison plot between the two and their highest performing parameters
- BTC_1min_bitfinex/ : 1 minute BTC price data from 2013 to 2019
- sma_optimization_results_100_runs.csv : results of 100 backtests using the SMA crossover strategy with different moving averages
- mean_reversion_optimization_results_100_runs.csv: results of 100 backtests using mean reversion strategy with different parameters



