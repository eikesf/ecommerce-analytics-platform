select
    id as product_id,
    title as product_title,
    price as product_price,
    category as product_category,
    _loaded_at
from {{ source('bronze', 'products') }}