This is a series of retirement financial simulations and investigations, initially
inspired by Michael McClung's book [Living Off Your Money].

[Living Off Your Money]: https://www.amazon.com/Living-Off-Your-Money-Retirement/dp/0997403411

QUICKSTART
==========

 $ virtualenv .
 $ bin/pip install --requirement requirements.txt
 $ bin/jupyter-notebook


JUPYTER NOTEBOOKS
=================
- [Prime Harvesting][1]. The one that started the project. A comparison of Prime Harvesting and
  Annual Rebalancing. [Blog post][Medium prime].
- [EM vs. VPW][2]. A comparison of portfolio values and incomes for EM and VPW (from bogleheads).
- [Inverted Withdrawals][3]. A look at [Inverted Withdrawals][inverted] and [blog post][Medium inverted].
- [Liability Matching Portfolio][4]. _Haven't done anything with this one yet..._
- [Sleep Well At Night][5]. A first look at bond levels with Prime Harvesting. [Blog post][Medium averages].
- Monthly Harvesting. The difference between checking annually and checking monthly. [Blog post][Monthly harvesting].

[1]: https://github.com/hoostus/prime-harvesting/blob/master/Prime%20Harvesting.ipynb
[2]: https://github.com/hoostus/prime-harvesting/blob/master/EM%20vs%20VPW.ipynb
[3]: https://github.com/hoostus/prime-harvesting/blob/master/Inverted%20Withdrawal%20Rates.ipynb
[inverted]: http://www.advisorperspectives.com/articles/2016/05/17/inverted-withdrawal-rates-and-the-sequence-of-returns-bonus
[Medium inverted]: https://medium.com/@justusjp/inverted-withdrawals-and-risk-aversion-8d165247c92a#.x6u540qsn
[4]: https://github.com/hoostus/prime-harvesting/blob/master/LMP.ipynb
[5]: https://github.com/hoostus/prime-harvesting/blob/master/Sleep%20Well%20At%20Night.ipynb
[Medium averages]: https://medium.com/@justusjp/prime-harvesting-bond-levels-the-problem-with-averages-7a21518b6f57#.8c7mk68y5
[Medium prime]: https://medium.com/@justusjp/prime-harvesting-vs-rebalancing-graphs-2687930a995b#.enlcxwdny
[Monthly harvesting]: https://medium.com/@justusjp/prime-harvesting-with-monthly-vs-annual-returns-64d6d748c36f#.yt519zjoq

DATA SOURCES
============
CSV imports are easier for the code to deal with, so I've frequently munged original
data source into CSV files.

- [1871_returns.csv] comes from Simba's backtesting spreadsheet on [bogleheads][6]
- [2004-period-life-table.csv] comes from https://www.kitces.com/joint-life-expectancy-and-mortality-calculator/
- [PortfolioChart.com 'simulated indexes'][7]. The blog post introducing them is
  https://portfoliocharts.com/stock-index-calculator/

[1871_returns.csv]: https://github.com/hoostus/prime-harvesting/blob/master/1871_returns.csv
[6]: https://www.bogleheads.org/wiki/Simba's_backtesting_spreadsheet
[2004-period-life-table.csv]: https://github.com/hoostus/prime-harvesting/blob/master/2004-period-life-table.csv
[7]: https://github.com/hoostus/prime-harvesting/blob/master/stock-index-calculator-20160620-v2.csv

I've also included local copies of some of the Excel sheets the CSV files were derived from.

- [Simba's backtesting spreadsheet][8]
- PortfolioChart.com 'simulated indexes' [raw Excel file][9]

[8]: https://github.com/hoostus/prime-harvesting/blob/master/Backtest-Portfolio-returns-rev15c.xlsx
[9]: https://github.com/hoostus/prime-harvesting/blob/master/stock-index-calculator-20160620-v2.xlsx

FUTURE IDEAS
============
- Probability of failure and SIZE of failure might be different. You might
choose the plan with the higher probability of failure because the size of
failure is smaller. See: Estrada's new paper
- Try to tie together Prime Harvesting and valuations better.
- CEW (and by extension WER & HREFF) punishing declining withdrawal rates.
However, the evidence from actual retirees (Bernicke & others) shows that's
exactly what retirees do. Have a metric that follows this?
- Mortality-weighted shortfall calculations from Gardner's paper.
  Except...when you do Monte Carlo with stochastic mortality, you get
  this already.
- Look at how bond percentages change with monthly Prime Harvesting.
- Look at how valuation/expected returns in PMT does long term smoothing
- Try putting Pye's higher rate with Siegel & Waring's average lifespan
  Does it tilt TOO much towards early income?
- Map early income tilts from PMT shapes against Bernicke & Blanchett's
  research on actual retiree spending.
- Walton's paper on inverted withdrawals
- Treat SS as a bond, argument against: https://www.bogleheads.org/forum/viewtopic.php?f=10&t=200572&newpost=3072525#p3072379
- "Alpha, Beta, and now Gamma" includes parameters for asset classes that allows
  use of a Truncated Levy Flight distribution to create Monte Carlo analysis. That sounds
  fun?
- redo Blanchett's Revisiting the Optimal Distribution Glide Path with a variable withdrawal
  strategy instead of constant withdrawals
