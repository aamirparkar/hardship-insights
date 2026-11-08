select account_id, cast(month_end as date) month_end,
       cast(observed as boolean) observed,
       cast(days_past_due as integer) days_past_due,
       cast(scheduled_due as decimal(12,2)) scheduled_due,
       cast(actual_paid as decimal(12,2)) actual_paid
from {{ source('raw', 'raw_account_months') }}
