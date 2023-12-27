# Data pipeline project: domain descriptions 

## Problem Statement

Building a production-ready data pipeline that outputs text-based SEO-optimized summaries for the performance of 
e-commerce domains when the source dataset is updated.  

## Tech Stack

- Postgres db
- OpenAI
- Docker
- AWS ECR
- AWS S3
- AWS Lambda
- AWS Batch
- Telegram
- Python

## How it works 

1. Get domain-level from the postgres db
2. Transform the postgres data so that it prepared for the openai queries 
3. Request from openai a summary for each domain 
4. Load the openai responses to an s3 bucket 

How each module works: 

#### get_postgres.py 

- query postgres db to get domains and categories
- calculate the first metrics in sql to be used

#### transform_postgres.py 
- adding ~45 columns to be used in openai prompt
- binning values to not reveal exact domain performance
- calculating domain and category values (e.g. ```category_group.transform(lambda x: x.quantile(0.10))```)

#### get_openai.py 

- building prompts using the ~45 columns 
- sending requests to openai 
- retry logic to handle when api returns errors
- conditional logic to handle domains that don't have categories

#### load_s3.py 

- loading results to s3 bucket

#### main.py 

- entry point for the program used by Dockerfile CMD to run

##### other files

##### util_package

- used to create_engine for sqlalchemy to access postgres db

##### build_and_run.sh

- build and run the docker container

##### update_ecr.sh

- building the docker image
- pushing docker image to AWS ECR

##### logs.py 

- printing to console critical phases of the pipeline

##### telegram_bot.py 

- sending a success/fail message to a telgram channel

##### Dockerfile

- Dockerfile that builds a container and runs the main.py file

##### requirements.txt

- generated from the IDE DataSpell 

## Running the project

- build the docker image by running: `build_and_run.sh`
- update AWS ECR: `update_ecr.sh`
- enable the AWS Lambda function to run the batch job 

## AWS setup 

- there is a lambda function with an s3 trigger 
- the lamdba fucntion is triggered from an event, which is when a file is uploaded, which indcates there has been a data update
- the lamdba function has code that runs the Batch job using Fargate
- the Batch job uses the Docker container image in the the ECR repository  

## Testing 

- testing that get_postgres.py doesn't return empty results and all columns are present
- testing that transform_postgres.py generates all the correct columns 
- testing that get_openai.py has the right columns and the responses are meeting some minimal criteria

## About the dataset used

This is a project built using the domain-level e-commerce dataset from Grips Intelligence, which is a representative
panel of e-commerce activity in the US, UK and DE consumer economy based. Comparing to the US Census Bureau's
[QUARTERLY RETAIL E-COMMERCE SALES report](https://www.census.gov/retail/mrts/www/data/pdf/ec_current.pdf), this Grips
dataset tracks 10.08% of all US e-commerce sales.


## Tech stack / why / alternatives 

The technologies you used, why they were selecgted and the benefits and tradeoffs of those technologies vs. others: 

#### AWS

Within AWS there are alternatives to the tools: 

- AWS batch: this task has a scheduled execution requirement, not a continuous or real-time processing requirement, 
therefore Batch is better than using Fargate or EC2 independently. 
- AWS ECR: job definitions in AWS batch use container images, and ECR a convenient choice within AWS. 
- AWS Fargate: for this small task use case EC2 or EKS are more complicated and not needed.  
- Lambda: lambda functions can be triggered by various AWS services, which is perfect for this use case when this 
job should start only after a file is delivered to an s3 bucket. 


There are so many alternative approaches. Here are a few that come to mind: 

- Just use Lambda: upload this worker as a zip file to s3, create a terraform config.yml, and use aws cloudwatch event as a trigger 
- Airflow as the trigger (bad option, because we don't need a server running at all times)
- Super simple: cron as the trigger (data updates are fairly standarized), some lightweight cloud server like digital
ocean, or even just running locally. 


#### Openai 

There are lots of alternatives to consider (Anthropic's Claude, Bard, etc.), but we started with openai, liked the 
results from the model "gpt-3.5-turbo", and the pricing is resonable. As the number of domains being run increased, 
it might make sense to revisit this decision. 

#### Telegram 

This was just for fun! Its nice to get a message to your phone to know the service is running properly, especially when
away from the computer. Also, its nice to invite the team to get the notifications as well. 

## Challenges and learnings 

Challenges while building the project: 

- Figuring out the right AWS setup for this project. Here I learned about the best path by talking to our data engineers.  
- Setting up AWS Batch, which was an AWS service I haven't used before. 
- Finding the right metrics to include: working with stakeholders to find just the right metrics to include in the 
results. For example, at first we were including metrics for the highest and lowest value conversion rate in the 
industry, but that was acting more like anomaly detection, so we switched it to top and bottom 10% for each metric. 
- Finding the right way to show certain metrics: working with stakeholders, we dcided to bin certain values because 
bcause otherwise we were giving too much data away for free (this is published on free to access pages)
- Openai api throwing lots of errors: I had to put in max retries for the calls of > 50 just to get through the job 
because the api returned so many errors 
- Prompt engineering: working with stakeholders to get the right output in the right format using the right style. 
- Slow openai response times: this job can take > 20 hours to run for all domains.


## Further Improvements

There are many things can be improved from this project if I spent more time: 

- Implement `asyncio` to speed up the openai api results: this is an I/O task, and concurrency would speed up the 
results without exceeding openai rate limits
- Comprehensive testing
- Implement CI/CD (Github actions or CircleCI)
- Terraform: a consistent and reliable to manage aws infrastructure resources




