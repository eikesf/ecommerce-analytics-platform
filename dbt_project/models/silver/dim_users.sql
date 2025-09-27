with stg_users as (

    select * from {{ref('stg_users')}}

)

select
    user_id,
    email,
    username,
    city,
    street,
    zipcode
from stg_users