select c.account_id from {{ ref('dim_account') }} c
left join {{ source('raw', 'fct_application') }} a using(request_id)
where c.customer_id is null or c.customer_id != a.customer_id
   or c.product is null or c.product != a.product
   or c.currency is null or c.currency != a.currency
   or c.monthly_due is null or c.monthly_due <= 0
