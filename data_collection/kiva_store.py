import json
import numpy as np
import requests
from sqlalchemy import create_engine
from sqlalchemy import Table, Column
from sqlalchemy import Integer, String, MetaData, Date, Boolean, Float
from requests_oauthlib import OAuth1
import sys
import cnfg


def get_loan_record(loan, filename_index):

    location = loan.get('location', {})
    location_geo = location.get('geo', {})
    location_geo_lat = None
    location_geo_long = None

    location_geo_type = location_geo.get('type', None)
    if (location_geo_type == 'point'):
        location_coords = location_geo.get('pairs', '')
        location_geo_lat = float(location_coords.split(' ')[0])
        location_geo_long = float(location_coords.split(' ')[1])

    description_tag = loan.get('description', {})
    texts_tag = description_tag.get('texts', {})

    tags = loan.get('tags', [])
    terms = loan.get('terms', {})

    loss_liability = terms.get('loss_liability', {})
    journal_totals = loan.get('journal_totals', {})

    payments = loan.get('payments', None)
    payments = str(payments) if payments else None

    return {'id': loan.get('id', {}),
            'name': loan.get('name', {}),
            'funded_amount': loan.get('funded_amount', None),
            'funded_date': loan.get('funded_date', None),
            'status': loan.get('status', None),
            'planned_expiration_date': loan.get('planned_expiration_date',
                                                None),
            'posted_date': loan.get('posted_date', None),
            'sector': loan.get('sector', None),
            'activity': loan.get('activity', None),
            'loan_amount': loan.get('loan_amount', None),
            'lender_count': loan.get('lender_count', None),
            'location_country_code': location.get('country_code', None),
            'location_country': location.get('country', None),
            'location_geo_level': location_geo.get('level', None),
            'location_geo_type': location_geo_type,
            'location_town': location.get('town', None),
            'location_geo_lat': location_geo_lat,
            'location_geo_long': location_geo_long,
            'partner_id': loan.get('partner_id', None),
            'bonus_credit_eligibility': loan.get('bonus_credit_eligibility',
                                                 None),
            'description_en':  texts_tag.get('en', None),
            'use_text': loan.get('use', None),
            'tag_text': ' '.join([t['name'] for t in tags]),
            'terms_disbursal_amount': terms.get('disbursal_amount', None),
            'terms_disbursal_currency': terms.get('disbursal_currency', None),
            'terms_disbursal_date': terms.get('disbursal_date', None),
            'terms_loan_amount': terms.get('loan_amount', None),
            'terms_loss_liability_currency_exchange':
            loss_liability.get('currency_exchange', None),
            'terms_loss_liability_nonpayment':
            loss_liability.get('nonpayment', None),
            'terms_repayment_term': terms.get('repayment_term', None),
            'journal_totals_entries': journal_totals.get('entries', 0),
            'payments': payments,
            'file_index': filename_index,
            'borrowers': loan.get('borrowers', None)}


def kiva_api(api_url):
    config_kiva = cnfg.load(".metis_config")['kiva_api']
    consumer_key = config_kiva['consumer_key']
    consumer_secret = config_kiva['consumer_secret']
    resource_owner_key = config_kiva['resource_owner_key']
    resource_owner_secret = config_kiva['resource_owner_secret']
    oauth = OAuth1(consumer_key,
                   client_secret=consumer_secret,
                   resource_owner_key=resource_owner_key,
                   resource_owner_secret=resource_owner_secret)
    response = requests.get(url=api_url, auth=oauth)
    response = response.text
    return response


def process_file_loans(filename_index, conn, loan_table,
                       loan_lender_table, loan_borrower_table):
    """
    Assumes Kiva snapshots stored under directory `kiva_ds_json`:
    For every loan and lender, get detailed information from Kiva API
    """
    filename = 'kiva_ds_json/loans_lenders/' + str(filename_index) + '.json'
    with open(filename) as data_file:
        data = json.load(data_file)
        file_loans = data['loans_lenders']

        # 1000 loans in a file, batch call in groups of 10
        for batch_index, batch_loans in enumerate(
                np.array_split(file_loans, 100)):
            batch_loan_ids = [str(loan['id']) for loan in batch_loans]
            loan_ids_str = ','.join(batch_loan_ids)
            api_url = 'https://api.kivaws.org/v1/loans/' + loan_ids_str + '.json'
            print(batch_index, ': ', api_url)
            response = kiva_api(api_url)

            try:
                loans_obj = json.loads(response)['loans']

                loan_records = []
                loan_lender_records = []
                loan_borrowers = []

                # process kiva API loan response
                for curr_loan in loans_obj:
                    loan_id = curr_loan['id']
                    if loan_id:
                        # get loan record
                        loan_rec = get_loan_record(curr_loan, filename_index)
                        borrowers = loan_rec.get('borrowers', None)

                        if borrowers:
                            for loan_borrower in borrowers:
                                loan_borrower.update({
                                    'file_index': filename_index,
                                    'loan_id': loan_id})
                                loan_borrowers.append(loan_borrower)

                        loan_records.append(loan_rec)

                # get lenders for loans from file
                for file_loan in batch_loans:
                    loan_id = file_loan['id']
                    lenders = file_loan.get('lender_ids', None)
                    if lenders:
                        loan_lender_records = loan_lender_records + \
                            [{'lender_id': lender_id, 'loan_id': loan_id,
                              'file_index': filename_index}
                             for lender_id in lenders]

                if loan_lender_records:
                    conn.execute(loan_lender_table.insert(),
                                 loan_lender_records)
                if loan_records:
                    conn.execute(loan_table.insert(), loan_records)

                if loan_borrowers:
                    conn.execute(loan_borrower_table.insert(),
                                 loan_borrowers)

            except:
                e = sys.exc_info()[0]
                print('Error, skipping batch')
                print(e)

        return loan_records


def main():
    """
    Store kiva loan, lender, and borrower data into
    `loan`, `loan_lender`, `loan_borrower` tables in database
    """
    config = cnfg.load(".metis_config")
    engine = create_engine('postgresql://{}:{}@{}:5432/{}'.format(
        config['db_user'],
        config['db_pwd'],
        config['db_host'],
        'ubuntu'))

    conn = engine.connect()
    metadata = MetaData()

    loan_table = Table('loan', metadata,
                       Column('id', Integer, primary_key=True),
                       Column('name', String),
                       Column('funded_amount', Integer),
                       Column('funded_date', Integer),
                       Column('status', String),
                       Column('planned_expiration_date', Date),
                       Column('posted_date', Date),
                       Column('sector', String),
                       Column('activity', String),
                       Column('loan_amount', Integer),
                       Column('lender_count', Integer),
                       Column('location_country_code', String),
                       Column('location_country', String),
                       Column('location_geo_level', String),
                       Column('location_geo_type', String),
                       Column('location_geo_lat', Float),
                       Column('location_geo_long', Float),
                       Column('location_town', String),
                       Column('partner_id', Integer),
                       Column('bonus_credit_eligibility', Boolean),
                       Column('description_en', String),
                       Column('use_text', String),
                       Column('tag_text', String),
                       Column('terms_disbursal_amount', Integer),
                       Column('terms_disbursal_currency', String),
                       Column('terms_disbursal_date', Date),
                       Column('terms_loan_amount', Integer),
                       Column('terms_loss_liability_currency_exchange',
                              String),
                       Column('terms_loss_liability_nonpayment', String),
                       Column('terms_repayment_term', Integer),
                       Column('journal_totals_entries', Integer),
                       Column('file_index', Integer),
                       Column('payments', String))

    loan_lender_table = Table('loan_lender', metadata,
                              Column('loan_id', Integer),
                              Column('lender_id', String),
                              Column('file_index', Integer))

    loan_borrower_table = Table('loan_borrower', metadata,
                                Column('loan_id', Integer),
                                Column('first_name', String),
                                Column('last_name', String),
                                Column('pictured', Boolean),
                                Column('gender', String),
                                Column('file_index', Integer))

    # Process files in `kiva_ds_json` directory
    for file_index in range(10, 150):
        print('-- File ', file_index)
        process_file_loans(file_index, conn, loan_table,
                           loan_lender_table, loan_borrower_table)


if __name__ == '__main__':
    main()
