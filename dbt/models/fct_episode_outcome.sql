with episodes as (
    select *, case when planned_end_date = last_day(planned_end_date)
                   then last_day(planned_end_date + interval '3 months')
                   else last_day(planned_end_date + interval '2 months') end horizon_date
    from {{ ref('fct_assistance') }}
), observations as (
    select e.episode_id, e.request_id, e.account_id, e.start_date, e.planned_end_date,
           e.horizon_date <= cast('{{ var("cutoff") }}' as date) mature,
           count(m.month_end) filter(where m.observed) observed_months,
           count(m.month_end) filter(where m.observed and m.days_past_due = 0) current_months
    from episodes e
    left join {{ ref('fct_account_month') }} m
      on e.account_id = m.account_id
     and m.month_end > e.planned_end_date
     and m.month_end <= e.horizon_date
    group by all
)
select o.*, a.jurisdiction, a.product, a.channel,
       case when a.days_past_due is null then 'Unknown'
            when a.days_past_due = 0 then 'Early contact' else 'In arrears' end contact_cohort,
       observed_months = 3 complete_followup,
       mature and observed_months = 3 eligible,
       mature and observed_months = 3 and current_months = 3 as is_stable
from observations o
join {{ source('raw', 'fct_application') }} a using(request_id)
