select
    id as user_id,
    email,
    username,
    address ->> 'city' as city,
    address ->> 'street' as street,
    address ->> 'zipcode' as zipcode,
    _loaded_at
from {{ source('bronze', 'users') }}