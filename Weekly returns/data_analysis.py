import pandas as pd
import numpy as np
# Calculate weekly returns
def calculate_weekly_returns(df):
    # Convert datadate to datetime and sort
    df['datadate'] = pd.to_datetime(df['datadate'], errors='coerce')
    df.sort_values(by=['tic', 'datadate'], inplace=True)

    # Calculate adjusted close prices
    df['adjusted_close'] = df['prccd'] / df['ajexdi']
    df['adjusted_close_prior'] = df.groupby('tic')['adjusted_close'].shift(1)
    df['trfd_prior'] = df.groupby('tic')['trfd'].shift(1)

    # Initialize daily_return with np.nan
    df['daily_return'] = np.nan

    # Calculate daily returns
    df['daily_return'] = (
        ((df['adjusted_close'] * df['trfd']) /
         (df['adjusted_close_prior'] * df['trfd_prior']))
    )

    # Set daily_return to NaN if the gap between days is too large
    df['day_diff'] = df.groupby('tic')['datadate'].diff().dt.days
    df.loc[df['day_diff'] > 5, 'daily_return'] = np.nan

    # Create a pivot table of daily returns
    adjusted_daily_returns = df.pivot_table(index='datadate', columns='tic', values='daily_return')

    # Calculate weekly returns
    all_weekdays = pd.date_range(start=adjusted_daily_returns.index.min(), end=adjusted_daily_returns.index.max(), freq='B')
    df_reindexed = adjusted_daily_returns.reindex(all_weekdays)

    all_mondays = pd.date_range(start=df_reindexed.index.min(), end=df_reindexed.index.max(), freq='W-MON')
    weekly_pivot_df = pd.DataFrame(data=np.nan, index=all_mondays, columns=df_reindexed.columns)
    ticker_start_dates = df_reindexed.apply(lambda x: x.first_valid_index(), axis=0)

    for i, monday in enumerate(all_mondays):
        start_date = monday
        if i < len(all_mondays) - 1:
            end_date = all_mondays[i + 1] - pd.DateOffset(days=1)
        else:
            end_date = df_reindexed.index.max()

        weekly_data = df_reindexed.loc[start_date:end_date]

        for ticker in df_reindexed.columns:
            if monday < ticker_start_dates[ticker]:
                weekly_pivot_df.loc[monday, ticker] = np.nan
            else:
                valid_weekly_data = weekly_data[ticker].dropna()
                if valid_weekly_data.empty:
                    weekly_pivot_df.loc[monday, ticker] = np.nan
                elif len(valid_weekly_data) < 3:  # Require at least 3 valid daily returns
                    weekly_pivot_df.loc[monday, ticker] = np.nan
                else:
                    weekly_return = valid_weekly_data.prod() - 1
                    # Handle cases where the product is zero
                    if weekly_return == 0:
                        weekly_pivot_df.loc[monday, ticker] = np.nan
                    else:
                        weekly_pivot_df.loc[monday, ticker] = weekly_return * 100

    weekly_pivot_df.dropna(axis=1, how='all', inplace=True)

    return weekly_pivot_df
