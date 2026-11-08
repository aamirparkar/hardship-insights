-- A minimal date dimension shared by account and support facts.
select cast(d as date) date_day, year(d) year_number, month(d) month_number
from generate_series(
    (select min(notice_date) from {{ source('raw', 'fct_application') }}),
    cast('{{ var("cutoff") }}' as date), interval '1 day'
) t(d)
