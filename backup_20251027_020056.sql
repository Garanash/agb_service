--
-- PostgreSQL database dump
--

\restrict YXsMdNcFIKVyI6H2wgO7gQOl1yvxTlOu7i9dH2APIo3ZgOK0nTZKijiVO5xkcOR

-- Dumped from database version 15.14 (Debian 15.14-1.pgdg13+1)
-- Dumped by pg_dump version 15.14 (Debian 15.14-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: article_mappings; Type: TABLE; Schema: public; Owner: agregator_user
--

CREATE TABLE public.article_mappings (
    id integer NOT NULL,
    contractor_article character varying NOT NULL,
    contractor_description character varying NOT NULL,
    agb_article character varying NOT NULL,
    agb_description character varying NOT NULL,
    confidence double precision,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.article_mappings OWNER TO agregator_user;

--
-- Name: article_mappings_id_seq; Type: SEQUENCE; Schema: public; Owner: agregator_user
--

CREATE SEQUENCE public.article_mappings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.article_mappings_id_seq OWNER TO agregator_user;

--
-- Name: article_mappings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: agregator_user
--

ALTER SEQUENCE public.article_mappings_id_seq OWNED BY public.article_mappings.id;


--
-- Name: contractor_documents; Type: TABLE; Schema: public; Owner: agregator_user
--

CREATE TABLE public.contractor_documents (
    id integer NOT NULL,
    contractor_id integer NOT NULL,
    document_type character varying NOT NULL,
    document_name character varying NOT NULL,
    document_path character varying NOT NULL,
    file_size integer,
    mime_type character varying,
    verification_status character varying NOT NULL,
    verification_notes text,
    verified_by integer,
    verified_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.contractor_documents OWNER TO agregator_user;

--
-- Name: contractor_documents_id_seq; Type: SEQUENCE; Schema: public; Owner: agregator_user
--

CREATE SEQUENCE public.contractor_documents_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.contractor_documents_id_seq OWNER TO agregator_user;

--
-- Name: contractor_documents_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: agregator_user
--

ALTER SEQUENCE public.contractor_documents_id_seq OWNED BY public.contractor_documents.id;


--
-- Name: contractor_education; Type: TABLE; Schema: public; Owner: agregator_user
--

CREATE TABLE public.contractor_education (
    id integer NOT NULL,
    contractor_id integer NOT NULL,
    institution_name character varying NOT NULL,
    degree character varying NOT NULL,
    specialization character varying NOT NULL,
    graduation_year integer,
    diploma_number character varying,
    document_path character varying,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.contractor_education OWNER TO agregator_user;

--
-- Name: contractor_education_id_seq; Type: SEQUENCE; Schema: public; Owner: agregator_user
--

CREATE SEQUENCE public.contractor_education_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.contractor_education_id_seq OWNER TO agregator_user;

--
-- Name: contractor_education_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: agregator_user
--

ALTER SEQUENCE public.contractor_education_id_seq OWNED BY public.contractor_education.id;


--
-- Name: contractor_profiles; Type: TABLE; Schema: public; Owner: agregator_user
--

CREATE TABLE public.contractor_profiles (
    id integer NOT NULL,
    user_id integer NOT NULL,
    last_name character varying,
    first_name character varying,
    patronymic character varying,
    phone character varying,
    email character varying,
    passport_series character varying,
    passport_number character varying,
    passport_issued_by character varying,
    passport_issued_date character varying,
    passport_issued_code character varying,
    birth_date character varying,
    birth_place character varying,
    inn character varying,
    professional_info json,
    bank_name character varying,
    bank_account character varying,
    bank_bik character varying,
    telegram_username character varying,
    website character varying,
    general_description character varying,
    profile_photo_path character varying,
    portfolio_files json,
    document_files json,
    specializations json,
    equipment_brands_experience json,
    certifications json,
    work_regions json,
    hourly_rate double precision,
    availability_status character varying,
    profile_completion_status character varying,
    security_verified boolean,
    manager_verified boolean,
    security_verified_at timestamp with time zone,
    manager_verified_at timestamp with time zone,
    security_verified_by integer,
    manager_verified_by integer,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.contractor_profiles OWNER TO agregator_user;

--
-- Name: contractor_profiles_id_seq; Type: SEQUENCE; Schema: public; Owner: agregator_user
--

CREATE SEQUENCE public.contractor_profiles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.contractor_profiles_id_seq OWNER TO agregator_user;

--
-- Name: contractor_profiles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: agregator_user
--

ALTER SEQUENCE public.contractor_profiles_id_seq OWNED BY public.contractor_profiles.id;


--
-- Name: contractor_request_items; Type: TABLE; Schema: public; Owner: agregator_user
--

CREATE TABLE public.contractor_request_items (
    id integer NOT NULL,
    request_id integer NOT NULL,
    contractor_article character varying NOT NULL,
    contractor_description character varying NOT NULL,
    agb_article character varying,
    agb_description character varying,
    confidence double precision,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.contractor_request_items OWNER TO agregator_user;

--
-- Name: contractor_request_items_id_seq; Type: SEQUENCE; Schema: public; Owner: agregator_user
--

CREATE SEQUENCE public.contractor_request_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.contractor_request_items_id_seq OWNER TO agregator_user;

--
-- Name: contractor_request_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: agregator_user
--

ALTER SEQUENCE public.contractor_request_items_id_seq OWNED BY public.contractor_request_items.id;


--
-- Name: contractor_requests; Type: TABLE; Schema: public; Owner: agregator_user
--

CREATE TABLE public.contractor_requests (
    id integer NOT NULL,
    request_number character varying NOT NULL,
    contractor_name character varying NOT NULL,
    request_date timestamp without time zone NOT NULL,
    status character varying,
    total_items integer,
    matched_items integer,
    created_by integer NOT NULL,
    processed_by integer,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    processed_at timestamp with time zone
);


ALTER TABLE public.contractor_requests OWNER TO agregator_user;

--
-- Name: contractor_requests_id_seq; Type: SEQUENCE; Schema: public; Owner: agregator_user
--

CREATE SEQUENCE public.contractor_requests_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.contractor_requests_id_seq OWNER TO agregator_user;

--
-- Name: contractor_requests_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: agregator_user
--

ALTER SEQUENCE public.contractor_requests_id_seq OWNED BY public.contractor_requests.id;


--
-- Name: contractor_responses; Type: TABLE; Schema: public; Owner: agregator_user
--

CREATE TABLE public.contractor_responses (
    id integer NOT NULL,
    request_id integer NOT NULL,
    contractor_id integer NOT NULL,
    proposed_price integer,
    estimated_time character varying,
    comment character varying,
    is_accepted boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.contractor_responses OWNER TO agregator_user;

--
-- Name: contractor_responses_id_seq; Type: SEQUENCE; Schema: public; Owner: agregator_user
--

CREATE SEQUENCE public.contractor_responses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.contractor_responses_id_seq OWNER TO agregator_user;

--
-- Name: contractor_responses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: agregator_user
--

ALTER SEQUENCE public.contractor_responses_id_seq OWNED BY public.contractor_responses.id;


--
-- Name: contractor_verifications; Type: TABLE; Schema: public; Owner: agregator_user
--

CREATE TABLE public.contractor_verifications (
    id integer NOT NULL,
    contractor_id integer NOT NULL,
    profile_completed boolean,
    documents_uploaded boolean,
    security_check_passed boolean,
    manager_approval boolean,
    overall_status character varying NOT NULL,
    security_notes text,
    manager_notes text,
    security_checked_by integer,
    manager_checked_by integer,
    security_checked_at timestamp with time zone,
    manager_checked_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.contractor_verifications OWNER TO agregator_user;

--
-- Name: contractor_verifications_id_seq; Type: SEQUENCE; Schema: public; Owner: agregator_user
--

CREATE SEQUENCE public.contractor_verifications_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.contractor_verifications_id_seq OWNER TO agregator_user;

--
-- Name: contractor_verifications_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: agregator_user
--

ALTER SEQUENCE public.contractor_verifications_id_seq OWNED BY public.contractor_verifications.id;


--
-- Name: customer_profiles; Type: TABLE; Schema: public; Owner: agregator_user
--

CREATE TABLE public.customer_profiles (
    id integer NOT NULL,
    user_id integer NOT NULL,
    company_name character varying NOT NULL,
    contact_person character varying NOT NULL,
    phone character varying NOT NULL,
    email character varying NOT NULL,
    address character varying,
    inn character varying,
    kpp character varying,
    ogrn character varying,
    equipment_brands json,
    equipment_types json,
    mining_operations json,
    service_history text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.customer_profiles OWNER TO agregator_user;

--
-- Name: customer_profiles_id_seq; Type: SEQUENCE; Schema: public; Owner: agregator_user
--

CREATE SEQUENCE public.customer_profiles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.customer_profiles_id_seq OWNER TO agregator_user;

--
-- Name: customer_profiles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: agregator_user
--

ALTER SEQUENCE public.customer_profiles_id_seq OWNED BY public.customer_profiles.id;


--
-- Name: hr_documents; Type: TABLE; Schema: public; Owner: agregator_user
--

CREATE TABLE public.hr_documents (
    id integer NOT NULL,
    contractor_id integer NOT NULL,
    document_type character varying NOT NULL,
    document_status character varying NOT NULL,
    generated_by integer,
    generated_at timestamp with time zone,
    document_path character varying,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.hr_documents OWNER TO agregator_user;

--
-- Name: hr_documents_id_seq; Type: SEQUENCE; Schema: public; Owner: agregator_user
--

CREATE SEQUENCE public.hr_documents_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.hr_documents_id_seq OWNER TO agregator_user;

--
-- Name: hr_documents_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: agregator_user
--

ALTER SEQUENCE public.hr_documents_id_seq OWNED BY public.hr_documents.id;


--
-- Name: repair_requests; Type: TABLE; Schema: public; Owner: agregator_user
--

CREATE TABLE public.repair_requests (
    id integer NOT NULL,
    customer_id integer NOT NULL,
    title character varying NOT NULL,
    description character varying NOT NULL,
    urgency character varying,
    preferred_date timestamp without time zone,
    address character varying,
    city character varying,
    region character varying,
    latitude double precision,
    longitude double precision,
    equipment_type character varying,
    equipment_brand character varying,
    equipment_model character varying,
    problem_description character varying,
    priority character varying,
    manager_comment character varying,
    clarification_details text,
    estimated_cost integer,
    final_price integer,
    sent_to_bot_at timestamp with time zone,
    scheduled_date timestamp without time zone,
    status character varying,
    service_engineer_id integer,
    assigned_contractor_id integer,
    manager_id integer,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    processed_at timestamp with time zone,
    assigned_at timestamp with time zone
);


ALTER TABLE public.repair_requests OWNER TO agregator_user;

--
-- Name: repair_requests_id_seq; Type: SEQUENCE; Schema: public; Owner: agregator_user
--

CREATE SEQUENCE public.repair_requests_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.repair_requests_id_seq OWNER TO agregator_user;

--
-- Name: repair_requests_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: agregator_user
--

ALTER SEQUENCE public.repair_requests_id_seq OWNED BY public.repair_requests.id;


--
-- Name: security_verifications; Type: TABLE; Schema: public; Owner: agregator_user
--

CREATE TABLE public.security_verifications (
    id integer NOT NULL,
    contractor_id integer NOT NULL,
    verification_status character varying NOT NULL,
    verification_notes text,
    checked_by integer,
    checked_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.security_verifications OWNER TO agregator_user;

--
-- Name: security_verifications_id_seq; Type: SEQUENCE; Schema: public; Owner: agregator_user
--

CREATE SEQUENCE public.security_verifications_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.security_verifications_id_seq OWNER TO agregator_user;

--
-- Name: security_verifications_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: agregator_user
--

ALTER SEQUENCE public.security_verifications_id_seq OWNED BY public.security_verifications.id;


--
-- Name: telegram_messages; Type: TABLE; Schema: public; Owner: agregator_user
--

CREATE TABLE public.telegram_messages (
    id integer NOT NULL,
    telegram_user_id integer NOT NULL,
    message_text text NOT NULL,
    message_type character varying(50) DEFAULT 'text'::character varying,
    is_from_bot boolean DEFAULT false,
    is_read boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.telegram_messages OWNER TO agregator_user;

--
-- Name: telegram_messages_id_seq; Type: SEQUENCE; Schema: public; Owner: agregator_user
--

CREATE SEQUENCE public.telegram_messages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.telegram_messages_id_seq OWNER TO agregator_user;

--
-- Name: telegram_messages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: agregator_user
--

ALTER SEQUENCE public.telegram_messages_id_seq OWNED BY public.telegram_messages.id;


--
-- Name: telegram_users; Type: TABLE; Schema: public; Owner: agregator_user
--

CREATE TABLE public.telegram_users (
    id integer NOT NULL,
    telegram_id bigint NOT NULL,
    user_id integer,
    username character varying,
    first_name character varying,
    last_name character varying,
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.telegram_users OWNER TO agregator_user;

--
-- Name: telegram_users_id_seq; Type: SEQUENCE; Schema: public; Owner: agregator_user
--

CREATE SEQUENCE public.telegram_users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.telegram_users_id_seq OWNER TO agregator_user;

--
-- Name: telegram_users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: agregator_user
--

ALTER SEQUENCE public.telegram_users_id_seq OWNED BY public.telegram_users.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: agregator_user
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying NOT NULL,
    email character varying NOT NULL,
    hashed_password character varying NOT NULL,
    first_name character varying,
    last_name character varying,
    middle_name character varying,
    role character varying,
    is_active boolean,
    is_password_changed boolean,
    email_verified boolean,
    email_verification_token character varying,
    avatar_url character varying,
    phone character varying,
    "position" character varying,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.users OWNER TO agregator_user;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: agregator_user
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO agregator_user;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: agregator_user
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: article_mappings id; Type: DEFAULT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.article_mappings ALTER COLUMN id SET DEFAULT nextval('public.article_mappings_id_seq'::regclass);


--
-- Name: contractor_documents id; Type: DEFAULT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.contractor_documents ALTER COLUMN id SET DEFAULT nextval('public.contractor_documents_id_seq'::regclass);


--
-- Name: contractor_education id; Type: DEFAULT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.contractor_education ALTER COLUMN id SET DEFAULT nextval('public.contractor_education_id_seq'::regclass);


--
-- Name: contractor_profiles id; Type: DEFAULT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.contractor_profiles ALTER COLUMN id SET DEFAULT nextval('public.contractor_profiles_id_seq'::regclass);


--
-- Name: contractor_request_items id; Type: DEFAULT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.contractor_request_items ALTER COLUMN id SET DEFAULT nextval('public.contractor_request_items_id_seq'::regclass);


--
-- Name: contractor_requests id; Type: DEFAULT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.contractor_requests ALTER COLUMN id SET DEFAULT nextval('public.contractor_requests_id_seq'::regclass);


--
-- Name: contractor_responses id; Type: DEFAULT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.contractor_responses ALTER COLUMN id SET DEFAULT nextval('public.contractor_responses_id_seq'::regclass);


--
-- Name: contractor_verifications id; Type: DEFAULT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.contractor_verifications ALTER COLUMN id SET DEFAULT nextval('public.contractor_verifications_id_seq'::regclass);


--
-- Name: customer_profiles id; Type: DEFAULT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.customer_profiles ALTER COLUMN id SET DEFAULT nextval('public.customer_profiles_id_seq'::regclass);


--
-- Name: hr_documents id; Type: DEFAULT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.hr_documents ALTER COLUMN id SET DEFAULT nextval('public.hr_documents_id_seq'::regclass);


--
-- Name: repair_requests id; Type: DEFAULT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.repair_requests ALTER COLUMN id SET DEFAULT nextval('public.repair_requests_id_seq'::regclass);


--
-- Name: security_verifications id; Type: DEFAULT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.security_verifications ALTER COLUMN id SET DEFAULT nextval('public.security_verifications_id_seq'::regclass);


--
-- Name: telegram_messages id; Type: DEFAULT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.telegram_messages ALTER COLUMN id SET DEFAULT nextval('public.telegram_messages_id_seq'::regclass);


--
-- Name: telegram_users id; Type: DEFAULT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.telegram_users ALTER COLUMN id SET DEFAULT nextval('public.telegram_users_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: article_mappings; Type: TABLE DATA; Schema: public; Owner: agregator_user
--

COPY public.article_mappings (id, contractor_article, contractor_description, agb_article, agb_description, confidence, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: contractor_documents; Type: TABLE DATA; Schema: public; Owner: agregator_user
--

COPY public.contractor_documents (id, contractor_id, document_type, document_name, document_path, file_size, mime_type, verification_status, verification_notes, verified_by, verified_at, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: contractor_education; Type: TABLE DATA; Schema: public; Owner: agregator_user
--

COPY public.contractor_education (id, contractor_id, institution_name, degree, specialization, graduation_year, diploma_number, document_path, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: contractor_profiles; Type: TABLE DATA; Schema: public; Owner: agregator_user
--

COPY public.contractor_profiles (id, user_id, last_name, first_name, patronymic, phone, email, passport_series, passport_number, passport_issued_by, passport_issued_date, passport_issued_code, birth_date, birth_place, inn, professional_info, bank_name, bank_account, bank_bik, telegram_username, website, general_description, profile_photo_path, portfolio_files, document_files, specializations, equipment_brands_experience, certifications, work_regions, hourly_rate, availability_status, profile_completion_status, security_verified, manager_verified, security_verified_at, manager_verified_at, security_verified_by, manager_verified_by, created_at, updated_at) FROM stdin;
5	16					test_final@mail.ru	\N	\N	\N	\N	\N	\N	\N	\N	[]	\N	\N	\N		\N	\N	\N	[]	[]	[]	[]	[]	[]	0	available	incomplete	f	f	\N	\N	\N	\N	2025-10-25 20:07:04.152221+00	\N
4	9	Сергеев	Сергей	Михайлович	+7(999)123-45-67	contractor3@test.com	\N	\N	\N	\N	\N	\N	\N	\N	[]	\N	\N	\N	Garanash	\N	\N	\N	[]	[]	["\\u0411\\u0443\\u0440\\u0435\\u043d\\u0438\\u0435", "\\u0420\\u0435\\u043c\\u043e\\u043d\\u0442 \\u043e\\u0431\\u043e\\u0440\\u0443\\u0434\\u043e\\u0432\\u0430\\u043d\\u0438\\u044f"]	["Atlas Copco", "Sandvik"]	["\\u0421\\u0435\\u0440\\u0442\\u0438\\u0444\\u0438\\u043a\\u0430\\u0442 \\u0431\\u0435\\u0437\\u043e\\u043f\\u0430\\u0441\\u043d\\u043e\\u0441\\u0442\\u0438"]	["\\u041c\\u043e\\u0441\\u043a\\u0432\\u0430", "\\u0421\\u0430\\u043d\\u043a\\u0442-\\u041f\\u0435\\u0442\\u0435\\u0440\\u0431\\u0443\\u0440\\u0433"]	1500	available	incomplete	f	f	\N	\N	\N	\N	2025-10-25 20:06:22.536315+00	2025-10-25 23:05:26.534186+00
6	17					nastia04897@mail.ru	\N	\N	\N	\N	\N	\N	\N	\N	[]	\N	\N	\N		\N	\N	\N	[]	[]	[]	[]	[]	[]	0	available	incomplete	f	f	\N	\N	\N	\N	2025-10-26 07:46:36.931111+00	\N
11	22					dolgov_am@mail.ru	\N	\N	\N	\N	\N	\N	\N	\N	[]	\N	\N	\N		\N	\N	\N	[]	[]	[]	[]	[]	[]	0	available	incomplete	f	f	\N	\N	\N	\N	2025-10-26 21:10:12.653602+00	\N
\.


--
-- Data for Name: contractor_request_items; Type: TABLE DATA; Schema: public; Owner: agregator_user
--

COPY public.contractor_request_items (id, request_id, contractor_article, contractor_description, agb_article, agb_description, confidence, created_at) FROM stdin;
\.


--
-- Data for Name: contractor_requests; Type: TABLE DATA; Schema: public; Owner: agregator_user
--

COPY public.contractor_requests (id, request_number, contractor_name, request_date, status, total_items, matched_items, created_by, processed_by, created_at, updated_at, processed_at) FROM stdin;
\.


--
-- Data for Name: contractor_responses; Type: TABLE DATA; Schema: public; Owner: agregator_user
--

COPY public.contractor_responses (id, request_id, contractor_id, proposed_price, estimated_time, comment, is_accepted, created_at, updated_at) FROM stdin;
2	6	4	84852	9 дней	Готов выполнить работу по заявке 'Тестовая заявка - Техническое обслуживание'. Имею опыт работы с данным типом оборудования.	t	2025-10-23 00:14:56.523623+00	\N
3	7	5	189472	11 дней	Готов выполнить работу по заявке 'Тестовая заявка - Аварийный ремонт'. Имею опыт работы с данным типом оборудования.	t	2025-10-24 09:14:56.586828+00	\N
4	9	5	109745	13 дней	Готов выполнить работу по заявке 'Тестовая заявка - Диагностика оборудования'. Имею опыт работы с данным типом оборудования.	t	2025-10-20 10:14:56.676154+00	\N
\.


--
-- Data for Name: contractor_verifications; Type: TABLE DATA; Schema: public; Owner: agregator_user
--

COPY public.contractor_verifications (id, contractor_id, profile_completed, documents_uploaded, security_check_passed, manager_approval, overall_status, security_notes, manager_notes, security_checked_by, manager_checked_by, security_checked_at, manager_checked_at, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: customer_profiles; Type: TABLE DATA; Schema: public; Owner: agregator_user
--

COPY public.customer_profiles (id, user_id, company_name, contact_person, phone, email, address, inn, kpp, ogrn, equipment_brands, equipment_types, mining_operations, service_history, created_at, updated_at) FROM stdin;
1	10	ООО Анна Аннова	Анна Аннова	+7(999)123-45-67	customer1@test.com	г. Москва, ул. Тестовая, д. 1	1234567890	123456789	1234567890123	["Atlas Copco"]	["\\u0411\\u0443\\u0440\\u043e\\u0432\\u044b\\u0435 \\u0443\\u0441\\u0442\\u0430\\u043d\\u043e\\u0432\\u043a\\u0438"]	["\\u041e\\u0442\\u043a\\u0440\\u044b\\u0442\\u044b\\u0435 \\u0440\\u0430\\u0431\\u043e\\u0442\\u044b"]	Работаем с 2020 года	2025-10-25 20:06:22.820108+00	\N
2	11	ООО Мария Марьева	Мария Марьева	+7(999)123-45-67	customer2@test.com	г. Москва, ул. Тестовая, д. 1	1234567890	123456789	1234567890123	["Atlas Copco"]	["\\u0411\\u0443\\u0440\\u043e\\u0432\\u044b\\u0435 \\u0443\\u0441\\u0442\\u0430\\u043d\\u043e\\u0432\\u043a\\u0438"]	["\\u041e\\u0442\\u043a\\u0440\\u044b\\u0442\\u044b\\u0435 \\u0440\\u0430\\u0431\\u043e\\u0442\\u044b"]	Работаем с 2020 года	2025-10-25 20:06:23.143407+00	\N
\.


--
-- Data for Name: hr_documents; Type: TABLE DATA; Schema: public; Owner: agregator_user
--

COPY public.hr_documents (id, contractor_id, document_type, document_status, generated_by, generated_at, document_path, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: repair_requests; Type: TABLE DATA; Schema: public; Owner: agregator_user
--

COPY public.repair_requests (id, customer_id, title, description, urgency, preferred_date, address, city, region, latitude, longitude, equipment_type, equipment_brand, equipment_model, problem_description, priority, manager_comment, clarification_details, estimated_cost, final_price, sent_to_bot_at, scheduled_date, status, service_engineer_id, assigned_contractor_id, manager_id, created_at, updated_at, processed_at, assigned_at) FROM stdin;
5	2	Тестовая заявка - Ремонт буровой установки	Требуется ремонт буровой установки на участке №1. Обнаружены неисправности в гидравлической системе.	high	\N	Участок №1, г. Москва	Москва	Московская область	\N	\N	Буровая установка	\N	\N	\N	high	\N	\N	150000	\N	\N	\N	new	\N	\N	\N	2025-10-03 22:14:56.498391+00	2025-10-23 22:14:56.498418+00	\N	\N
6	1	Тестовая заявка - Техническое обслуживание	Плановое техническое обслуживание оборудования. Замена фильтров, проверка систем.	medium	\N	Склад №2, г. Санкт-Петербург	Санкт-Петербург	Ленинградская область	\N	\N	Оборудование	\N	\N	\N	medium	\N	\N	75000	\N	\N	\N	new	\N	9	\N	2025-10-22 22:14:56.523623+00	2025-10-25 22:14:56.554615+00	\N	2025-10-23 22:14:56.523623+00
7	1	Тестовая заявка - Аварийный ремонт	Срочный ремонт насосного оборудования. Остановка производства.	urgent	\N	Производство №3, г. Екатеринбург	Екатеринбург	Свердловская область	\N	\N	Насосное оборудование	\N	\N	\N	urgent	\N	\N	200000	\N	\N	\N	new	\N	16	\N	2025-10-23 22:14:56.586828+00	2025-10-25 22:14:56.61334+00	2025-10-28 22:14:56.586828+00	2025-10-25 22:14:56.586828+00
8	1	Тестовая заявка - Модернизация системы	Модернизация системы управления. Установка нового программного обеспечения.	low	\N	Цех №4, г. Новосибирск	Новосибирск	Новосибирская область	\N	\N	Система управления	\N	\N	\N	low	\N	\N	300000	\N	\N	\N	new	\N	\N	\N	2025-10-21 22:14:56.659181+00	2025-10-25 22:14:56.6592+00	\N	\N
9	1	Тестовая заявка - Диагностика оборудования	Комплексная диагностика всего оборудования на объекте. Составление отчета.	medium	\N	Объект №5, г. Казань	Казань	Республика Татарстан	\N	\N	Диагностическое оборудование	\N	\N	\N	medium	\N	\N	120000	\N	\N	\N	new	\N	16	\N	2025-10-19 22:14:56.676154+00	2025-10-25 22:14:56.693134+00	\N	2025-10-21 22:14:56.676154+00
\.


--
-- Data for Name: security_verifications; Type: TABLE DATA; Schema: public; Owner: agregator_user
--

COPY public.security_verifications (id, contractor_id, verification_status, verification_notes, checked_by, checked_at, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: telegram_messages; Type: TABLE DATA; Schema: public; Owner: agregator_user
--

COPY public.telegram_messages (id, telegram_user_id, message_text, message_type, is_from_bot, is_read, created_at) FROM stdin;
\.


--
-- Data for Name: telegram_users; Type: TABLE DATA; Schema: public; Owner: agregator_user
--

COPY public.telegram_users (id, telegram_id, user_id, username, first_name, last_name, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: agregator_user
--

COPY public.users (id, username, email, hashed_password, first_name, last_name, middle_name, role, is_active, is_password_changed, email_verified, email_verification_token, avatar_url, phone, "position", created_at, updated_at) FROM stdin;
6	contractor1	contractor1@test.com	$5$rounds=535000$xWJznujSXc4/obGU$/NuDBx0kmr/YeUrxmt.FRXtypUFW.4b2ON3gbDMyb76	Иван	Иванов	\N	contractor	t	f	t	kgHbAF8zeP7QfMmtMPpII-bdIxlO3nHuGHvPSJ9LuK0	\N	\N	\N	2025-10-25 20:02:36.976742+00	\N
8	contractor2	contractor2@test.com	$5$rounds=535000$befjay8WgWGLygjk$.69RHTlGUvlFISlpB.dZDJ1g.GXDl.XG0kNNqOm4Um6	Петр	Петров	\N	contractor	t	f	t	HeV8MoUpV8fMHWWDvol9PvhIkoq4QMkyHzSgKRbS06I	\N	\N	\N	2025-10-25 20:03:22.501317+00	\N
9	contractor3	contractor3@test.com	$5$rounds=535000$i3rFqH8Gebl1r0Lb$Yv0mmJ91scfRh1/Y07soTyR.bmL/xtRnjGZj8W0XtZ7	Сергей	Сергеев	\N	contractor	t	f	t	DiD5IV1zUR1RAT-e-UHcoys45Cvbaf6olFTfwKdl3UY	\N	\N	\N	2025-10-25 20:06:22.225648+00	\N
10	customer1	customer1@test.com	$5$rounds=535000$pDb3/8wPkdB0MDVy$3liXpkFlkpdpZwF5BQ9LOSOgkrAtsgSFA2yZroPCc48	Анна	Аннова	\N	customer	t	f	t	xY4kRyu9A6q3upnYX8ZreD5mmMZLant93LxZuxP15SM	\N	\N	\N	2025-10-25 20:06:22.54868+00	\N
11	customer2	customer2@test.com	$5$rounds=535000$VwBoP1WtPFOPA8yV$nm0sKR23/cyyLhVbXN64He55v/9MsAIOixckSdgX.aC	Мария	Марьева	\N	customer	t	f	t	2EU9JmIhM3PmznkKrEUDrpNLZ_biXZ6TdfgITgSYI9Q	\N	\N	\N	2025-10-25 20:06:22.827869+00	\N
12	security1	security1@test.com	$5$rounds=535000$De65W54cONegAhAY$LESD8fu8w/0U.tboYjr0Hxhi9iMcfYGedOBN8NiELh5	Алексей	Алексеев	\N	security	t	f	t	hfXhbu9Ev1SZWLUnKuDbgybqoIDl_9rjdlvQTqyQiHo	\N	\N	\N	2025-10-25 20:06:23.148468+00	\N
13	hr1	hr1@test.com	$5$rounds=535000$USLTHzHfE6ytHs/8$mti8rkltsn.6inET96YExkm8DVMaps7MxCBUcqCwp27	Елена	Еленова	\N	hr	t	f	t	aaSx2bJCfSQyY2wP478tIUpKWG3vzX4uHL54tIR-DGY	\N	\N	\N	2025-10-25 20:06:23.420558+00	\N
14	manager1	manager1@test.com	$5$rounds=535000$MB05ftxBIqt8cBcC$SCK.o7lflAvTUKUk/0fH6GKyDuAYfFeINu.LwQhVj.B	Дмитрий	Дмитриев	\N	manager	t	f	t	oIFPiTmAAqsxhsIraLbgGj4I00FJyA18dQqfWXWhBq4	\N	\N	\N	2025-10-25 20:06:23.688096+00	\N
16	test_browser_final	test_final@mail.ru	$5$rounds=535000$l4ThQjSh0pZ78H1R$fdx8ST2IukO66AlA0O76Y/VqylEmkUXmRv5NLUnIA3/				contractor	t	f	f	xzQtQvQVrCKRBGKFDBzK9q-0ilYq100qponNf6_Sq8c	\N			2025-10-25 20:07:03.868847+00	\N
1	admin	admin@agb-service.com	$5$rounds=535000$LO9QnobkjfhMapVi$xBWCd/Sn3OvnwpOz39/BikQ6TMvxsWJjPDL83.6.iPB	Администратор	Системы		admin	t	f	t	\N	/uploads/avatars/c36b606c-8391-4f48-9d01-5128a0a8076b_128x128.jpg			2025-10-24 21:27:04.007251+00	2025-10-25 23:17:00.713105+00
17	erek	nastia04897@mail.ru	$5$rounds=535000$CYjcEOwmy6QVctyb$x/hRoytbBz6tm7lXnc3csivwx6La.ZbX5aQkN0vHs04				contractor	t	f	f	EBZji9nzC8DUDk8qs5I8vKRXG65hc0cxJEv-b0ptHrU	\N			2025-10-26 07:46:36.613262+00	\N
22	final_email_test	dolgov_am@mail.ru	$5$rounds=535000$lHsT82GXEAkh4LP9$7tV8iwGo3pNWL.LfIbXv9wzVUkKvlkFM9hHIB5makXA				contractor	t	f	t	\N	\N			2025-10-26 21:10:12.32026+00	2025-10-26 21:15:33.326839+00
\.


--
-- Name: article_mappings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: agregator_user
--

SELECT pg_catalog.setval('public.article_mappings_id_seq', 1, false);


--
-- Name: contractor_documents_id_seq; Type: SEQUENCE SET; Schema: public; Owner: agregator_user
--

SELECT pg_catalog.setval('public.contractor_documents_id_seq', 1, false);


--
-- Name: contractor_education_id_seq; Type: SEQUENCE SET; Schema: public; Owner: agregator_user
--

SELECT pg_catalog.setval('public.contractor_education_id_seq', 1, false);


--
-- Name: contractor_profiles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: agregator_user
--

SELECT pg_catalog.setval('public.contractor_profiles_id_seq', 11, true);


--
-- Name: contractor_request_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: agregator_user
--

SELECT pg_catalog.setval('public.contractor_request_items_id_seq', 1, false);


--
-- Name: contractor_requests_id_seq; Type: SEQUENCE SET; Schema: public; Owner: agregator_user
--

SELECT pg_catalog.setval('public.contractor_requests_id_seq', 1, false);


--
-- Name: contractor_responses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: agregator_user
--

SELECT pg_catalog.setval('public.contractor_responses_id_seq', 4, true);


--
-- Name: contractor_verifications_id_seq; Type: SEQUENCE SET; Schema: public; Owner: agregator_user
--

SELECT pg_catalog.setval('public.contractor_verifications_id_seq', 1, false);


--
-- Name: customer_profiles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: agregator_user
--

SELECT pg_catalog.setval('public.customer_profiles_id_seq', 2, true);


--
-- Name: hr_documents_id_seq; Type: SEQUENCE SET; Schema: public; Owner: agregator_user
--

SELECT pg_catalog.setval('public.hr_documents_id_seq', 1, false);


--
-- Name: repair_requests_id_seq; Type: SEQUENCE SET; Schema: public; Owner: agregator_user
--

SELECT pg_catalog.setval('public.repair_requests_id_seq', 9, true);


--
-- Name: security_verifications_id_seq; Type: SEQUENCE SET; Schema: public; Owner: agregator_user
--

SELECT pg_catalog.setval('public.security_verifications_id_seq', 1, false);


--
-- Name: telegram_messages_id_seq; Type: SEQUENCE SET; Schema: public; Owner: agregator_user
--

SELECT pg_catalog.setval('public.telegram_messages_id_seq', 1, false);


--
-- Name: telegram_users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: agregator_user
--

SELECT pg_catalog.setval('public.telegram_users_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: agregator_user
--

SELECT pg_catalog.setval('public.users_id_seq', 22, true);


--
-- Name: article_mappings article_mappings_pkey; Type: CONSTRAINT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.article_mappings
    ADD CONSTRAINT article_mappings_pkey PRIMARY KEY (id);


--
-- Name: contractor_documents contractor_documents_pkey; Type: CONSTRAINT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.contractor_documents
    ADD CONSTRAINT contractor_documents_pkey PRIMARY KEY (id);


--
-- Name: contractor_education contractor_education_pkey; Type: CONSTRAINT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.contractor_education
    ADD CONSTRAINT contractor_education_pkey PRIMARY KEY (id);


--
-- Name: contractor_profiles contractor_profiles_pkey; Type: CONSTRAINT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.contractor_profiles
    ADD CONSTRAINT contractor_profiles_pkey PRIMARY KEY (id);


--
-- Name: contractor_profiles contractor_profiles_user_id_key; Type: CONSTRAINT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.contractor_profiles
    ADD CONSTRAINT contractor_profiles_user_id_key UNIQUE (user_id);


--
-- Name: contractor_request_items contractor_request_items_pkey; Type: CONSTRAINT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.contractor_request_items
    ADD CONSTRAINT contractor_request_items_pkey PRIMARY KEY (id);


--
-- Name: contractor_requests contractor_requests_pkey; Type: CONSTRAINT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.contractor_requests
    ADD CONSTRAINT contractor_requests_pkey PRIMARY KEY (id);


--
-- Name: contractor_responses contractor_responses_pkey; Type: CONSTRAINT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.contractor_responses
    ADD CONSTRAINT contractor_responses_pkey PRIMARY KEY (id);


--
-- Name: contractor_verifications contractor_verifications_contractor_id_key; Type: CONSTRAINT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.contractor_verifications
    ADD CONSTRAINT contractor_verifications_contractor_id_key UNIQUE (contractor_id);


--
-- Name: contractor_verifications contractor_verifications_pkey; Type: CONSTRAINT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.contractor_verifications
    ADD CONSTRAINT contractor_verifications_pkey PRIMARY KEY (id);


--
-- Name: customer_profiles customer_profiles_pkey; Type: CONSTRAINT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.customer_profiles
    ADD CONSTRAINT customer_profiles_pkey PRIMARY KEY (id);


--
-- Name: customer_profiles customer_profiles_user_id_key; Type: CONSTRAINT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.customer_profiles
    ADD CONSTRAINT customer_profiles_user_id_key UNIQUE (user_id);


--
-- Name: hr_documents hr_documents_pkey; Type: CONSTRAINT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.hr_documents
    ADD CONSTRAINT hr_documents_pkey PRIMARY KEY (id);


--
-- Name: repair_requests repair_requests_pkey; Type: CONSTRAINT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.repair_requests
    ADD CONSTRAINT repair_requests_pkey PRIMARY KEY (id);


--
-- Name: security_verifications security_verifications_pkey; Type: CONSTRAINT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.security_verifications
    ADD CONSTRAINT security_verifications_pkey PRIMARY KEY (id);


--
-- Name: telegram_messages telegram_messages_pkey; Type: CONSTRAINT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.telegram_messages
    ADD CONSTRAINT telegram_messages_pkey PRIMARY KEY (id);


--
-- Name: telegram_users telegram_users_pkey; Type: CONSTRAINT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.telegram_users
    ADD CONSTRAINT telegram_users_pkey PRIMARY KEY (id);


--
-- Name: telegram_users telegram_users_telegram_id_key; Type: CONSTRAINT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.telegram_users
    ADD CONSTRAINT telegram_users_telegram_id_key UNIQUE (telegram_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: idx_telegram_messages_created_at; Type: INDEX; Schema: public; Owner: agregator_user
--

CREATE INDEX idx_telegram_messages_created_at ON public.telegram_messages USING btree (created_at);


--
-- Name: idx_telegram_messages_is_read; Type: INDEX; Schema: public; Owner: agregator_user
--

CREATE INDEX idx_telegram_messages_is_read ON public.telegram_messages USING btree (is_read);


--
-- Name: idx_telegram_messages_telegram_user_id; Type: INDEX; Schema: public; Owner: agregator_user
--

CREATE INDEX idx_telegram_messages_telegram_user_id ON public.telegram_messages USING btree (telegram_user_id);


--
-- Name: ix_article_mappings_agb_article; Type: INDEX; Schema: public; Owner: agregator_user
--

CREATE INDEX ix_article_mappings_agb_article ON public.article_mappings USING btree (agb_article);


--
-- Name: ix_article_mappings_contractor_article; Type: INDEX; Schema: public; Owner: agregator_user
--

CREATE INDEX ix_article_mappings_contractor_article ON public.article_mappings USING btree (contractor_article);


--
-- Name: ix_article_mappings_id; Type: INDEX; Schema: public; Owner: agregator_user
--

CREATE INDEX ix_article_mappings_id ON public.article_mappings USING btree (id);


--
-- Name: ix_contractor_documents_id; Type: INDEX; Schema: public; Owner: agregator_user
--

CREATE INDEX ix_contractor_documents_id ON public.contractor_documents USING btree (id);


--
-- Name: ix_contractor_education_id; Type: INDEX; Schema: public; Owner: agregator_user
--

CREATE INDEX ix_contractor_education_id ON public.contractor_education USING btree (id);


--
-- Name: ix_contractor_profiles_id; Type: INDEX; Schema: public; Owner: agregator_user
--

CREATE INDEX ix_contractor_profiles_id ON public.contractor_profiles USING btree (id);


--
-- Name: ix_contractor_request_items_id; Type: INDEX; Schema: public; Owner: agregator_user
--

CREATE INDEX ix_contractor_request_items_id ON public.contractor_request_items USING btree (id);


--
-- Name: ix_contractor_requests_id; Type: INDEX; Schema: public; Owner: agregator_user
--

CREATE INDEX ix_contractor_requests_id ON public.contractor_requests USING btree (id);


--
-- Name: ix_contractor_requests_request_number; Type: INDEX; Schema: public; Owner: agregator_user
--

CREATE UNIQUE INDEX ix_contractor_requests_request_number ON public.contractor_requests USING btree (request_number);


--
-- Name: ix_contractor_responses_id; Type: INDEX; Schema: public; Owner: agregator_user
--

CREATE INDEX ix_contractor_responses_id ON public.contractor_responses USING btree (id);


--
-- Name: ix_contractor_verifications_id; Type: INDEX; Schema: public; Owner: agregator_user
--

CREATE INDEX ix_contractor_verifications_id ON public.contractor_verifications USING btree (id);


--
-- Name: ix_customer_profiles_id; Type: INDEX; Schema: public; Owner: agregator_user
--

CREATE INDEX ix_customer_profiles_id ON public.customer_profiles USING btree (id);


--
-- Name: ix_hr_documents_id; Type: INDEX; Schema: public; Owner: agregator_user
--

CREATE INDEX ix_hr_documents_id ON public.hr_documents USING btree (id);


--
-- Name: ix_repair_requests_id; Type: INDEX; Schema: public; Owner: agregator_user
--

CREATE INDEX ix_repair_requests_id ON public.repair_requests USING btree (id);


--
-- Name: ix_security_verifications_id; Type: INDEX; Schema: public; Owner: agregator_user
--

CREATE INDEX ix_security_verifications_id ON public.security_verifications USING btree (id);


--
-- Name: ix_telegram_users_id; Type: INDEX; Schema: public; Owner: agregator_user
--

CREATE INDEX ix_telegram_users_id ON public.telegram_users USING btree (id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: agregator_user
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: agregator_user
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: ix_users_username; Type: INDEX; Schema: public; Owner: agregator_user
--

CREATE UNIQUE INDEX ix_users_username ON public.users USING btree (username);


--
-- Name: contractor_documents contractor_documents_contractor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.contractor_documents
    ADD CONSTRAINT contractor_documents_contractor_id_fkey FOREIGN KEY (contractor_id) REFERENCES public.contractor_profiles(id);


--
-- Name: contractor_documents contractor_documents_verified_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.contractor_documents
    ADD CONSTRAINT contractor_documents_verified_by_fkey FOREIGN KEY (verified_by) REFERENCES public.users(id);


--
-- Name: contractor_education contractor_education_contractor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.contractor_education
    ADD CONSTRAINT contractor_education_contractor_id_fkey FOREIGN KEY (contractor_id) REFERENCES public.contractor_profiles(id);


--
-- Name: contractor_profiles contractor_profiles_manager_verified_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.contractor_profiles
    ADD CONSTRAINT contractor_profiles_manager_verified_by_fkey FOREIGN KEY (manager_verified_by) REFERENCES public.users(id);


--
-- Name: contractor_profiles contractor_profiles_security_verified_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.contractor_profiles
    ADD CONSTRAINT contractor_profiles_security_verified_by_fkey FOREIGN KEY (security_verified_by) REFERENCES public.users(id);


--
-- Name: contractor_profiles contractor_profiles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.contractor_profiles
    ADD CONSTRAINT contractor_profiles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: contractor_request_items contractor_request_items_request_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.contractor_request_items
    ADD CONSTRAINT contractor_request_items_request_id_fkey FOREIGN KEY (request_id) REFERENCES public.contractor_requests(id);


--
-- Name: contractor_requests contractor_requests_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.contractor_requests
    ADD CONSTRAINT contractor_requests_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: contractor_requests contractor_requests_processed_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.contractor_requests
    ADD CONSTRAINT contractor_requests_processed_by_fkey FOREIGN KEY (processed_by) REFERENCES public.users(id);


--
-- Name: contractor_responses contractor_responses_contractor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.contractor_responses
    ADD CONSTRAINT contractor_responses_contractor_id_fkey FOREIGN KEY (contractor_id) REFERENCES public.contractor_profiles(id);


--
-- Name: contractor_responses contractor_responses_request_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.contractor_responses
    ADD CONSTRAINT contractor_responses_request_id_fkey FOREIGN KEY (request_id) REFERENCES public.repair_requests(id);


--
-- Name: contractor_verifications contractor_verifications_contractor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.contractor_verifications
    ADD CONSTRAINT contractor_verifications_contractor_id_fkey FOREIGN KEY (contractor_id) REFERENCES public.contractor_profiles(id);


--
-- Name: contractor_verifications contractor_verifications_manager_checked_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.contractor_verifications
    ADD CONSTRAINT contractor_verifications_manager_checked_by_fkey FOREIGN KEY (manager_checked_by) REFERENCES public.users(id);


--
-- Name: contractor_verifications contractor_verifications_security_checked_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.contractor_verifications
    ADD CONSTRAINT contractor_verifications_security_checked_by_fkey FOREIGN KEY (security_checked_by) REFERENCES public.users(id);


--
-- Name: customer_profiles customer_profiles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.customer_profiles
    ADD CONSTRAINT customer_profiles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: hr_documents hr_documents_contractor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.hr_documents
    ADD CONSTRAINT hr_documents_contractor_id_fkey FOREIGN KEY (contractor_id) REFERENCES public.contractor_profiles(id);


--
-- Name: hr_documents hr_documents_generated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.hr_documents
    ADD CONSTRAINT hr_documents_generated_by_fkey FOREIGN KEY (generated_by) REFERENCES public.users(id);


--
-- Name: repair_requests repair_requests_assigned_contractor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.repair_requests
    ADD CONSTRAINT repair_requests_assigned_contractor_id_fkey FOREIGN KEY (assigned_contractor_id) REFERENCES public.users(id);


--
-- Name: repair_requests repair_requests_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.repair_requests
    ADD CONSTRAINT repair_requests_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customer_profiles(id);


--
-- Name: repair_requests repair_requests_manager_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.repair_requests
    ADD CONSTRAINT repair_requests_manager_id_fkey FOREIGN KEY (manager_id) REFERENCES public.users(id);


--
-- Name: repair_requests repair_requests_service_engineer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.repair_requests
    ADD CONSTRAINT repair_requests_service_engineer_id_fkey FOREIGN KEY (service_engineer_id) REFERENCES public.users(id);


--
-- Name: security_verifications security_verifications_checked_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.security_verifications
    ADD CONSTRAINT security_verifications_checked_by_fkey FOREIGN KEY (checked_by) REFERENCES public.users(id);


--
-- Name: security_verifications security_verifications_contractor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.security_verifications
    ADD CONSTRAINT security_verifications_contractor_id_fkey FOREIGN KEY (contractor_id) REFERENCES public.contractor_profiles(id);


--
-- Name: telegram_messages telegram_messages_telegram_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.telegram_messages
    ADD CONSTRAINT telegram_messages_telegram_user_id_fkey FOREIGN KEY (telegram_user_id) REFERENCES public.telegram_users(id);


--
-- Name: telegram_users telegram_users_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agregator_user
--

ALTER TABLE ONLY public.telegram_users
    ADD CONSTRAINT telegram_users_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- PostgreSQL database dump complete
--

\unrestrict YXsMdNcFIKVyI6H2wgO7gQOl1yvxTlOu7i9dH2APIo3ZgOK0nTZKijiVO5xkcOR

