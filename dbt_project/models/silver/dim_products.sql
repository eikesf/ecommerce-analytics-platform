with stg_products as (

    select * from {{ ref('stg_products') }}

)

select
    product_id,
    product_title,
    product_price,
    product_category
from stg_products