import pandas as pd
from dateutil.relativedelta import relativedelta
import datetime
from src.logs import logger
from util_package.util import users_db, domains_db


#get domains, calculating the first metrics needed for openai query
def get_domains(date):
    logger.info('Getting domains...')
    query = f'''
    SELECT
        "domain",
        SUM("transactionrevenue") AS revenue,
        SUM("transactions") AS transactions,
        SUM("sessions") AS sessions,
        CAST(SUM("transactions") * 100.0 / SUM("sessions") AS NUMERIC(10, 2)) AS conv_rate,
        CAST(SUM("transactionrevenue") / SUM("transactions") AS NUMERIC(20, 2)) AS aov
    FROM "table_name"
    WHERE "date" = '{date}'
    GROUP BY "domain"
    ORDER BY revenue DESC;
    '''

    return pd.read_sql(query, domains_db)

#get domain categories, don't need country split so selecting distinct
def get_categories():
    query = '''
    SELECT DISTINCT "domain", "category"
    FROM "table_name"
    WHERE "category" IS NOT NULL;
    '''
    return pd.read_sql(query, users_db)

def doms_cats(categories, domains):
    with_cats = pd.merge(categories, domains, left_on='domain', right_on='domain', how='right', indicator=True)
    with_cats2 = with_cats.fillna(0)
    return with_cats2

#get input date
current_date = datetime.date.today()
# Subtract one month while keeping the day as 01 to match data updates (data has 1 month data lag)
one_month_ago = current_date - relativedelta(months=1)
formatted_date = one_month_ago.replace(day=1)
formatted_date2 = formatted_date.strftime("%Y-%m-%d")


#function to run
def run_get_domains():
    domains = get_domains(formatted_date2)
    categories = get_categories()
    logger.info('Getting domains complete')
    return doms_cats(categories, domains)