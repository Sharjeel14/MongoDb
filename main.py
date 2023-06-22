import os
from llama_index import ListIndex, SimpleWebPageReader
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from concurrent.futures import ThreadPoolExecutor
import json
import boto3
import botocore.exceptions
import pymongo

# os.environ['OPENAI_API_KEY'] = "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"


application = Flask(__name__)
CORS(application)
application.config['SECRET_KEY'] = 'AIFUNOCUQJOR9C20NTV2N%^%$#$#^^&^*^*&*'

bucket_name = 'controlnet-images'
key = 'data.json'
client = pymongo.MongoClient(
    "mongodb://mongo:z9nNQPhxuelyTjRvXJtF@containers-us-west-70.railway.app:8067")
db = client['Sharjeel']
collection = db['mydb']


@application.route('/', defaults={'path': ''}, methods=['GET'])
@application.route('/<path:path>')
def catch_all(path):
    return render_template('index.html')


@application.route('/')
def index():
    return render_template('index.html')

# Create a function to generate auto-incrementing IDs


def get_next_sequence_value(sequence_name):
    sequence = collection.find_one_and_update(
        {"_id": sequence_name},
        {"$inc": {"number of records": 1}},
        upsert=True,
        return_document=True
    )
    return sequence["number of records"]


# def create_json_file(bucketname, filekey, json_data):
#     session = boto3.Session(
#         aws_access_key_id='AKIA53RMBYHOR6F6GOXG',
#         aws_secret_access_key='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'
#     )

#     s3_client = session.client('s3')
#     try:
#         # Check if the file already exists
#         s3_client.head_object(Bucket=bucketname, Key=filekey)
#         print(f"File '{filekey}' already exists in the bucket '{bucketname}'.")
#     except botocore.exceptions.ClientError as e:
#         if e.response['Error']['Code'] == '404':
#             # File does not exist, create it
#             existing_data = []

#             try:
#                 response = s3_client.get_object(Bucket=bucketname, Key=filekey)
#                 existing_data = json.loads(response['Body'].read().decode('utf-8'))
#                 if not isinstance(existing_data, list):
#                     existing_data = [existing_data]
#             except botocore.exceptions.ClientError as e:
#                 if e.response['Error']['Code'] != 'NoSuchKey':
#                     print(f"An error occurred: {e}")
#                     return

#             existing_data.append(json_data)
#             json_data = json.dumps(existing_data)
#             s3_client.put_object(Body=json_data, Bucket=bucketname, Key=filekey)
#             print(f"Created file '{filekey}' in the bucket '{bucketname}'.")
#         else:
#             # Other error occurred
#             print(f"An error occurred: {e}")


# def store_json_data(bucketnames, keys, new_data):
#     # Create a session with your AWS access key and secret key

#     session = boto3.Session(
#         aws_access_key_id='AKIA53RMBYHOR6F6GOXG',
#         aws_secret_access_key='Mwvyfgu25V9Ou1Z6I29SPWdLX4F9EbkRM97N0Gb9'
#     )

#     # Create an S3 client using the session
#     s3_client = session.client('s3')

#     # Fetch existing JSON data from S3
#     response = s3_client.get_object(
#         Bucket=bucketnames,
#         Key=keys
#     )
#     existing_data = json.loads(response['Body'].read().decode('utf-8'))

#     # Append new data to existing data
#     if isinstance(existing_data, list):
#         # print(new_data)

#         existing_data.append(new_data)
#         print("datastored")
#         # print(existing_data)

#     # else:
#     #     existing_data = [existing_data, new_data]

#     # Convert the updated data to JSON format
#     json_data = json.dumps(existing_data)
#     print('datadumped')
#     # Upload the updated JSON data to S3
#     response = s3_client.put_object(
#         Bucket=bucketnames,
#         Key=keys,
#         Body=json_data
#     )
#     print("Stored")
#     if response['ResponseMetadata']['HTTPStatusCode'] == 200:
#         print("New JSON data stored in S3 successfully!")
#     else:
#         print("Failed to store new JSON data in S3.")


# def fetch_json_data(bucketname, keys):
#     # Create a session with your AWS access key and secret key
#     session = boto3.Session(
#         aws_access_key_id='AKIA53RMBYHOR6F6GOXG',
#         aws_secret_access_key='Mwvyfgu25V9Ou1Z6I29SPWdLX4F9EbkRM97N0Gb9'
#     )

#     # Create an S3 client using the session
#     s3_client = session.client('s3')

#     # Retrieve the JSON data from S3
#     response = s3_client.get_object(
#         Bucket=bucketname,
#         Key=keys
#     )

#     # Read the JSON data from the response
#     json_data = response['Body'].read().decode('utf-8')

#     # Parse the JSON data
#     data = json.loads(json_data)

#     return data


file_key = 'data.json'
sample_data = {'url': 'http://website.com',
               'Adapted Reading Passage': 'content',
               'Summary': 'summ',
               'Key Vocabulary Words': 'words',
               'Multiple Choice Questions': 'mcqs',
               'Short Answer Questions': 'short',
               'Open-ended Prompts': 'long_q',
               }

# create_json_file(bucket_name, file_key, sample_data)


def get_mcqs(query_engine):
    mcqs = query_engine.query(
        "Please give me 2 to 4 mcqs  with 4 possible options from this content."
        "The format should be like 1) what is a fruit"
        " from these options. 1)seed 2)wood 3)apple 4)Moon"
    )
    return mcqs


def get_short_questions(query_engine):
    short = query_engine.query(
        "Please give me the 2 to 4 short questions from the provided document,"
        " the question should be valid and make sense")
    return short


def get_long_questions(query_engine):
    long_q = query_engine.query(
        "Please give me the 2 to 4 long questions from the provided document, "
        "the question should be valid and make sense")
    return long_q


def get_vocabulary(query_engine):
    vocabulary = query_engine.query(
        "Please give me the key vocabulary words and its definitions from the provided documents")
    return vocabulary


def get_content(query_engine):
    content = query_engine.query("Please give me the content of the document")
    return content


def get_summary(query_engine):
    summary = query_engine.query(
        "Please give me the effective Summary of the document")
    return summary


@application.route('/data', methods=["POST"])
def contents():
    try:
        data = request.get_json()
        url = data['url']
        db_url = collection.find({'url': url})
        count = collection.count_documents({'url': url})
        if count > 0:
            for item in db_url:
                fetched_data = item
            if fetched_data:
                if fetched_data['url'] == url:
                    print('data found')
                    return jsonify({
                        'Adapted Reading Passage': fetched_data['Adapted Reading Passage'],
                        'Summary': fetched_data['Summary'],
                        'Key Vocabulary Words': fetched_data['Key Vocabulary Words'],
                        'Multiple Choice Questions': fetched_data['Multiple Choice Questions'],
                        'Short Answer Questions': fetched_data['Short Answer Questions'],
                        'Open-ended Prompts': fetched_data['Open-ended Prompts'],
                    })
        else:
            print('No Data Found')
            # documents = TrafilaturaWebReader().load_data([url])
            # documents = SimpleWebPageReader(html_to_text=True).load_data([url])
            # print(documents)
            # index = ListIndex.from_documents(documents)
            # query_engine = index.as_query_engine()

            # # Create a thread pool executor
            # executor = ThreadPoolExecutor()

            # # Submit the functions to the executor
            # mcqs_future = executor.submit(get_mcqs, query_engine)
            # short_questions_future = executor.submit(
            #     get_short_questions, query_engine)
            # long_questions_future = executor.submit(
            #     get_long_questions, query_engine)
            # vocabulary_future = executor.submit(get_vocabulary, query_engine)
            # content_future = executor.submit(get_content, query_engine)
            # summary_future = executor.submit(get_summary, query_engine)

            # # Retrieve the results from the futures
            # mcqs = mcqs_future.result()
            # short = short_questions_future.result()
            # long_q = long_questions_future.result()
            # vocabulary = vocabulary_future.result()
            # content = content_future.result()
            # summary = summary_future.result()
            # new_data = {
            #     'url': url,
            #     'Adapted Reading Passage': content.response,
            #     'Summary': summary.response,
            #     'Key Vocabulary Words': vocabulary.response,
            #     'Multiple Choice Questions': mcqs.response,
            #     'Short Answer Questions': short.response,
            #     'Open-ended Prompts': long_q.response,
            # }
            new_data = {
                "_id": get_next_sequence_value("records"),
                'url': url,
                'Adapted Reading Passage': 'content.response',
                'Summary': 'summary.response',
                'Key Vocabulary Words': 'vocabulary.response',
                'Multiple Choice Questions': 'mcqs.response',
                'Short Answer Questions': 'short.response',
                'Open-ended Prompts': 'long_q.response',
            }
            collection.insert_one(new_data)

            return jsonify(new_data)
    except Exception as e:
        print(e)
        return jsonify(e)


if __name__ == "__main__":
    application.run(debug=True, host='0.0.0.0', port=5000)
