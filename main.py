from src.get_postgres import run_get_domains
from src.transform_postgres import run_transform_postgres
from src.get_openai import run_openai
from src.load_s3 import run_load_s3, get_previous_month_filename
from src.telegram_bot import telegram_bot_sendtext

def main():

    # get postgres data
    postgres_domains = run_get_domains()

    # transform postgres data
    transformed_postgres = run_transform_postgres(postgres_domains)

    # get openai data
    results = run_openai(transformed_postgres)

    # load to s3
    run_load_s3(results)

    # send confirmation message to Telegram
    file = get_previous_month_filename()
    telegram_bot_sendtext(f'{file} upload complete')

if __name__ == "__main__":
    main()


