select account_id, request_id, customer_id, product, currency,
       cast(monthly_due as decimal(12,2)) monthly_due
from {{ source('raw', 'raw_accounts') }}
