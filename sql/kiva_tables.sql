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


-- Create Primary View

CREATE VIEW kiva_loan_view AS
SELECT
 l.id, l.name, l.funded_amount, l.funded_date, l.status, l.planned_expiration_date,
 l.posted_date, l.sector, l.activity, l.loan_amount, l.lender_count,
 l.location_country AS country, l.location_country_code AS country_code, l.location_town AS town,
 l.location_geo_lat AS latitude, l.location_geo_long AS longitude,
 l.bonus_credit_eligibility, l.description_en AS description,
 l.use_text, l.tag_text,
 l.terms_disbursal_amount, l.terms_disbursal_currency,
 l.terms_disbursal_date, l.terms_loan_amount, l.terms_loss_liability_nonpayment,
 l.terms_repayment_term, l.journal_totals_entries,
 b.borrower_count, b.m_borrower_count, b.f_borrower_count, b.pic_borrower_count
FROM loan l
LEFT OUTER JOIN (
     SELECT loan_id,
       sum(case when loan_id IS NOT NULL then 1 else 0 end) as borrower_count,
       sum(case when gender  = 'M' then 1 else 0 end) as m_borrower_count,
       sum(case when gender  = 'F' then 1 else 0 end) as f_borrower_count,
       sum(case when pictured IS TRUE then 1 else 0 end) as pic_borrower_count
     FROM loan_borrower
     GROUP BY loan_id
) b ON b.loan_id = l.id
WHERE l.status IN ('expired', 'funded');
