create table category
(
    id   integer not null
        constraint category_pk
            primary key,
    name text
);

alter table category
    owner to mard;

create table product
(
    id         integer not null
        constraint product_pk
            primary key,
    asin       text
        constraint product_k
            unique,
    title      text,
    "group"    text,
    sales_rank integer
);

alter table product
    owner to mard;

create table product_category
(
    prod_id integer not null
        constraint product_category_fk1
            references product,
    cat_id  integer not null
        constraint product_category_fk2
            references category,
    index   integer not null,
    constraint product_category_pk
        primary key (prod_id, cat_id, index)
);

alter table product_category
    owner to mard;

create table product_similar
(
    first_prod_id  integer
        constraint product_similar_fk1
            references product,
    second_prod_id integer
        constraint product_similar_fk2
            references product,
    constraint product_similar_pk
        unique (first_prod_id, second_prod_id)
);

alter table product_similar
    owner to mard;

create table review
(
    time        timestamp,
    prod_id     integer
        constraint review_fk
            references product,
    customer_id text,
    rating      integer,
    votes       integer,
    helpful     integer
);

alter table review
    owner to mard;


