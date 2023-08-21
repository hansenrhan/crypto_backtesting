# crypto_backtesting_analysis
This repository contains Jupyter notebooks for analyzing the performance of trend following and mean reversion strategies for trading Bitcoin.


## Background
In 2020, I was interested in setting up automated trading systems for cryptocurrency. To start, I explored how well trend following and mean reversion strategies could perform on cryptocurrency trading. Initially, I took 1 minute Bitcoin data from 2014 through 2019 and wrote both a simple moving average (SMA) crossover system and a mean reversion system to see how well it would perform. Afterwards, I did a crude optimization to find the best parameters by re-running the algorithms 100 times with random parameters to see how well they affected the returns. 


Since then, I've updated the repository to include data through 2023 and backtest short-selling and calculate fees based on trading volume. 


## Results
The results showed that some Mean Reversion and SMA Crossover strategy runs did outperform buy and hold, but overall after incorperating fees - neither strategy (with or without shorting) outperformed buy and hold in the majority of runs using random parameters.

This is not to say that Mean Reversion and/or SMA Crossover strategies cannot outperform Buy and Hold, but it can be difficult to optimize and identify parameters without overfitting. A walk forward analysis would be probably be the next step where paper trading or trading with a small amount of money would be done after identifying some of the top parameters from this analysis. 

Regardless of whether either beats buy and hold, it seems that SMA Crossover seems to be a better pick than Mean Reversion for BTC trading. 


![plot](/images/jun_13_boxplots.png)

![plot](/images/jun_13_barplots.png)

## Limitations
It is important to note that there are gaps in the price data. 

Even though I had data from 2013, I ended up removing the data since there was a flash crash incident that was heavily skewing the mean reversion strategies to buy the crash and hold for the remaining 6 years (see images/comparison_log_plot.png)

## Future Directions
Future work should aim to address the limitations, such as removing flash-crash incidents,exploring different cryptocurrencies and moving average approaches, and improving model performance metrics.

## Live Trading
If you are interested in implementing the strategies identified in this analysis, you may want to check out the following repository:

https://github.com/hansenrhan/crypto_trader

In this repository, I created mean reversion and trend following bots so I could live trade cryptocurrency on the coinbase exchange using the parameters identified in the analysis in this repository. This repository includes code and instructions for setting up and running the trading bots.

## Contents
- crypto_backtesting.py: logic for backtesting, plotting, helper functions
- simple_moving_average_analysis.ipynb: trend following backtesting analysis
- mean_reversion_analysis.ipynb: mean reversion backtesting analysis
- BTC_1min_bitfinex/: 1 minute BTC price data from 2013 to 2023
- strategy_comparison.Rmd: R markdown analysis comparing output from backtests
- strategy_comparative_analysis.html: R markdown analysis output
- archive/:  misc. files generated while developing
- run_output/: backtesting run files
- images/: images generated during analysis

## Disclaimer
Please note that cryptocurrency trading is a high-risk activity and past performance is not indicative of future results. Use this code and the analysis in this repository at your own risk. Make sure to thoroughly understand the risks involved and do your own research before making any trades. The author of this repository is not responsible for any losses or damages incurred as a result of using the code or following the analysis in this repository.