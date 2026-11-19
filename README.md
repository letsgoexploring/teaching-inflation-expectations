# Teaching Inflation Expectations

Materials for:

> Jenkins, Brian C. (2026). "Teaching Inflation Expectations with Professional Forecast Data and a Classroom Experiment." Working paper. [paper/Jenkins_Inflation_Expectations.pdf](paper/Jenkins_Inflation_Expectations.pdf)

The paper describes low-cost resources for teaching how inflation expectations are measured and how they behave, using survey data on professional and household forecasts and a short classroom forecasting experiment. If you use these materials in your teaching or research, please cite the paper.

## What is here

| Resource | Where | What it is |
|---|---|---|
| Paper | [`paper/`](paper/) | Current draft of the paper |
| Teaching dataset | [economic-data repository](https://github.com/letsgoexploring/economic-data/tree/main/inflation-forecasts-and-interest-rates) | SPF inflation forecasts, actual GDP deflator inflation, and the one-year Treasury rate, at annual and quarterly frequencies |
| Homework questions | [`homework/`](homework/) | Sample homework questions that use the annual dataset |
| oTree experiment | [`otree/`](otree/) | Browser-based inflation forecasting experiment; see [`SETUP.md`](SETUP.md) to deploy it |
| Spreadsheet version | [`worksheet/`](worksheet/) | Excel worksheet for running the experiment in class without oTree |
| Code | [`python/`](python/) | Notebook that produces the paper's figures and tables |

## The teaching dataset

The dataset is maintained and periodically updated in the [`inflation-forecasts-and-interest-rates`](https://github.com/letsgoexploring/economic-data/tree/main/inflation-forecasts-and-interest-rates) folder of my economic-data repository, along with the notebook that builds it from the original sources. It has two CSV files:

- `inflation_forecast_data_annual.csv`
- `inflation_forecast_data_quarterly.csv`

Each has three columns:

- `deflator inflation - forecast`: median one-year-ahead GDP deflator inflation forecast from the Federal Reserve Bank of Philadelphia's Survey of Professional Forecasters (SPF)
- `deflator inflation - actual`: actual GDP deflator inflation over the following year (FRED series GDPDEF for quarterly data, A191RD3A086NBEA for annual data)
- `nominal interest`: one-year Treasury rate (FRED series GS1), averaged over the months of each period

Each row is dated by when the forecast was made. The row for 2020 holds the forecast made in 2020 and actual inflation from 2020 to 2021. So, row by row:

- the *ex ante* real interest rate is `nominal interest` minus `deflator inflation - forecast`
- the forecast error is `deflator inflation - forecast` minus `deflator inflation - actual` (positive means the forecast was too high)

Students can download the annual file directly from:

```
https://raw.githubusercontent.com/letsgoexploring/economic-data/refs/heads/main/inflation-forecasts-and-interest-rates/csv/inflation_forecast_data_annual.csv
```

See the paper for details and caveats, including data revisions and the SPF's switch from the GNP deflator before 1992.

## The experiment

Students forecast U.S. inflation one year ahead for 20 rounds covering 1970 to 1989, without being told the years. Each round shows the previous five years of inflation, unemployment, and the federal funds rate. After each forecast, students see actual inflation, their forecast error, and their running mean squared error. The first two rounds are practice. The experiment takes about 20 minutes and works on phones and laptops.

**With oTree.** The app is in [`otree/`](otree/). [`SETUP.md`](SETUP.md) explains how to deploy it to Heroku, create a session, distribute participant links, and export the data. The historical data shown to students are in `otree/inflation_forecast/inflation_data.csv`.

**Without oTree.** Show the data for each round on slides, have students record forecasts in the worksheet, then reveal actual inflation. The [`worksheet/`](worksheet/) folder has:

- `forecasting_worksheet.xlsx`: blank worksheet for students, with formulas for the forecast error, squared error, and running MSE
- `forecasting_worksheet_example.xlsx`: the partly completed example shown in the paper

To avoid errors from mistyped values, lock the actual inflation column or recompute forecast errors from the submitted forecasts.

## Code

[`python/experiment_data_analysis.ipynb`](python/experiment_data_analysis.ipynb) produces the paper's figures and tables. It needs the student forecast data, which are **not** included in this repository: under the study's IRB protocol, the de-identified experiment data are accessible only to the study team.

## License

MIT License. See [`LICENSE`](LICENSE).
