select account_id from {{ ref('fct_account_month') }}
where month_end != last_day(month_end)
   or month_end > cast('{{ var("cutoff") }}' as date)
   or scheduled_due is null or scheduled_due < 0
   or (observed and (days_past_due is null or days_past_due < 0 or actual_paid is null or actual_paid < 0))
   or (not observed and (days_past_due is not null or actual_paid is not null))
union all
select account_id from {{ ref('fct_account_month') }}
group by account_id, month_end having count(*) > 1
