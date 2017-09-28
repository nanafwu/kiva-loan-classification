# kiva-loan-classification

Documentation for Kiva API here:
https://build.kiva.org/


## Workflow
1) Store Kiva Snapshots (http://build.kiva.org/docs/data/snapshots) under directory `kiva_ds_json`
2) Gather detailed information for  `loan`, `loan_lender`, and `loan_borrower` tables
3) Create `kiva_loan_view` - See `data_collection/kiva_tables.sql`
