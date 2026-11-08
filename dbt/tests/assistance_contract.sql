select e.episode_id from {{ ref('fct_assistance') }} e
left join {{ source('raw', 'fct_application') }} a using(request_id)
left join {{ ref('dim_account') }} c on e.account_id = c.account_id
where a.request_id is null or a.status != 'approved'
   or c.request_id != e.request_id
   or e.start_date is null or e.planned_end_date is null
   or e.start_date < a.decision_date or e.planned_end_date < e.start_date
   or e.start_date > cast('{{ var("cutoff") }}' as date)
