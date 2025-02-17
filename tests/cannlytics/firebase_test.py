"""
Test Firebase Module
Created: 1/27/2021
Updated: 7/20/2021
"""
# Standard imports.
import os
import sys

# External imports.
import environ
from google.cloud.firestore_v1.collection import CollectionReference
from google.cloud.firestore_v1.document import DocumentReference

# Internal imports.
sys.path.append('../..')
from cannlytics import firebase # pylint: disable=import-error
from cannlytics.utils.utils import get_keywords, snake_case # pylint: disable=import-error


#------------------------------------------------------------#
# Test Firestore
#------------------------------------------------------------#

def test_firestore():
    """Test Firestore functions by managing a test document."""

    # Initialize Firebase.
    env = environ.Env()
    env.read_env('../.env')
    credentials = env('GOOGLE_APPLICATION_CREDENTIALS')
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials
    db = firebase.initialize_firebase()

    # Create a collection reference.
    col_ref = firebase.create_reference(db, 'tests')
    assert isinstance(col_ref, CollectionReference)

    # Create a document reference.
    doc_ref = firebase.create_reference(db, 'tests/firebase_test')
    assert isinstance(doc_ref, DocumentReference)

    # Create a document.
    firebase.update_document('tests/firebase_test', {'user': 'CannBot'})

    # Update a document.
    firebase.update_document('tests/firebase_test', {'test': 'firebase_test'})

    # Get the document.
    data = firebase.get_document('tests/firebase_test')
    assert data['user'] == 'CannBot'
    assert data['test'] == 'firebase_test'

    # Get a collection.
    filters = [{'key': 'test', 'operation': '==', 'value': 'firebase_test'}]
    docs = firebase.get_collection('tests', filters=filters)
    assert docs[0]['test'] == 'firebase_test'

    # Add an element to an array in a document.
    firebase.add_to_array('tests/firebase_test', 'likes', 'Testing')
    data = firebase.get_document('tests/firebase_test')
    assert 'Testing' in data['likes']

    # Remove an element from an array in a document.
    firebase.remove_from_array('tests/firebase_test', 'likes', 'Testing')
    data = firebase.get_document('tests/firebase_test')
    assert 'Testing' not in data['likes']

    # Increment a value in a document.
    firebase.increment_value('tests/firebase_test', 'runs')
    data = firebase.get_document('tests/firebase_test')
    assert data['runs'] > 0

    # Import .csv data to Firestore.
    ref = 'tests/test_collections/licensees'
    data_file = './assets/data/licensees_partial.csv'
    firebase.import_data(db, ref, data_file)

    # TODO: Test import .xlsx data to Firestore.

    # TODO: Test import .txt data to Firestore.

    # Export data to .csv from Firestore.
    output_csv_file = './assets/data/licensees_test.csv'
    output_xlsx_file = './assets/data/licensees_test.xlsx'
    firebase.export_data(db, ref, output_csv_file)

    # Export data to .xlsx from Firestore.
    firebase.export_data(db, ref, output_xlsx_file)


def test_create_log():
    """Test create a log."""

    # Initialize Firebase.
    env = environ.Env()
    env.read_env('../.env')
    credentials = env('GOOGLE_APPLICATION_CREDENTIALS')
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials
    db = firebase.initialize_firebase()

    # Create a test log.
    user = {
        'uid': 'test',
        'display_name': 'CannBot',
        'email': 'bot@cannlytics.com',
        'photo_url': 'https://robohash.org/bot@cannlytics.com',
    }
    logs = 'tests/test_collections/logs'
    firebase.create_log(logs, user, 'Test log.', 'test', 'create_log')


#------------------------------------------------------------#
# Test Firebase Storage
#------------------------------------------------------------#

def test_storage():
    """Test Firebase Storage by managing a test file."""

    # Initialize Firebase.
    env = environ.Env()
    env.read_env('../.env')
    credentials = env('GOOGLE_APPLICATION_CREDENTIALS')
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials
    firebase.initialize_firebase()

    # Define file names.
    bucket_name = env('FIREBASE_STORAGE_BUCKET')
    bucket_folder = 'tests/assets/pdfs'
    destination_blob_name = 'tests/assets/pdfs/pandas_cheat_sheet.pdf'
    local_folder = './assets/pdfs'
    source_file_name = './assets/pdfs/Pandas_Cheat_Sheet.pdf'
    download_folder = './assets/downloads/pdfs'
    download_file_name = './assets/downloads/pdfs/Pandas_Cheat_Sheet.pdf'
    file_name = 'pandas_cheat_sheet.pdf'
    file_copy = 'pandas_cheat_sheet_copy.pdf'
    newfile_name = 'tests/assets/pdfs/' + file_copy

    # Upload a file to a Firebase Storage bucket.
    firebase.upload_file(bucket_name, destination_blob_name, source_file_name)

    # Upload all files in a folder to a Firebase Storage bucket.
    firebase.upload_files(bucket_name, bucket_folder, local_folder)

    # List all files in the Firebase Storage bucket folder.
    files = firebase.list_files(bucket_name, bucket_folder)
    assert isinstance(files, list)

    # Download a file from Firebase Storage.
    firebase.download_file(bucket_name, destination_blob_name, download_file_name)

    # Download all files in a given Firebase Storage folder.
    firebase.download_files(bucket_name, bucket_folder, download_folder)

    # Rename a file in the Firebase Storage bucket.
    firebase.rename_file(bucket_name, bucket_folder, file_name, newfile_name)

    # Delete a file from the Firebase Storage bucket.
    firebase.delete_file(bucket_name, bucket_folder, file_copy)


#------------------------------------------------------------#
# Authentication
#------------------------------------------------------------#

def test_auth():
    """Test Firebase Authentication by managing a user."""

    # Initialize Firebase
    env = environ.Env()
    env.read_env('../.env')
    credentials = env('GOOGLE_APPLICATION_CREDENTIALS')
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials
    firebase.initialize_firebase()

    # Create account.
    name = 'CannBot'
    email = 'contact@cannlytics.com'
    claims = {'organizations': ['Cannlytics']}
    user, _ = firebase.create_user(name, email, notification=True)

    # Create and get custom claims.
    firebase.create_custom_claims(user.uid, email=email, claims=claims)
    custom_claims = firebase.get_custom_claims(email)

    # Create custom token.
    token = firebase.create_custom_token(user.uid, email=None, claims=custom_claims)
    assert isinstance(token, bytes)

    # Get user.
    user = firebase.get_user(email)

    # Get all users.
    all_users = firebase.get_users()
    assert isinstance(all_users, list)

    # Update user.
    photo_url = f'https://robohash.org/{email}?set=set5'
    user = firebase.update_user(user, {'photo_url': photo_url})
    assert user.photo_url == 'https://robohash.org/contact@cannlytics.com?set=set5'

    # Delete a user.
    firebase.delete_user(user.uid)


#------------------------------------------------------------#
# Secret Manager
#------------------------------------------------------------#

def test_secret_manager():
    """Test Secret Manager by creating a secret, updating the version
    of the secret, then deleting the secret."""

    # Initialize Firebase
    env = environ.Env()
    env.read_env('../../.env')
    credentials = env('GOOGLE_APPLICATION_CREDENTIALS')
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials
    firebase.initialize_firebase()

    # Mock license.
    license_data = {
        'license_number': 'test',
        'license_type': 'lab',
        'state': 'OK',
        'user_api_key': '123',
    }
    license_number = license_data['license_number']
    user_api_key = license_data['user_api_key']

    # Create a secret.
    project_id = 'cannlytics'
    secret_id = f'{license_number}-secret'
    try:
        version_id = firebase.create_secret(project_id, secret_id, user_api_key)
    except: # AlreadyExists error
        pass # Secret may already be created.

    # Add the secret's secret data.
    secret = firebase.add_secret_version(project_id, secret_id, user_api_key)
    version_id = secret.split('/')[-1]

    # Get the secret.
    # In production the secret ID and version ID are stored with the license data.
    user_api_key = firebase.access_secret_version(project_id, secret_id, version_id)
    assert user_api_key == license_data['user_api_key']

#------------------------------------------------------------#
# Misc
#------------------------------------------------------------#

def test_get_keywords():
    """Test get keywords."""
    keywords = get_keywords('Gorilla Glue')
    assert 'gorilla' in keywords and 'glue' in keywords


def test_snake_case():
    """Test string to snake-case."""
    key = snake_case('% Dev. from the mean')
    assert key == 'percent_dev_from_the_mean'


if __name__ == '__main__':

    test_secret_manager()
