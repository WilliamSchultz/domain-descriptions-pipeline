from projects.pipeline_ecom_industry_descriptions.src.get_openai import run_openai
from projects.pipeline_ecom_industry_descriptions.src.get_postgres import run_get_domains
from projects.pipeline_ecom_industry_descriptions.src.transform_postgres import run_transform_postgres

def test_get_domains():
    # Test the get_domains function with a specific date
    result = run_get_domains()

    # Assert that the result is not empty
    assert not result.empty

    # Assert that revenue isn't empty
    assert result.revenue.isna().sum()<1

    # Assert that the result has more than 30k rows
    assert result.shape[0] > 30000

    # Assert that the result has the expected columns
    expected_columns = ['domain', 'category', 'revenue', 'transactions', 'sessions',
                        'conv_rate', 'aov', '_merge']

    assert list(result.columns) == expected_columns


    return result

def test_transform_postgres():

    # transform postgres data
    postgres_domains = run_get_domains()
    result = run_transform_postgres(postgres_domains)

    # Assert that the result is not empty
    assert not result.empty

    # Assert that the result has more than 30,000 rows
    assert result.shape[0] > 30000

    # Assert that the result has the expected columns
    expected_columns = ['domain', 'category', 'revenue', 'transactions', 'sessions',
                        'conv_rate', 'aov', '_merge', 'cat_high_revenue', 'cat_low_revenue',
                        'cat_median_revenue', 'cat_percentile_10_revenue',
                        'cat_percentile_90_revenue', 'cat_high_transactions',
                        'cat_low_transactions', 'cat_median_transactions',
                        'cat_percentile_10_transactions', 'cat_percentile_90_transactions',
                        'cat_high_sessions', 'cat_low_sessions', 'cat_median_sessions',
                        'cat_percentile_10_sessions', 'cat_percentile_90_sessions',
                        'cat_high_conv_rate', 'cat_low_conv_rate', 'cat_median_conv_rate',
                        'cat_percentile_10_conv_rate', 'cat_percentile_90_conv_rate',
                        'cat_high_aov', 'cat_low_aov', 'cat_median_aov',
                        'cat_percentile_10_aov', 'cat_percentile_90_aov',
                        'top_cat_revenue_domain', 'top_cat_transactions_domain',
                        'top_cat_sessions_domain', 'top_cat_conv_rate_domain',
                        'top_cat_aov_domain', 'binned_aov', 'binned_conv_rate']

    assert list(result.columns) == expected_columns

def test_get_openai():

    postgres_domains = run_get_domains()
    transformed_postgres = run_transform_postgres(postgres_domains)

    #testing one categorized site and one not
    sample = transformed_postgres[transformed_postgres.domain.str.contains('kbdepot.com|amazon.com', regex=True) == True]

    result = run_openai(sample)

    # Assert that the result is not empty
    assert not result.empty

    # Assert that the result has the expected columns
    expected_columns = ['domain', 'description']

    assert list(result.columns) == expected_columns

    condition_met = result['domain'].eq('amazon.com') & result['description'].str.contains('category')
    assert any(condition_met), "Expected 'domain' to be 'amazon.com' and 'description' to contain the word 'category'"

    condition_met = result['domain'].eq('kbdepot.com') & -result['description'].str.contains('category')
    assert any(condition_met), "Expected 'domain' to be 'kbdepot.com' and 'description' not to contain the word 'category'"

    # Check if 'description' column has a text string for each row that is greater than 50 characters
    is_text_long_enough = result['description'].apply(lambda x: isinstance(x, str) and len(x) > 50)
    assert any(is_text_long_enough), "Some response doesn't have enough text"



















