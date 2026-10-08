--
-- PostgreSQL database dump
--

\restrict IasfJgk2hhgilCQN7tWa8VI7w52Rr5wmYGyTyGzqPdKRvFBb5Fw3I7quvZLstCj

-- Dumped from database version 18.6
-- Dumped by pg_dump version 18.6

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: customers; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.customers (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    phone character varying(20) NOT NULL,
    email character varying(150),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    address text
);


--
-- Name: customers_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.customers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: customers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.customers_id_seq OWNED BY public.customers.id;


--
-- Name: food_items; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.food_items (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    price numeric(10,2) NOT NULL,
    category character varying(50),
    available boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: food_items_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.food_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: food_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.food_items_id_seq OWNED BY public.food_items.id;


--
-- Name: order_items; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.order_items (
    id integer NOT NULL,
    order_id integer,
    food_id integer,
    quantity integer NOT NULL,
    price numeric(10,2) NOT NULL
);


--
-- Name: order_items_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.order_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: order_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.order_items_id_seq OWNED BY public.order_items.id;


--
-- Name: orders; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.orders (
    id integer NOT NULL,
    customer_id integer,
    total_amount numeric(10,2) NOT NULL,
    payment_method character varying(30) NOT NULL,
    order_status character varying(30) DEFAULT 'Pending'::character varying,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: orders_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.orders_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: orders_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.orders_id_seq OWNED BY public.orders.id;


--
-- Name: customers id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.customers ALTER COLUMN id SET DEFAULT nextval('public.customers_id_seq'::regclass);


--
-- Name: food_items id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.food_items ALTER COLUMN id SET DEFAULT nextval('public.food_items_id_seq'::regclass);


--
-- Name: order_items id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.order_items ALTER COLUMN id SET DEFAULT nextval('public.order_items_id_seq'::regclass);


--
-- Name: orders id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orders ALTER COLUMN id SET DEFAULT nextval('public.orders_id_seq'::regclass);


--
-- Data for Name: customers; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.customers (id, name, phone, email, created_at, address) FROM stdin;
8	Ram	9708234374	\N	2026-10-03 19:22:42.812927	vill- gurmiya
9	Sneha Kumari	9608289006		2026-10-04 17:12:17.11013	college canteen
10	divya	9876543210		2026-10-04 18:41:04.279609	punjab
\.


--
-- Data for Name: food_items; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.food_items (id, name, description, price, category, available, created_at) FROM stdin;
1	Veg Thali	Fresh and tasty homemade veg thali	120.00	Main Course	t	2026-10-03 14:00:24.007746
2	Veg Noodles	Delicious vegetable noodles	90.00	Chinese	t	2026-10-03 14:00:24.007746
3	Veg Sandwich	Fresh vegetable sandwich	70.00	Snacks	t	2026-10-03 14:00:24.007746
4	Chocolate Cake	Soft and delicious chocolate cake	80.00	Dessert	t	2026-10-03 14:00:24.007746
5	Masala Tea	Fresh hot masala tea	35.00	Beverages	t	2026-10-03 19:52:28.417558
\.


--
-- Data for Name: order_items; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.order_items (id, order_id, food_id, quantity, price) FROM stdin;
1	8	1	1	120.00
2	9	1	1	120.00
3	10	1	1	120.00
4	11	1	1	120.00
5	12	1	1	120.00
\.


--
-- Data for Name: orders; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.orders (id, customer_id, total_amount, payment_method, order_status, created_at) FROM stdin;
8	8	120.00	Cash	delivered	2026-10-03 19:22:42.812927
9	9	120.00	cash	pending	2026-10-04 17:12:17.11013
10	9	120.00	cash	pending	2026-10-04 17:16:28.151719
11	10	120.00	cash	pending	2026-10-04 18:41:04.279609
12	10	114.00	cash	pending	2026-10-04 19:08:16.683409
\.


--
-- Name: customers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.customers_id_seq', 10, true);


--
-- Name: food_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.food_items_id_seq', 5, true);


--
-- Name: order_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.order_items_id_seq', 5, true);


--
-- Name: orders_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.orders_id_seq', 12, true);


--
-- Name: customers customers_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.customers
    ADD CONSTRAINT customers_pkey PRIMARY KEY (id);


--
-- Name: food_items food_items_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.food_items
    ADD CONSTRAINT food_items_pkey PRIMARY KEY (id);


--
-- Name: order_items order_items_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_pkey PRIMARY KEY (id);


--
-- Name: orders orders_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_pkey PRIMARY KEY (id);


--
-- Name: order_items order_items_food_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_food_id_fkey FOREIGN KEY (food_id) REFERENCES public.food_items(id);


--
-- Name: order_items order_items_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(id) ON DELETE CASCADE;


--
-- Name: orders orders_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id);


--
-- PostgreSQL database dump complete
--

\unrestrict IasfJgk2hhgilCQN7tWa8VI7w52Rr5wmYGyTyGzqPdKRvFBb5Fw3I7quvZLstCj

