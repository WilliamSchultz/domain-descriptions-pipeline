import pandas as pd
from src.logs import logger

# Calculate and add various statistics for the 'metric' within each category -- useful for the openai prompts
def big_columns(df, metric):
    category_group = df.groupby('category')[metric]
    df[f'cat_high_{metric}'] = category_group.transform('max')  # Highest value in the category
    df[f'cat_low_{metric}'] = category_group.transform('min')    # Lowest value in the category
    df[f'cat_median_{metric}'] = category_group.transform('median')  # Median value in the category
    df[f'cat_percentile_10_{metric}'] = category_group.transform(lambda x: x.quantile(0.10))  # 10th percentile in the category
    df[f'cat_percentile_90_{metric}'] = category_group.transform(lambda x: x.quantile(0.90))  # 90th percentile in the category
    df[metric] = df[metric].fillna(0)
    
    return df
# Calculate the top domain for each metric -- useful for the openai prompts
def top_domain(df, metric):
    category_group = df.groupby('category')[metric]
    idx = category_group.idxmax()
    highest_df = df.loc[idx, ['category', 'domain']].rename(columns={'domain': f'top_cat_{metric}_domain'})
    return df.merge(highest_df, on='category', how='left')    

metrics = ['revenue', 'transactions', 'sessions', 'conv_rate', 'aov']

def process_metrics(df, metrics):
    for metric in metrics:
        result_df = big_columns(df, metric)
    return result_df

def process_top_domains(df, metrics): 
    result_df = df  # Initialize result_df with the original DataFrame
    for metric in metrics: 
        result_df = top_domain(result_df, metric)
    return result_df

# binning certain metrics
def binned_aov(df, bin_size=25):
    max_aov = int(df['aov'].max())
    bins = range(0, max_aov + bin_size, bin_size)
    df['binned_aov'] = pd.cut(df['aov'], bins, right=False).apply(lambda x: f"{x.left}-{x.left+bin_size}")
    return df

def binned_conv_rate(df, bin_size=0.5):
    max_conv_rate = df['conv_rate'].max()
    bins = pd.interval_range(start=0, end=max_conv_rate + bin_size, freq=bin_size)
    df['binned_conv_rate'] = pd.cut(df['conv_rate'], bins, right=False).apply(lambda x: f"{x.left:.2f}-{x.left+bin_size:.2f}")
    return df

#Each metric can appear in text that openai generates, so needs to be human-readable
columns_no_decimal = ['revenue', 'transactions', 'sessions', 'aov', 'cat_high_revenue', 'cat_low_revenue',
       'cat_median_revenue', 'cat_percentile_10_revenue',
       'cat_percentile_90_revenue', 'cat_high_sessions', 'cat_low_sessions',
       'cat_median_sessions', 'cat_percentile_10_sessions',
       'cat_percentile_90_sessions', 'cat_high_aov', 'cat_low_aov',
       'cat_median_aov', 'cat_percentile_10_aov', 'cat_percentile_90_aov', 'cat_high_transactions',
       'cat_low_transactions', 'cat_median_transactions',
       'cat_percentile_10_transactions', 'cat_percentile_90_transactions']

columns_decimal = ['cat_high_conv_rate', 'cat_low_conv_rate',
       'cat_median_conv_rate', 'cat_percentile_10_conv_rate',
       'cat_percentile_90_conv_rate']

def format_dataframe(df, columns_no_decimal, columns_decimal):
    def format_columns(df, columns, decimal_places=0):
        df[columns] = df[columns].round(decimal_places)
        df[columns] = df[columns].apply(lambda x: "{:,.{decimals}f}".format(x, decimals=decimal_places) if pd.notnull(x) else x)
        return df

    for column_name in columns_no_decimal:
        df = format_columns(df, column_name, decimal_places=0)

    for column_name in columns_decimal:
        df = format_columns(df, column_name, decimal_places=2)

    return df

#function to run
def run_transform_postgres(df):
    logger.info('formatting domain data started...')
    add_metrics = process_metrics(df, metrics)
    add_domains = process_top_domains(add_metrics, metrics)
    aov_bins = binned_aov(add_domains)
    cr_bins = binned_conv_rate(aov_bins)
    logger.info('formatting domain data complete')
    return format_dataframe(cr_bins, columns_no_decimal, columns_decimal)
    
    


