# crypto_backtesting_analysis
This repository contains Jupyter notebooks for analyzing the performance of trend following and mean reversion strategies for trading Bitcoin.


## Background
In 2020, I was interested in setting up automated trading systems for cryptocurrency. To start, I explored how well trend following and mean reversion strategies could perform on cryptocurrency trading. I took 1 minute Bitcoin data from 2014 through 2019 and wrote both a simple moving average (SMA) crossover system and a mean reversion system to see how well it would perform. Afterwards, I did a crude optimization to find the best parameters by re-running the algorithms 100 times with random parameters to see how well they affected the returns.

## Results
The results showed that both trend following and mean reversion strategies outperformed the buy and hold strategy. The highest cumulative return for each strategy was 3,929.8% for mean reversion and 5,569.8% for SMA crossover, compared to 886.6% for buy and hold.


![plot](/images/comparison_plot.png)

## Limitations
It is important to note that there are gaps in the price data and that the code does not factor in exchange fees. Additionally, there may be overfitting when searching for the best parameters.

Even though I had data from 2013, I ended up removing the data since there was a flash crash incident that was heavily skewing the mean reversion strategies to buy the crash and hold for the remaining 6 years (see this log-scale plot from 2013 to 2019:)
![plot](/images/comparison_log_plot.png)

## Future Directions
Future work should aim to address the limitations, such as removing flash-crash incidents, adding the ability to short-sell, incorporating more recent data, exploring different cryptocurrencies and moving average approaches, and improving model performance metrics.

## Live Trading
If you are interested in implementing the strategies identified in this analysis, you may want to check out the following repository:

https://github.com/hansenrhan/crypto_trader

In this repository, I created mean reversion and trend following bots so I could live trade cryptocurrency on the coinbase exchange using the parameters identified in the analysis in this repository. This repository includes code and instructions for setting up and running the trading bots.

## Contents
- simple_moving_average_analysis.ipynb: trend following backtests  
- mean_reversion_analysis.ipynb: mean reversion backtests
- comparison.ipynb: creating a comparison plot between the two and their highest performing parameters
- BTC_1min_bitfinex/: 1 minute BTC price data from 2013 to 2019
- sma_optimization_results_100_runs.csv: results of 100 backtests using the SMA crossover strategy with different moving averages
- mean_reversion_optimization_results_100_runs.csv: results of 100 backtests using mean reversion strategy with different parameters

## Disclaimer
Please note that cryptocurrency trading is a high-risk activity and past performance is not indicative of future results. Use this code and the analysis in this repository at your own risk. Make sure to thoroughly understand the risks involved and do your own research before making any trades. The author of this repository is not responsible for any losses or damages incurred as a result of using the code or following the analysis in this repository.