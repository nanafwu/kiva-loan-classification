-- SELECT statements

SELECT status, count(1)
FROM loan
GROUP BY status


SELECT date_trunc('month', posted_date) AS max_posted_date, count(*)
FROM loan
GROUP BY max_posted_date
ORDER BY max_posted_date;


SELECT file_index, max(date_trunc('month', posted_date)) AS max_posted_date, min(date_trunc('month', posted_date)) AS min_posted_date, count(*)
FROM loan
GROUP BY file_index
ORDER BY max_posted_date;

-- Create Views
 funded_date                            | timestamp without time zone |
 status                                 | character varying(100)      |
 planned_expiration_date                | timestamp without time zone |
 posted_date                            | timestamp without time zone |
 sector                                 | character varying(100)      |
 activity                               | character varying(1000)     |
 loan_amount                            | integer                     |
 lender_count                           | integer                     |
 location_country_code                  | character varying(10)       |
 location_country                       | character varying(100)      |
 location_town                          | character varying(1000)     |
 location_geo_level                     | character varying(100)      |
 location_geo_type                      | character varying(100)      |
 location_geo_lat                       | numeric                     |
 location_geo_long                      | numeric                     |
 partner_id                             | integer                     |
 bonus_credit_eligibility               | boolean                     |
 description_en                         | text                        |
 use_text                               | text                        |
 tag_text                               | text                        |
 terms_disbursal_amount                 | integer                     |
 terms_disbursal_currency               | character varying(10)       |
 terms_disbursal_date                   | timestamp without time zone |
 terms_loan_amount                      | integer                     |
 terms_loss_liability_currency_exchange | character varying(20)       |
 terms_loss_liability_nonpayment        | character varying(20)       |
 terms_repayment_term                   | smallint                    |
 journal_totals_entries                 | smallint                    |

SELECT
 l.id, l.name, l.funded_amount, l.funded_date, l.status, l.planned_expiration_date,
 l.posted_date, l.sector, l.activity, l.loan_amount, l.lender_count,
 l.location_country AS country, l.location_country_code AS country_code, l.location_town AS town,
 l.location_geo_lat AS latitude, l.location_geo_long AS longitude,
 l.bonus_credit_eligibility, l.description_en AS description,
 l.use_text, l.tag_text,
 l.terms_disbursal_amount, l.terms_disbursal_currency,
 l.terms_disbursal_date, l.terms_loan_amount, l.terms_loss_liability_nonpayment,
 p.name AS partner_name, p.status AS partner_status, p.rating AS partner_rating,
 p.delinquency_rate AS partner_delinquency_rate, p.default_rate AS partner_rate,
 p.total_amount_raised AS partner_total_amount_raised, p.loans_posted AS partner_loans_posted,
 p.charges_fees_and_interest AS partner_charges_fees_and_interest,
 p.average_loan_size_percent_per_capita_income AS partner_average_loan_size_percent_per_capita_income,
 p.loans_at_risk_rate AS partner_loans_at_risk_rate
FROM loan l
LEFT OUTER JOIN partner p ON l.partner_id = p.id
LIMIT 10

-- CREATE Tables

CREATE TABLE loan (
    id INTEGER NOT NULL,
    name VARCHAR(100),
    funded_amount INTEGER,
    funded_date TIMESTAMP,
    status VARCHAR(100),
    planned_expiration_date TIMESTAMP,
    posted_date TIMESTAMP,
    sector VARCHAR(100),
    activity VARCHAR(1000),
    loan_amount INTEGER,
    lender_count INTEGER,
    location_country_code VARCHAR(10),
    location_country VARCHAR(100),
    location_town VARCHAR(1000),
    location_geo_level VARCHAR(100),
    location_geo_type VARCHAR(100),
    location_geo_lat decimal,
    location_geo_long decimal,
    partner_id INTEGER,
    bonus_credit_eligibility BOOLEAN,
    description_en TEXT,
    use_text TEXT,
    tag_text TEXT,
    terms_disbursal_amount INTEGER,
    terms_disbursal_currency VARCHAR(10),
    terms_disbursal_date TIMESTAMP,
    terms_loan_amount INTEGER,
    terms_loss_liability_currency_exchange VARCHAR(20),
    terms_loss_liability_nonpayment VARCHAR(20),
    terms_repayment_term SMALLINT,
    journal_totals_entries SMALLINT,
    file_index SMALLINT,
    payments TEXT,
    PRIMARY KEY (id)
);

CREATE INDEX loan_status_idx_new ON loan (status);
CREATE INDEX loan_funded_amount_idx_new ON loan (funded_amount);
CREATE INDEX loan_funded_date_idx_new ON loan (funded_date);
CREATE INDEX loan_loan_amount_idx_new ON loan (loan_amount);


CREATE TABLE loan_lender (
   lender_id VARCHAR(500),
   loan_id INTEGER NOT NULL,
   file_index SMALLINT,
   PRIMARY KEY (loan_id, lender_id)
);


CREATE TABLE loan_borrower (
   loan_id INTEGER,
   first_name VARCHAR(250),
   last_name VARCHAR(250),
   pictured BOOLEAN,
   gender VARCHAR(5),
   file_index SMALLINT
);

CREATE INDEX loan_borrower_idx ON loan_borrower (loan_id);


CREATE TABLE partner (
       id INTEGER,
       name VARCHAR(1000),
       status VARCHAR(50),
       rating DECIMAL,
       start_date TIMESTAMP,
       delinquency_rate DECIMAL,
       default_rate DECIMAL,
       total_amount_raised BIGINT,
       loans_posted INTEGER,
       charges_fees_and_interest BOOLEAN,
       average_loan_size_percent_per_capita_income DECIMAL,
       loans_at_risk_rate DECIMAL,
       currency_exchange_loss_rate DECIMAL,
       PRIMARY KEY(id)
);
