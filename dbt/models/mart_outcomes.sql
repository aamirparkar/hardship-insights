select jurisdiction, product, contact_cohort,
       count(*) episodes,
       count(*) filter(where not mature) immature,
       count(*) filter(where mature) mature,
       count(*) filter(where mature and not complete_followup) missing_followup,
       count(*) filter(where eligible) eligible,
       count(*) filter(where is_stable) stable_count,
       count(*) filter(where is_stable) * 1.0 / nullif(count(*) filter(where eligible), 0) stability_rate,
       count(*) filter(where eligible) * 1.0 / nullif(count(*) filter(where mature), 0) followup_coverage
from {{ ref('fct_episode_outcome') }}
group by jurisdiction, product, contact_cohort
