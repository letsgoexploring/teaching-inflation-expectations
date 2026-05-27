# Teaching Inflation Expectations

This repository contains replication materials for:

> Jenkins, Brian C. (2026). "Teaching Inflation Expectations with Professional Forecast Data and a Classroom Experiment." Working paper. https://github.com/letsgoexploring/teaching-inflation-expectations/blob/main/paper/Jenkins_Inflation_Expectations.pdf

If you use any of these materials in your own research or teaching, please cite the paper above.

This repository contains two main resources:

1. **A dataset for teaching** — historical U.S. inflation, professional forecasts, and interest rates, provided as ready-to-use CSV files along with the Python code used to construct them from FRED and the Philadelphia Fed's Survey of Professional Forecasters.
2. **An oTree classroom experiment** — a browser-based forecasting experiment in which students predict one-period-ahead inflation using historical macroeconomic data, deployable to Heroku.

---

## Repository Contents

```
teaching-inflation-expectations/
├── paper/
│   └── Jenkins_Inflation_Expectations.pdf   # Working paper
├── otree/                                    # oTree classroom experiment
│   ├── inflation_forecast/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── Intro.html
│   │   ├── Instructions.html
│   │   ├── InstructionsMSE.html
│   │   ├── Forecast.html
│   │   ├── Feedback.html
│   │   ├── Survey.html
│   │   ├── Results.html
│   │   └── inflation_data.csv               # Historical macro data used by the experiment
│   ├── settings.py
│   ├── requirements.txt
│   ├── Procfile
│   └── .python-version
├── python/
│   └── inflation_forecast_data.ipynb         # Builds the CSV datasets from FRED + SPF
├── csv/
│   ├── inflation_forecast_data_annual.csv    # Annual SPF forecast data
│   └── inflation_forecast_data_quarterly.csv # Quarterly SPF forecast data
├── LICENSE
├── README.md
└── SETUP.md                                  # Local and Heroku deployment instructions
```

See [`SETUP.md`](SETUP.md) for instructions on running the oTree experiment locally and deploying it to Heroku.

---

## License

This project is licensed under the MIT License. See [`LICENSE`](LICENSE) for details.
