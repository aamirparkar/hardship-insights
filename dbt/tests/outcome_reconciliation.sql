select episode_id from {{ ref('fct_episode_outcome') }}
where observed_months > 3 or current_months > observed_months
   or (is_stable and not eligible) or (eligible and not mature)
union all
select episode_id from {{ ref('fct_assistance') }}
where episode_id not in (select episode_id from {{ ref('fct_episode_outcome') }})
