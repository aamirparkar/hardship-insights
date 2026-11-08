select episode_id, request_id, account_id,
       cast(start_date as date) start_date,
       cast(planned_end_date as date) planned_end_date, assistance_type
from {{ source('raw', 'raw_assistance') }}
