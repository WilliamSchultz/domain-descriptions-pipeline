import time
import openai
import pandas as pd
from src.logs import logger

openai.api_key = ''

# This function generates performance metric descriptions for domains with categories

def chat_cat(
    domain_col, category_col, revenue_col, convrate_col, aov_col, cat_median_revenue_col, top_cat_revenue_domain_col,
    cat_high_revenue_col, cat_high_conv_rate_col, cat_low_conv_rate_col, binned_aov_col, cat_high_aov_col, cat_low_aov_col,
    sessions_col, cat_high_sessions_col, top_cat_sessions_domain_col, cat_median_conv_rate_col,
    cat_percentile_90_conv_rate_col, cat_percentile_10_conv_rate_col, cat_median_aov_col, cat_percentile_90_aov_col,
    cat_percentile_10_aov_col, cat_median_sessions_col
):
    global result_numbers

    # Creating a chat conversation with user's query for OpenAI
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": f'''in 100 words, write a description of the performance metrics we observe for {domain_col}. 
Here are some of the performance metrics for the month of September, 2023. Not all need to be included:

{domain_col}'s industry: {category_col}

{domain_col}'s revenue: ${revenue_col} and the median revenue in the {category_col} is ${cat_median_revenue_col}. 
The largest online store in the {category_col} category is {top_cat_revenue_domain_col} with ${cat_high_revenue_col}. 

{domain_col}'s conversion rate: {convrate_col}%
A very high conversion rate in the {category_col} is: {cat_percentile_90_conv_rate_col}%
A very low conversion rate in the {category_col} is: {cat_percentile_10_conv_rate_col}%

{domain_col}'s AOV: ${binned_aov_col}
A very high AOV in the {category_col} is: ${cat_percentile_90_aov_col} 
A very low AOV in the {category_col} is ${cat_percentile_10_aov_col}

{domain_col}'s sessions: {sessions_col}
The store with the highest sessions is at {cat_high_sessions_col} from {top_cat_sessions_domain_col}
The median sessions in the {category_col} is {cat_median_sessions_col}. 

Format the output as one single line of text, never bullet points.'''
            }
        ],
        temperature=1.5,
        max_tokens=250,
        top_p=.9,
        frequency_penalty=0,
        presence_penalty=0
    )

    text = response['choices'][0]['message']['content']
    new = pd.DataFrame(columns=['domain', 'description'])
    new.loc[0] = [domain_col, text]
    return new

# This function generates performance metric descriptions for domains without categories

def chat_nocat(domain_col, category_col, revenue_col, convrate_col, aov_col, cat_median_revenue_col, top_cat_revenue_domain_col, 
              cat_high_revenue_col, cat_high_conv_rate_col, cat_low_conv_rate_col, binned_aov_col, cat_high_aov_col, cat_low_aov_col, 
              sessions_col, cat_high_sessions_col, top_cat_sessions_domain_col, cat_median_conv_rate_col, 
              cat_percentile_90_conv_rate_col, cat_percentile_10_conv_rate_col, cat_median_aov_col, cat_percentile_90_aov_col, cat_percentile_10_aov_col, cat_median_sessions_col):
    global result_numbers
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user",
                   "content": f'''in 100 words, write a description of the performance metrics we observe for {domain_col}. Here are some of the performance metrics for the month of September, 2023. Not all need to be included: 

{domain_col}'s revenue: ${revenue_col} 

{domain_col}'s conversion rate: {convrate_col}% 

{domain_col}'s AOV: ${binned_aov_col}

{domain_col}'s sessions: {sessions_col}

Format the output as one single line of text, never bullet points.'''
                  }
                 ],
        temperature=1.5,
        max_tokens=250,
        top_p=.9,
        frequency_penalty=0,
        presence_penalty=0)

    text = response['choices'][0]['message']['content']
    new = pd.DataFrame(columns=['domain', 'description'])
    new.loc[0] = [domain_col, text]
    return new



# function that decides if a domain should go to chat_cat or chat_nocat depending if the domain has a category

def calls_retry_chat(
    domain_col, category_col, revenue_col, convrate_col, aov_col, cat_median_revenue_col, top_cat_revenue_domain_col,
    cat_high_revenue_col, cat_high_conv_rate_col, cat_low_conv_rate_col, binned_aov_col, cat_high_aov_col, cat_low_aov_col,
    sessions_col, cat_high_sessions_col, top_cat_sessions_domain_col, cat_median_conv_rate_col,
    cat_percentile_90_conv_rate_col, cat_percentile_10_conv_rate_col, cat_median_aov_col, cat_percentile_90_aov_col,
    cat_percentile_10_aov_col, cat_median_sessions_col
):
    max_retries = 100
    retry_delay = 5  #seconds

    if category_col == 'null':
    # If 'category_col' is None or empty, send to chat_nocat function.
        retry_function = chat_nocat
    else:
    # If 'category_col' is not None or not empty, send to chat_cat function.
        retry_function = chat_cat

    # Iterate through a set number of retries.
    for retry in range(max_retries):
        try:
            # calling chat_cat or chat_nocat function
            response = retry_function(
                domain_col, category_col, revenue_col, convrate_col, aov_col, cat_median_revenue_col,
                top_cat_revenue_domain_col, cat_high_revenue_col, cat_high_conv_rate_col, cat_low_conv_rate_col,
                binned_aov_col, cat_high_aov_col, cat_low_aov_col, sessions_col, cat_high_sessions_col,
                top_cat_sessions_domain_col, cat_median_conv_rate_col, cat_percentile_90_conv_rate_col,
                cat_percentile_10_conv_rate_col, cat_median_aov_col, cat_percentile_90_aov_col, cat_percentile_10_aov_col,
                cat_median_sessions_col
            )
            return response

        except openai.error.APIError as e:
            logger.info(f'API error occurred: {str(e)}. Retrying in {retry_delay} seconds...')
            #print(f"API error occurred: {str(e)}. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)

        except Exception as e:
            logger.info(f'An unexpected error occurred: {str(e)}. Retrying in {retry_delay} seconds...')
            time.sleep(retry_delay)

    print("Max retries exceeded. Unable to get a response.")
    return None


def run_openai(df):
    logger.info('Sending domain data to openai started...')
    descriptions = []

    for index, row in df.iterrows():
        domain_col = row['domain']
        category_col = row['category']
        revenue_col = row['revenue']
        convrate_col = row['binned_conv_rate']
        aov_col = row['binned_aov']
        cat_median_revenue_col = row['cat_median_revenue']
        top_cat_revenue_domain_col = row['top_cat_revenue_domain']
        cat_high_revenue_col = row['cat_high_revenue']
        cat_high_conv_rate_col = row['cat_high_conv_rate']
        cat_low_conv_rate_col = row['cat_low_conv_rate']
        binned_aov_col = row['binned_aov']
        cat_high_aov_col = row['binned_aov']  # Is this correct?
        cat_low_aov_col = row['binned_aov']    # Is this correct?
        sessions_col = row['sessions']
        cat_high_sessions_col = row['cat_high_sessions']
        top_cat_sessions_domain_col = row['top_cat_sessions_domain']
        cat_median_conv_rate_col = row['cat_median_conv_rate']
        cat_percentile_90_conv_rate_col = row['cat_percentile_90_conv_rate']
        cat_percentile_10_conv_rate_col = row['cat_percentile_10_conv_rate']
        cat_median_aov_col = row['cat_median_aov']
        cat_percentile_90_aov_col = row['cat_percentile_90_aov']
        cat_percentile_10_aov_col = row['cat_percentile_10_aov']
        cat_median_sessions_col = row['cat_median_sessions']

        description_df = calls_retry_chat(
            domain_col, category_col, revenue_col, convrate_col, aov_col, cat_median_revenue_col,
            top_cat_revenue_domain_col, cat_high_revenue_col, cat_high_conv_rate_col, cat_low_conv_rate_col,
            binned_aov_col, cat_high_aov_col, cat_low_aov_col, sessions_col, cat_high_sessions_col,
            top_cat_sessions_domain_col, cat_median_conv_rate_col, cat_percentile_90_conv_rate_col,
            cat_percentile_10_conv_rate_col, cat_median_aov_col, cat_percentile_90_aov_col, cat_percentile_10_aov_col,
            cat_median_sessions_col
        )

        descriptions.append(description_df)

    descriptions_df = pd.concat(descriptions, ignore_index=True)
    logger.info('openai stage complete')
    return descriptions_df


