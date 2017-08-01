import json
import requests
from sqlalchemy import create_engine
from sqlalchemy import Table, Column
from sqlalchemy import Integer, String, MetaData, Date, Boolean, Float


def get_partner_record(partner):
    rating = partner.get('rating', None)
    delinquency_rate = partner.get('delinquency_rate', None)
    default_rate = partner.get('default_rate', None)

    if type(rating) is str:
        rating = None

    if type(delinquency_rate) is str:
        delinquency_rate = None

    if type(default_rate) is str:
        default_rate = None

    return {'id': partner.get('id', None),
            'name': partner.get('name', None),
            'rating': rating,
            'status': partner.get('status', None),
            'start_date': partner.get('start_date', None),
            'delinquency_rate': delinquency_rate,
            'default_rate': default_rate,
            'total_amount_raised': partner.get('total_amount_raised', None),
            'loans_posted': partner.get('loans_posted', None),
            'charges_fees_and_interest': partner.get('charges_fees_and_interest', None),
            'average_loan_size_percent_per_capita_income': partner.get('average_loan_size_percent_per_capita_income', None),
            'loans_at_risk_rate': partner.get('loans_at_risk_rate', None),
            'currency_exchange_loss_rate': partner.get('currency_exchange_loss_rate', None)
            }


def process_kiva_partners(conn, partner_table):
    api_url = 'http://api.kivaws.org/v1/partners.json'
    response = requests.get(api_url).text
    resp_obj = json.loads(response)
    kiva_partners = resp_obj['partners']

    kiva_partners_db = []
    for partner_index, partner in enumerate(kiva_partners):
        print('processing partner', partner_index)
        partner_rec = get_partner_record(partner)
        conn.execute(partner_table.insert(), [partner_rec])


def main():
    engine = create_engine(
        'postgresql://ubuntu:ubuntu@ec2-13-59-36-9.us-east-2.compute.amazonaws.com:5432/ubuntu')
    conn = engine.connect()
    metadata = MetaData()

    partner_table = Table('partner', metadata,
                          Column('id', Integer, primary_key=True),
                          Column('name', String),
                          Column('status', String),
                          Column('rating', Float),
                          Column('start_date', Date),
                          Column('delinquency_rate', Float),
                          Column('default_rate', Float),
                          Column('total_amount_raised', ),
                          Column('loans_posted', Integer),
                          Column('charges_fees_and_interest', Boolean),
                          Column(
                              'average_loan_size_percent_per_capita_income', Float),
                          Column('loans_at_risk_rate', Float),
                          Column('currency_exchange_loss_rate', Float))
    process_kiva_partners(conn, partner_table)


if __name__ == '__main__':
    main()
