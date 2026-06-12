--
-- PostgreSQL database dump
--

\restrict oMjAS6ar2WZJ6sYi3ptgq8AqfODepklvipbTI52IfaVJscbjyXU9efoFQ79sOfZ

-- Dumped from database version 18.1
-- Dumped by pg_dump version 18.1

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

--
-- Name: update_profile_updated_at(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.update_profile_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: spr_analysis_scope; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_analysis_scope (
    scope_code text NOT NULL,
    name_ru text NOT NULL,
    description_ru text
);


--
-- Name: TABLE spr_analysis_scope; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.spr_analysis_scope IS 'Области применения анализа (здоровье, бизнес и т.д.)';


--
-- Name: spr_bazi_qi_phase; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_bazi_qi_phase (
    id bigint NOT NULL,
    stem_char text NOT NULL,
    branch_char text NOT NULL,
    phase_id bigint NOT NULL,
    phase_name text NOT NULL,
    numeric_score double precision
);


--
-- Name: TABLE spr_bazi_qi_phase; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.spr_bazi_qi_phase IS 'Фазы Ци столпов (месяц/день/час)';


--
-- Name: spr_black_rabbit_day_joey; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_black_rabbit_day_joey (
    first_day_jiazi_id integer NOT NULL,
    lunar_day integer NOT NULL,
    star_name text NOT NULL,
    score double precision NOT NULL
);


--
-- Name: spr_black_rabbit_hour_joey; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_black_rabbit_hour_joey (
    day_stem text NOT NULL,
    hour_branch text NOT NULL,
    star_name text NOT NULL,
    score double precision NOT NULL
);


--
-- Name: spr_black_rabbit_matrix; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_black_rabbit_matrix (
    jiazi_id integer NOT NULL,
    lunar_day integer NOT NULL,
    star_name text
);


--
-- Name: spr_black_rabbit_scores; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_black_rabbit_scores (
    star_name text NOT NULL,
    numeric_score double precision
);


--
-- Name: spr_column_comment; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_column_comment (
    table_name text NOT NULL,
    column_name text NOT NULL,
    comment_text text NOT NULL
);


--
-- Name: TABLE spr_column_comment; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.spr_column_comment IS 'Хранилище комментариев к колонкам (legacy/резерв)';


--
-- Name: spr_day_officer_mapping; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_day_officer_mapping (
    month_branch_id bigint NOT NULL,
    day_branch_id bigint NOT NULL,
    officer_value_id bigint NOT NULL
);


--
-- Name: TABLE spr_day_officer_mapping; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.spr_day_officer_mapping IS 'Маппинг Дневных Офицеров (建除十二直) по ветви месяца + ветви дня';


--
-- Name: spr_earthly_branch; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_earthly_branch (
    branch_id bigint NOT NULL,
    branch_char text NOT NULL,
    branch_pinyin text,
    branch_rus text,
    element text,
    yin_yang text,
    yuan_level bigint,
    start_hour bigint,
    end_hour bigint,
    guigu_score bigint,
    color_hex character varying(7)
);


--
-- Name: TABLE spr_earthly_branch; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.spr_earthly_branch IS 'Справочник 12 Земных Ветвей (地支)';


--
-- Name: COLUMN spr_earthly_branch.branch_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.spr_earthly_branch.branch_id IS 'ID ветви (1-12)';


--
-- Name: COLUMN spr_earthly_branch.branch_char; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.spr_earthly_branch.branch_char IS 'Иероглиф ветви';


--
-- Name: COLUMN spr_earthly_branch.branch_pinyin; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.spr_earthly_branch.branch_pinyin IS 'Пиньинь';


--
-- Name: COLUMN spr_earthly_branch.element; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.spr_earthly_branch.element IS 'Элемент';


--
-- Name: spr_element_display; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_element_display (
    element_id integer NOT NULL,
    element_name_ru text NOT NULL,
    element_name_en text,
    element_char text,
    color_hex text DEFAULT '#000000'::text,
    bg_color_hex text DEFAULT '#ffffff'::text,
    text_color_hex text DEFAULT '#000000'::text,
    display_order integer DEFAULT 0
);


--
-- Name: spr_element_display_element_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.spr_element_display_element_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: spr_element_display_element_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.spr_element_display_element_id_seq OWNED BY public.spr_element_display.element_id;


--
-- Name: spr_flying_star_map; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_flying_star_map (
    center_star integer NOT NULL,
    palace integer NOT NULL,
    resident_star integer
);


--
-- Name: TABLE spr_flying_star_map; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.spr_flying_star_map IS 'Карта Летящих Звёзд: период + направление → звёзды';


--
-- Name: spr_gates; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_gates (
    id bigint NOT NULL,
    name_en text,
    name_ru text
);


--
-- Name: TABLE spr_gates; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.spr_gates IS 'Справочник 8 Врат Ци Мэнь Дуня (八門)';


--
-- Name: spr_gods; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_gods (
    id bigint NOT NULL,
    name_en text,
    name_ru text
);


--
-- Name: TABLE spr_gods; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.spr_gods IS 'Справочник 8 Божеств Ци Мэнь Дуня (八神)';


--
-- Name: spr_heavenly_stem; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_heavenly_stem (
    stem_id bigint NOT NULL,
    stem_char text NOT NULL,
    stem_pinyin text,
    stem_rus text,
    element text,
    yin_yang text,
    guigu_score bigint,
    color_hex character varying(7)
);


--
-- Name: TABLE spr_heavenly_stem; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.spr_heavenly_stem IS 'Справочник 10 Небесных Стволов (天干)';


--
-- Name: COLUMN spr_heavenly_stem.stem_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.spr_heavenly_stem.stem_id IS 'ID ствола (1-10)';


--
-- Name: COLUMN spr_heavenly_stem.stem_char; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.spr_heavenly_stem.stem_char IS 'Иероглиф ствола';


--
-- Name: COLUMN spr_heavenly_stem.stem_pinyin; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.spr_heavenly_stem.stem_pinyin IS 'Пиньинь';


--
-- Name: COLUMN spr_heavenly_stem.element; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.spr_heavenly_stem.element IS 'Элемент (Дерево/Огонь/Земля/Металл/Вода)';


--
-- Name: spr_hour_stars; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_hour_stars (
    day_branch text NOT NULL,
    yin_yang bigint NOT NULL,
    hour_branch text NOT NULL,
    star bigint
);


--
-- Name: TABLE spr_hour_stars; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.spr_hour_stars IS 'Часовые звёзды для Фэн Шуй';


--
-- Name: spr_indicator; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_indicator (
    indicator_id bigint NOT NULL,
    code text NOT NULL,
    name_ru text NOT NULL,
    description_ru text,
    level text NOT NULL,
    value_type text NOT NULL,
    is_active bigint NOT NULL
);


--
-- Name: TABLE spr_indicator; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.spr_indicator IS 'Справочник индикаторов анализа (группировка правил)';


--
-- Name: spr_indicator_scope; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_indicator_scope (
    indicator_id bigint NOT NULL,
    scope_code text NOT NULL
);


--
-- Name: TABLE spr_indicator_scope; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.spr_indicator_scope IS 'Связь индикаторов с областями применения';


--
-- Name: spr_indicator_value; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_indicator_value (
    value_id bigint NOT NULL,
    indicator_id bigint NOT NULL,
    code text NOT NULL,
    name_ru text NOT NULL,
    description_ru text,
    favorable_actions text,
    unfavorable_actions text,
    interpretation_ru text,
    numeric_score double precision NOT NULL
);


--
-- Name: TABLE spr_indicator_value; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.spr_indicator_value IS 'Значения индикаторов с числовым score';


--
-- Name: spr_jiazi_extended; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_jiazi_extended (
    jiazi_id integer NOT NULL,
    stem text,
    branch text,
    nayin_element text,
    nayin_name text,
    dagua_element integer,
    dagua_period integer,
    dagua_role text,
    upper_ju_yang integer,
    middle_ju_yang integer,
    lower_ju_yang integer,
    upper_ju_yin integer,
    middle_ju_yin integer,
    lower_ju_yin integer
);


--
-- Name: spr_leader_stems; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_leader_stems (
    idx bigint NOT NULL,
    stem text
);


--
-- Name: TABLE spr_leader_stems; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.spr_leader_stems IS 'Ведущие стволы для определения часового/месячного столпа';


--
-- Name: spr_master_dano_mapping; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_master_dano_mapping (
    month_branch_id bigint NOT NULL,
    day_stem_id bigint NOT NULL,
    day_branch_id bigint NOT NULL,
    indicator_value_id bigint NOT NULL
);


--
-- Name: TABLE spr_master_dano_mapping; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.spr_master_dano_mapping IS 'Маппинг Мастера Дун Гуна по ветви месяца + стволу/ветви дня';


--
-- Name: spr_month_stars; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_month_stars (
    year_branch text NOT NULL,
    month_branch text NOT NULL,
    star bigint
);


--
-- Name: TABLE spr_month_stars; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.spr_month_stars IS 'Месячные звёзды для Фэн Шуй';


--
-- Name: spr_pillar_cycle; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_pillar_cycle (
    cycle_index bigint NOT NULL,
    stem_id bigint NOT NULL,
    branch_id bigint NOT NULL
);


--
-- Name: TABLE spr_pillar_cycle; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.spr_pillar_cycle IS 'Справочник столпов (год/месяц/день) для цикла Цзя-Цзы';


--
-- Name: spr_pillar_hour_rule; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_pillar_hour_rule (
    day_stem_id bigint NOT NULL,
    hour_branch_id bigint NOT NULL,
    hour_stem_id bigint NOT NULL
);


--
-- Name: TABLE spr_pillar_hour_rule; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.spr_pillar_hour_rule IS 'Правила вычисления часового столпа из дневного ствола';


--
-- Name: spr_pillar_month_rule; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_pillar_month_rule (
    year_stem_id bigint NOT NULL,
    month_index bigint NOT NULL,
    month_stem_id bigint NOT NULL
);


--
-- Name: TABLE spr_pillar_month_rule; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.spr_pillar_month_rule IS 'Правила вычисления месячного столпа из годового ствола';


--
-- Name: spr_qimen_templates; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_qimen_templates (
    template_id text NOT NULL,
    rasklad_id text,
    yin_yang text,
    ju_num bigint,
    hour_stem_branch text,
    palace_no bigint,
    structure text,
    heaven_stem text,
    is_fou_tou_heaven bigint,
    earth_stem text,
    is_fou_tou_earth bigint,
    star text,
    is_main_star bigint,
    gate text,
    is_main_gate bigint,
    spirit text
);


--
-- Name: TABLE spr_qimen_templates; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.spr_qimen_templates IS 'Шаблоны раскладов Ци Мэнь (базовые конфигурации)';


--
-- Name: spr_scdg; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_scdg (
    id integer NOT NULL,
    jiazi_id integer,
    stem text,
    branch text,
    family_name text,
    parent_child text,
    family_role text,
    element_name text,
    element_glyph text,
    stem_element text,
    branch_animal text,
    element_num integer,
    period_num integer,
    hexagram_num integer,
    hexagram_name text,
    degrees_from numeric,
    degrees_to numeric,
    direction text,
    outer_gua_1 integer,
    outer_gua_2 integer,
    outer_gua_3 integer,
    score_1 integer,
    score_2 integer,
    score_3 integer,
    score_4 integer,
    score_5 integer,
    score_6 integer
);


--
-- Name: spr_scdg_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.spr_scdg_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: spr_scdg_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.spr_scdg_id_seq OWNED BY public.spr_scdg.id;


--
-- Name: spr_skdg_hexagram_pairs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_skdg_hexagram_pairs (
    jiazi_id_a integer NOT NULL,
    pillar_a text NOT NULL,
    el_a integer NOT NULL,
    per_a integer NOT NULL,
    jiazi_id_b integer NOT NULL,
    pillar_b text NOT NULL,
    el_b integer NOT NULL,
    per_b integer NOT NULL,
    is_hetu_el_per boolean DEFAULT false,
    is_c10_el_per boolean DEFAULT false,
    is_same_element boolean DEFAULT false,
    is_same_period boolean DEFAULT false
);


--
-- Name: TABLE spr_skdg_hexagram_pairs; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.spr_skdg_hexagram_pairs IS 'СКДГ: пары гексаграмм по комбинациям Хэ Ту, Комб.10, одинаковый элемент/период';


--
-- Name: spr_skdg_wuxing_relation; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_skdg_wuxing_relation (
    group_a integer NOT NULL,
    group_b integer NOT NULL,
    group_a_name text NOT NULL,
    group_b_name text NOT NULL,
    relation text NOT NULL,
    relation_ru text NOT NULL
);


--
-- Name: TABLE spr_skdg_wuxing_relation; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.spr_skdg_wuxing_relation IS 'СКДГ: отношения У-Син между группами элементов Хэ Ту (1=Вода,2=Огонь,3=Дерево,4=Металл)';


--
-- Name: spr_solar_term; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_solar_term (
    solar_term_id bigint NOT NULL,
    solar_term_char text NOT NULL,
    solar_term_name_ru text,
    solar_term_pinyin text,
    longitude_deg bigint NOT NULL,
    month_branch_id bigint NOT NULL,
    upper_ju bigint,
    middle_ju bigint,
    lower_ju bigint
);


--
-- Name: TABLE spr_solar_term; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.spr_solar_term IS 'Справочник 24 солнечных терминов (節氣)';


--
-- Name: spr_stars; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_stars (
    id bigint NOT NULL,
    name_en text,
    name_ru text
);


--
-- Name: TABLE spr_stars; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.spr_stars IS 'Справочник 9 Звёзд Ци Мэнь Дуня (九星)';


--
-- Name: spr_table_comment; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_table_comment (
    table_name text NOT NULL,
    comment_text text NOT NULL
);


--
-- Name: TABLE spr_table_comment; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.spr_table_comment IS 'Хранилище комментариев к таблицам (legacy/резерв)';


--
-- Name: spr_taiyi_gate_seq; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_taiyi_gate_seq (
    cycle_type text NOT NULL,
    seq_idx integer NOT NULL,
    palace_id integer
);


--
-- Name: spr_taiyi_gates; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_taiyi_gates (
    id integer NOT NULL,
    code text,
    name_cn text,
    name_ru text,
    lucky_score integer
);


--
-- Name: spr_taiyi_jianchu; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_taiyi_jianchu (
    id integer NOT NULL,
    char_cn text NOT NULL,
    name_ru text NOT NULL,
    description text,
    score integer NOT NULL
);


--
-- Name: TABLE spr_taiyi_jianchu; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.spr_taiyi_jianchu IS 'Справочник 12 созвездий 建除十二神 с score';


--
-- Name: spr_taiyi_kong_wang; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_taiyi_kong_wang (
    day_stem_id integer NOT NULL,
    hour_branch_id integer NOT NULL
);


--
-- Name: spr_taiyi_noble; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_taiyi_noble (
    day_stem_id integer NOT NULL,
    hour_branch_id integer NOT NULL
);


--
-- Name: spr_taiyi_palace_ring; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_taiyi_palace_ring (
    palace_id integer NOT NULL,
    ring_idx integer
);


--
-- Name: spr_taiyi_qing_long_start; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_taiyi_qing_long_start (
    day_branch_id integer NOT NULL,
    start_hour_idx integer
);


--
-- Name: spr_taiyi_spirits; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_taiyi_spirits (
    id integer NOT NULL,
    code text,
    name_cn text,
    name_ru text,
    lucky_score integer
);


--
-- Name: spr_taiyi_star_start; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_taiyi_star_start (
    cycle_type text NOT NULL,
    decade_idx integer NOT NULL,
    start_palace integer
);


--
-- Name: spr_taiyi_stars; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_taiyi_stars (
    id integer NOT NULL,
    code text,
    name_cn text,
    name_ru text,
    lucky_score integer
);


--
-- Name: spr_taiyi_xi_shen; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_taiyi_xi_shen (
    day_stem_id integer NOT NULL,
    palace_id integer
);


--
-- Name: spr_tongshu_black_rabbit_rating; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_tongshu_black_rabbit_rating (
    star_name text NOT NULL,
    rating_code text NOT NULL,
    rating_name text NOT NULL,
    description_ru text
);


--
-- Name: TABLE spr_tongshu_black_rabbit_rating; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.spr_tongshu_black_rabbit_rating IS 'Оценки звёзд Чёрного Кролика по Тун Шу';


--
-- Name: spr_tongshu_black_rabbit_star; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_tongshu_black_rabbit_star (
    cycle_index integer NOT NULL,
    lunar_day integer NOT NULL,
    method_code text DEFAULT 'primary'::text NOT NULL,
    star_name text NOT NULL,
    description_ru text,
    nature character varying(20),
    color_hex character varying(7)
);


--
-- Name: TABLE spr_tongshu_black_rabbit_star; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.spr_tongshu_black_rabbit_star IS 'Звёзды Чёрного Кролика по Тун Шу';


--
-- Name: spr_tongshu_branch_combo_rule; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_tongshu_branch_combo_rule (
    rule_id bigint NOT NULL,
    combo_name text NOT NULL,
    combo_type_id bigint NOT NULL,
    numeric_score double precision NOT NULL,
    item1 text NOT NULL,
    item2 text NOT NULL,
    item3 text,
    description text
);


--
-- Name: TABLE spr_tongshu_branch_combo_rule; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.spr_tongshu_branch_combo_rule IS 'Правила комбинаций Земных Ветвей (三合/六合/刑/冲/害/破)';


--
-- Name: spr_tongshu_guigu_outcome; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_tongshu_guigu_outcome (
    outcome_number bigint NOT NULL,
    name_ru text NOT NULL,
    verdict_code text NOT NULL,
    description_ru text,
    numeric_score double precision
);


--
-- Name: TABLE spr_tongshu_guigu_outcome; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.spr_tongshu_guigu_outcome IS 'Результаты Гуй Гу Шу (鬼谷數)';


--
-- Name: spr_tongshu_jiazi_profile; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_tongshu_jiazi_profile (
    cycle_index bigint NOT NULL,
    pillar_text text NOT NULL,
    nayin_name text,
    nayin_element text,
    nayin_code text,
    dagua_element bigint,
    dagua_period bigint,
    family_code text,
    family_role text
);


--
-- Name: TABLE spr_tongshu_jiazi_profile; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.spr_tongshu_jiazi_profile IS 'Профили 60 Цзя-Цзы по Тун Шу';


--
-- Name: spr_tongshu_phase; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_tongshu_phase (
    phase_id bigint NOT NULL,
    name_ru text NOT NULL,
    numeric_score double precision NOT NULL
);


--
-- Name: TABLE spr_tongshu_phase; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.spr_tongshu_phase IS 'Фазы Ци (氣) по Тун Шу';


--
-- Name: spr_tongshu_phase_mapping; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_tongshu_phase_mapping (
    day_stem text NOT NULL,
    phase_id bigint NOT NULL,
    reference_branch text NOT NULL
);


--
-- Name: TABLE spr_tongshu_phase_mapping; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.spr_tongshu_phase_mapping IS 'Маппинг фаз Ци по столпам';


--
-- Name: spr_tongshu_shensha_rule; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_tongshu_shensha_rule (
    rule_id bigint NOT NULL,
    star_name text NOT NULL,
    master_scope text NOT NULL,
    master_value text NOT NULL,
    target_scope text NOT NULL,
    target_value text NOT NULL,
    notes text,
    source character varying(50) DEFAULT 'classical'::character varying
);


--
-- Name: TABLE spr_tongshu_shensha_rule; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.spr_tongshu_shensha_rule IS 'Правила Шэнь Ша (神煞) — духи и демоны';


--
-- Name: spr_tongshu_stem_combo_rule; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_tongshu_stem_combo_rule (
    rule_id bigint NOT NULL,
    combo_name text NOT NULL,
    combo_type_id bigint NOT NULL,
    numeric_score double precision NOT NULL,
    item1 text NOT NULL,
    item2 text NOT NULL,
    description text
);


--
-- Name: TABLE spr_tongshu_stem_combo_rule; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.spr_tongshu_stem_combo_rule IS 'Правила комбинаций Небесных Стволов (合/冲)';


--
-- Name: spr_tongshu_ten_god; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_tongshu_ten_god (
    day_stem text NOT NULL,
    god_code text NOT NULL,
    related_stem text NOT NULL
);


--
-- Name: TABLE spr_tongshu_ten_god; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.spr_tongshu_ten_god IS 'Справочник 10 Богов (十神)';


--
-- Name: spr_yanqin_day_constellation; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_yanqin_day_constellation (
    dow integer NOT NULL,
    branch_group integer NOT NULL,
    constellation_char text NOT NULL,
    constellation_name text NOT NULL,
    star_element text NOT NULL,
    score double precision NOT NULL
);


--
-- Name: TABLE spr_yanqin_day_constellation; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.spr_yanqin_day_constellation IS 'Справочник 28 созвездий 演禽 по дню недели + группе ветвей';


--
-- Name: spr_yellow_black_matrix; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_yellow_black_matrix (
    month_branch text NOT NULL,
    day_branch text NOT NULL,
    star_id bigint
);


--
-- Name: TABLE spr_yellow_black_matrix; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.spr_yellow_black_matrix IS 'Матрица Жёлтого/Чёрного пути: ветвь месяца + ветвь дня → ID звезды';


--
-- Name: spr_yellow_black_stars; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spr_yellow_black_stars (
    id bigint NOT NULL,
    name text,
    score double precision
);


--
-- Name: TABLE spr_yellow_black_stars; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.spr_yellow_black_stars IS 'Звёзды Жёлтого/Чёрного пути с оценкой (+1/-1)';


--
-- Name: t_analysis_date; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.t_analysis_date (
    hour_id text NOT NULL,
    rule_id text NOT NULL,
    result_value text,
    score double precision
);


--
-- Name: TABLE t_analysis_date; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.t_analysis_date IS 'Дополнительные данные анализа по датам';


--
-- Name: t_analysis_day; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.t_analysis_day (
    date_val date NOT NULL,
    year_pillar text NOT NULL,
    month_pillar text NOT NULL,
    day_pillar text NOT NULL,
    rule_id text NOT NULL,
    result_value text NOT NULL,
    score double precision
)
WITH (autovacuum_enabled='true');


--
-- Name: TABLE t_analysis_day; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.t_analysis_day IS 'Результаты анализа дневного уровня (~365 расчётов/год/правило)';


--
-- Name: COLUMN t_analysis_day.date_val; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.t_analysis_day.date_val IS 'Дата';


--
-- Name: COLUMN t_analysis_day.year_pillar; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.t_analysis_day.year_pillar IS 'Столп года';


--
-- Name: COLUMN t_analysis_day.month_pillar; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.t_analysis_day.month_pillar IS 'Столп месяца';


--
-- Name: COLUMN t_analysis_day.day_pillar; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.t_analysis_day.day_pillar IS 'Столп дня';


--
-- Name: COLUMN t_analysis_day.rule_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.t_analysis_day.rule_id IS 'ID правила (FK t_rule_registry)';


--
-- Name: COLUMN t_analysis_day.result_value; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.t_analysis_day.result_value IS 'Текстовый результат правила';


--
-- Name: COLUMN t_analysis_day.score; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.t_analysis_day.score IS 'Числовой score правила';


--
-- Name: t_analysis_direction; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.t_analysis_direction (
    hour_id text NOT NULL,
    palace_no bigint NOT NULL,
    system_type text NOT NULL,
    chart_level text NOT NULL,
    rule_id text NOT NULL,
    result_value text,
    score double precision
)
WITH (autovacuum_enabled='true');


--
-- Name: TABLE t_analysis_direction; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.t_analysis_direction IS 'Базовая таблица анализа направлений';


--
-- Name: t_analysis_direction_day; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.t_analysis_direction_day (
    date_val date NOT NULL,
    year_pillar text NOT NULL,
    month_pillar text NOT NULL,
    day_pillar text NOT NULL,
    palace_no integer NOT NULL,
    system_type text NOT NULL,
    rule_id text NOT NULL,
    result_value text,
    score double precision
)
WITH (autovacuum_enabled='true');


--
-- Name: TABLE t_analysis_direction_day; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.t_analysis_direction_day IS 'Анализ направлений: дневной уровень (Ци Мэнь)';


--
-- Name: t_analysis_direction_hour; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.t_analysis_direction_hour (
    hour_id text NOT NULL,
    year_pillar text,
    month_pillar text,
    day_pillar text,
    hour_pillar text,
    palace_no integer NOT NULL,
    system_type text NOT NULL,
    rule_id text NOT NULL,
    result_value text,
    score double precision
)
WITH (autovacuum_enabled='true');


--
-- Name: TABLE t_analysis_direction_hour; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.t_analysis_direction_hour IS 'Анализ направлений: часовой уровень (Ци Мэнь)';


--
-- Name: t_analysis_direction_month; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.t_analysis_direction_month (
    year integer NOT NULL,
    month integer NOT NULL,
    year_pillar text NOT NULL,
    month_pillar text NOT NULL,
    palace_no integer NOT NULL,
    system_type text NOT NULL,
    rule_id text NOT NULL,
    result_value text,
    score double precision
)
WITH (autovacuum_enabled='true');


--
-- Name: TABLE t_analysis_direction_month; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.t_analysis_direction_month IS 'Анализ направлений: месячный уровень';


--
-- Name: t_analysis_direction_year; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.t_analysis_direction_year (
    year integer NOT NULL,
    year_pillar text NOT NULL,
    palace_no integer NOT NULL,
    system_type text NOT NULL,
    rule_id text NOT NULL,
    result_value text,
    score double precision
)
WITH (autovacuum_enabled='true');


--
-- Name: TABLE t_analysis_direction_year; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.t_analysis_direction_year IS 'Анализ направлений: годовой уровень';


--
-- Name: t_analysis_hour; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.t_analysis_hour (
    hour_id text NOT NULL,
    year_pillar text,
    month_pillar text,
    day_pillar text,
    hour_pillar text,
    rule_id text NOT NULL,
    result_value text,
    score double precision
)
WITH (autovacuum_enabled='true');


--
-- Name: TABLE t_analysis_hour; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.t_analysis_hour IS 'Результаты анализа часового уровня (~8760 расчётов/год/правило)';


--
-- Name: COLUMN t_analysis_hour.hour_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.t_analysis_hour.hour_id IS 'ID часового слота (FK t_bazi_hourly)';


--
-- Name: COLUMN t_analysis_hour.year_pillar; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.t_analysis_hour.year_pillar IS 'Столп года';


--
-- Name: COLUMN t_analysis_hour.month_pillar; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.t_analysis_hour.month_pillar IS 'Столп месяца';


--
-- Name: COLUMN t_analysis_hour.day_pillar; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.t_analysis_hour.day_pillar IS 'Столп дня';


--
-- Name: COLUMN t_analysis_hour.hour_pillar; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.t_analysis_hour.hour_pillar IS 'Столп часа';


--
-- Name: COLUMN t_analysis_hour.rule_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.t_analysis_hour.rule_id IS 'ID правила (FK t_rule_registry)';


--
-- Name: COLUMN t_analysis_hour.result_value; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.t_analysis_hour.result_value IS 'Текстовый результат';


--
-- Name: COLUMN t_analysis_hour.score; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.t_analysis_hour.score IS 'Числовой score';


--
-- Name: t_analysis_month; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.t_analysis_month (
    year integer NOT NULL,
    month integer NOT NULL,
    year_pillar text NOT NULL,
    month_pillar text NOT NULL,
    rule_id text NOT NULL,
    result_value text NOT NULL,
    score double precision
)
WITH (autovacuum_enabled='true');


--
-- Name: TABLE t_analysis_month; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.t_analysis_month IS 'Результаты анализа месячного уровня (12 расчётов/год/правило)';


--
-- Name: t_analysis_year; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.t_analysis_year (
    year integer NOT NULL,
    year_pillar text NOT NULL,
    rule_id text NOT NULL,
    result_value text NOT NULL,
    score double precision
)
WITH (autovacuum_enabled='true');


--
-- Name: TABLE t_analysis_year; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.t_analysis_year IS 'Результаты анализа годового уровня (1 расчёт/год/правило)';


--
-- Name: t_bazi_hourly; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.t_bazi_hourly (
    hour_id text NOT NULL,
    tz_offset_hours integer NOT NULL,
    slot_start_date_utc text NOT NULL,
    slot_start_time_utc text NOT NULL,
    slot_end_date_utc text,
    slot_end_time_utc text,
    slot_start_date_local text,
    slot_start_time_local text,
    slot_end_date_local text,
    slot_end_time_local text,
    weekday_local text,
    solar_term_id integer,
    year_pillar text,
    month_pillar text,
    day_pillar text,
    hour_pillar text,
    year_stem text,
    year_branch text,
    month_stem text,
    month_branch text,
    day_stem text,
    day_branch text,
    hour_stem text,
    hour_branch text,
    lunar_month integer,
    lunar_day integer,
    lunar_is_leap integer,
    lunar_month_zi integer,
    lunar_day_zi integer,
    lunar_is_leap_zi integer,
    year_int integer
);


--
-- Name: t_control_t_bazi_hourly; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.t_control_t_bazi_hourly (
    hour_id text,
    tz_offset_hours integer,
    slot_start_date_utc text,
    slot_start_time_utc text,
    slot_end_date_utc text,
    slot_end_time_utc text,
    slot_start_date_local text,
    slot_start_time_local text,
    slot_end_date_local text,
    slot_end_time_local text,
    weekday_local text,
    solar_term_id integer,
    solar_term_name text,
    year_pillar text,
    month_pillar text,
    day_pillar text,
    hour_pillar text,
    year_stem text,
    year_branch text,
    month_stem text,
    month_branch text,
    day_stem text,
    day_branch text,
    hour_stem text,
    hour_branch text,
    lunar_month integer,
    lunar_day integer,
    lunar_is_leap integer,
    lunar_month_zi integer,
    lunar_day_zi integer,
    lunar_is_leap_zi integer,
    day_officer_value_id integer
);


--
-- Name: TABLE t_control_t_bazi_hourly; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.t_control_t_bazi_hourly IS 'Контрольные данные для верификации t_bazi_hourly';


--
-- Name: t_control_t_flying_stars; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.t_control_t_flying_stars (
    hour_id text,
    palace integer,
    year_star integer,
    month_star integer,
    day_star integer,
    hour_star integer
);


--
-- Name: TABLE t_control_t_flying_stars; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.t_control_t_flying_stars IS 'Контрольные данные для верификации t_flying_stars';


--
-- Name: t_control_t_qumen_chauby_hourly; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.t_control_t_qumen_chauby_hourly (
    chart_id text,
    hour_id text,
    rasklad_id text,
    palace_no integer,
    chart_type text
);


--
-- Name: TABLE t_control_t_qumen_chauby_hourly; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.t_control_t_qumen_chauby_hourly IS 'Контрольные данные для Ци Мэнь Чай Бу (часовой)';


--
-- Name: t_control_t_qumen_dgiren_day; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.t_control_t_qumen_dgiren_day (
    chart_id text,
    year_pillar text,
    month_pillar text,
    day_pillar text,
    rasklad_id text,
    palace_no integer,
    chart_type text
);


--
-- Name: TABLE t_control_t_qumen_dgiren_day; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.t_control_t_qumen_dgiren_day IS 'Контрольные данные для Ци Мэнь Чжи Жэнь (дневной)';


--
-- Name: t_control_t_qumen_dgiren_hourly; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.t_control_t_qumen_dgiren_hourly (
    chart_id text,
    hour_id text,
    rasklad_id text,
    palace_no integer,
    chart_type text
);


--
-- Name: TABLE t_control_t_qumen_dgiren_hourly; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.t_control_t_qumen_dgiren_hourly IS 'Контрольные данные для Ци Мэнь Чжи Жэнь (часовой)';


--
-- Name: t_control_t_qumen_dgiren_month; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.t_control_t_qumen_dgiren_month (
    chart_id text,
    year_pillar text,
    month_pillar text,
    rasklad_id text,
    palace_no integer,
    chart_type text
);


--
-- Name: TABLE t_control_t_qumen_dgiren_month; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.t_control_t_qumen_dgiren_month IS 'Контрольные данные для Ци Мэнь Чжи Жэнь (месячный)';


--
-- Name: t_control_t_qumen_dgiren_year; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.t_control_t_qumen_dgiren_year (
    chart_id text,
    year_pillar text,
    rasklad_id text,
    palace_no integer,
    chart_type text
);


--
-- Name: TABLE t_control_t_qumen_dgiren_year; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.t_control_t_qumen_dgiren_year IS 'Контрольные данные для Ци Мэнь Чжи Жэнь (годовой)';


--
-- Name: t_crm_calculation; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.t_crm_calculation (
    id integer NOT NULL,
    client_id integer NOT NULL,
    calculation_type character varying(50) NOT NULL,
    reference_id character varying(255) NOT NULL,
    notes text,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: t_crm_calculation_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.t_crm_calculation_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: t_crm_calculation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.t_crm_calculation_id_seq OWNED BY public.t_crm_calculation.id;


--
-- Name: t_crm_client; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.t_crm_client (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    email character varying(255),
    phone character varying(50),
    birth_date date,
    birth_time character varying(10),
    notes text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


--
-- Name: t_crm_client_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.t_crm_client_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: t_crm_client_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.t_crm_client_id_seq OWNED BY public.t_crm_client.id;


--
-- Name: t_crm_note; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.t_crm_note (
    id integer NOT NULL,
    client_id integer NOT NULL,
    note_text text NOT NULL,
    calculation_id character varying(255),
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: t_crm_note_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.t_crm_note_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: t_crm_note_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.t_crm_note_id_seq OWNED BY public.t_crm_note.id;


--
-- Name: t_crm_session; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.t_crm_session (
    id integer NOT NULL,
    client_id integer NOT NULL,
    date date NOT NULL,
    notes text,
    summary text,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: t_crm_session_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.t_crm_session_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: t_crm_session_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.t_crm_session_id_seq OWNED BY public.t_crm_session.id;


--
-- Name: t_event; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.t_event (
    id text NOT NULL,
    dt_start timestamp without time zone NOT NULL,
    dt_end timestamp without time zone NOT NULL,
    calendar text NOT NULL,
    title text NOT NULL,
    comment text
);


--
-- Name: t_flying_stars; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.t_flying_stars (
    hour_id text NOT NULL,
    palace integer NOT NULL,
    year_star integer,
    month_star integer,
    day_star integer,
    hour_star integer
);


--
-- Name: t_profile; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.t_profile (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    birth_date date NOT NULL,
    birth_time time without time zone,
    birth_city character varying(255),
    birth_city_lat numeric(10,7),
    birth_city_lon numeric(10,7),
    birth_timezone character varying(50),
    notes text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: TABLE t_profile; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.t_profile IS 'Профили пользователей для персонализированных расчетов';


--
-- Name: COLUMN t_profile.name; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.t_profile.name IS 'Имя человека';


--
-- Name: COLUMN t_profile.birth_date; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.t_profile.birth_date IS 'Дата рождения';


--
-- Name: COLUMN t_profile.birth_time; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.t_profile.birth_time IS 'Время рождения';


--
-- Name: COLUMN t_profile.birth_city; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.t_profile.birth_city IS 'Город рождения';


--
-- Name: COLUMN t_profile.birth_city_lat; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.t_profile.birth_city_lat IS 'Широта города рождения';


--
-- Name: COLUMN t_profile.birth_city_lon; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.t_profile.birth_city_lon IS 'Долгота города рождения';


--
-- Name: COLUMN t_profile.birth_timezone; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.t_profile.birth_timezone IS 'Часовой пояс (IANA)';


--
-- Name: COLUMN t_profile.notes; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.t_profile.notes IS 'Заметки';


--
-- Name: t_profile_birth_chart; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.t_profile_birth_chart (
    id integer NOT NULL,
    profile_id integer NOT NULL,
    year_pillar character varying(10),
    month_pillar character varying(10),
    day_pillar character varying(10),
    hour_pillar character varying(10),
    day_master character varying(10),
    day_master_element character varying(20),
    calculated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: TABLE t_profile_birth_chart; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.t_profile_birth_chart IS 'Рассчитанные карты рождения (8 столпов)';


--
-- Name: t_profile_birth_chart_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.t_profile_birth_chart_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: t_profile_birth_chart_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.t_profile_birth_chart_id_seq OWNED BY public.t_profile_birth_chart.id;


--
-- Name: t_profile_history; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.t_profile_history (
    id integer NOT NULL,
    profile_id integer NOT NULL,
    action_type character varying(50) NOT NULL,
    module character varying(50),
    reference_date date,
    notes text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: TABLE t_profile_history; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.t_profile_history IS 'История обращений к профилю';


--
-- Name: t_profile_history_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.t_profile_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: t_profile_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.t_profile_history_id_seq OWNED BY public.t_profile_history.id;


--
-- Name: t_profile_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.t_profile_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: t_profile_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.t_profile_id_seq OWNED BY public.t_profile.id;


--
-- Name: t_qumen_chauby_hourly; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.t_qumen_chauby_hourly (
    chart_id text NOT NULL,
    hour_id text NOT NULL,
    rasklad_id text,
    palace_no integer,
    chart_type text
);


--
-- Name: t_qumen_dgiren_day; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.t_qumen_dgiren_day (
    chart_id text NOT NULL,
    year_pillar text,
    month_pillar text,
    day_pillar text,
    rasklad_id text,
    palace_no integer,
    chart_type text
);


--
-- Name: t_qumen_dgiren_hourly; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.t_qumen_dgiren_hourly (
    chart_id text NOT NULL,
    hour_id text NOT NULL,
    rasklad_id text,
    palace_no integer,
    chart_type text
);


--
-- Name: t_qumen_dgiren_month; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.t_qumen_dgiren_month (
    chart_id text NOT NULL,
    year_pillar text,
    month_pillar text,
    rasklad_id text,
    palace_no integer,
    chart_type text
);


--
-- Name: t_qumen_dgiren_year; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.t_qumen_dgiren_year (
    chart_id text NOT NULL,
    year_pillar text,
    rasklad_id text,
    palace_no integer,
    chart_type text
);


--
-- Name: t_qumen_tayi_day; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.t_qumen_tayi_day (
    date_val date NOT NULL,
    palace_no smallint NOT NULL,
    year_pillar text,
    month_pillar text,
    day_pillar text,
    run_type text,
    tai_yi_palace smallint,
    xiu_men_palace smallint,
    xi_shen_palace smallint,
    star text,
    gate text,
    hhd_spirits text,
    jianchu text,
    is_xi_shen smallint DEFAULT 0,
    is_noble smallint DEFAULT 0,
    is_kong_wang smallint DEFAULT 0,
    gate_score real DEFAULT 0,
    star_score real DEFAULT 0,
    jianchu_score real DEFAULT 0,
    total_score real DEFAULT 0
);


--
-- Name: TABLE t_qumen_tayi_day; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.t_qumen_tayi_day IS 'Итоговый дневной расклад Тай И (плоский: 9 строк/день, 1 строка/дворец)';


--
-- Name: COLUMN t_qumen_tayi_day.date_val; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.t_qumen_tayi_day.date_val IS 'Дата (PK часть 1)';


--
-- Name: COLUMN t_qumen_tayi_day.palace_no; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.t_qumen_tayi_day.palace_no IS 'Номер дворца 1-9 (PK часть 2)';


--
-- Name: COLUMN t_qumen_tayi_day.year_pillar; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.t_qumen_tayi_day.year_pillar IS 'Столп года';


--
-- Name: COLUMN t_qumen_tayi_day.month_pillar; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.t_qumen_tayi_day.month_pillar IS 'Столп месяца';


--
-- Name: COLUMN t_qumen_tayi_day.day_pillar; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.t_qumen_tayi_day.day_pillar IS 'Столп дня';


--
-- Name: COLUMN t_qumen_tayi_day.run_type; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.t_qumen_tayi_day.run_type IS 'Тип цикла YIN/YANG';


--
-- Name: COLUMN t_qumen_tayi_day.tai_yi_palace; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.t_qumen_tayi_day.tai_yi_palace IS 'Дворец Тай И (денормализовано)';


--
-- Name: COLUMN t_qumen_tayi_day.xiu_men_palace; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.t_qumen_tayi_day.xiu_men_palace IS 'Дворец Врат Отдыха';


--
-- Name: COLUMN t_qumen_tayi_day.xi_shen_palace; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.t_qumen_tayi_day.xi_shen_palace IS 'Дворец Духа Счастья';


--
-- Name: COLUMN t_qumen_tayi_day.star; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.t_qumen_tayi_day.star IS 'Звезда дворца (иероглиф)';


--
-- Name: COLUMN t_qumen_tayi_day.gate; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.t_qumen_tayi_day.gate IS 'Врата дворца (иероглиф, NULL для P5)';


--
-- Name: COLUMN t_qumen_tayi_day.hhd_spirits; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.t_qumen_tayi_day.hhd_spirits IS 'Духи ХХД направления (иероглифы, / для 2-ветвевых)';


--
-- Name: COLUMN t_qumen_tayi_day.jianchu; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.t_qumen_tayi_day.jianchu IS '建除 направления (иероглифы)';


--
-- Name: COLUMN t_qumen_tayi_day.is_xi_shen; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.t_qumen_tayi_day.is_xi_shen IS 'Флаг: Дух Счастья в этом дворце';


--
-- Name: COLUMN t_qumen_tayi_day.is_noble; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.t_qumen_tayi_day.is_noble IS 'Флаг: благородное направление (OR)';


--
-- Name: COLUMN t_qumen_tayi_day.is_kong_wang; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.t_qumen_tayi_day.is_kong_wang IS 'Флаг: пустота направления (OR)';


--
-- Name: COLUMN t_qumen_tayi_day.gate_score; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.t_qumen_tayi_day.gate_score IS 'Score врат (-1/0/1)';


--
-- Name: COLUMN t_qumen_tayi_day.star_score; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.t_qumen_tayi_day.star_score IS 'Score звезды (-1/0/1)';


--
-- Name: COLUMN t_qumen_tayi_day.jianchu_score; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.t_qumen_tayi_day.jianchu_score IS 'Score 建除 (avg для 2-ветвевых)';


--
-- Name: COLUMN t_qumen_tayi_day.total_score; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.t_qumen_tayi_day.total_score IS 'Итого: (gate*2+star*2+jianchu+xi_shen+noble)*(1-kong_wang)';


--
-- Name: t_rule_registry; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.t_rule_registry (
    rule_id text NOT NULL,
    name_ru text NOT NULL,
    predicate_code text NOT NULL,
    params_json text,
    score_base double precision,
    score_formula text,
    description text,
    is_active bigint,
    period_type text DEFAULT 'hour'::text
);


--
-- Name: TABLE t_rule_registry; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.t_rule_registry IS 'Реестр правил анализа (predicate_code, period_type, is_active)';


--
-- Name: COLUMN t_rule_registry.rule_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.t_rule_registry.rule_id IS 'MD5-хеш ID правила (PK)';


--
-- Name: COLUMN t_rule_registry.predicate_code; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.t_rule_registry.predicate_code IS 'Код предиката правила';


--
-- Name: COLUMN t_rule_registry.description; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.t_rule_registry.description IS 'Описание правила';


--
-- Name: COLUMN t_rule_registry.is_active; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.t_rule_registry.is_active IS '1=активное, 0=неактивное';


--
-- Name: COLUMN t_rule_registry.period_type; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.t_rule_registry.period_type IS 'Уровень: year/month/day/hour';


--
-- Name: t_rule_scope; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.t_rule_scope (
    rule_id text NOT NULL,
    scope_type text NOT NULL,
    is_stop bigint
);


--
-- Name: TABLE t_rule_scope; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.t_rule_scope IS 'Связь правил с областями применения';


--
-- Name: t_solar_term_time; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.t_solar_term_time (
    year integer NOT NULL,
    solar_term_id integer NOT NULL,
    longitude_deg integer NOT NULL,
    crossing_utc timestamp without time zone NOT NULL,
    crossing_gmt0 timestamp without time zone NOT NULL
);


--
-- Name: TABLE t_solar_term_time; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.t_solar_term_time IS 'Точное время наступления солнечных терминов (астрономический расчёт)';


--
-- Name: t_solar_term_time_hko; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.t_solar_term_time_hko (
    year integer NOT NULL,
    solar_term_id integer NOT NULL,
    longitude_deg integer NOT NULL,
    crossing_hkt timestamp without time zone NOT NULL,
    crossing_utc timestamp without time zone NOT NULL,
    tz_offset_hours integer DEFAULT 8 NOT NULL
);


--
-- Name: TABLE t_solar_term_time_hko; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.t_solar_term_time_hko IS 'Время солнечных терминов из HKO (контрольные данные)';


--
-- Name: t_sys_calculation_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.t_sys_calculation_log (
    id bigint NOT NULL,
    stage_name text NOT NULL,
    start_dt text NOT NULL,
    end_dt text,
    duration_sec double precision,
    record_count bigint,
    status text,
    error_msg text
);


--
-- Name: TABLE t_sys_calculation_log; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.t_sys_calculation_log IS 'Журнал расчётов: этапы, длительность, ошибки';


--
-- Name: t_taiyi_day; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.t_taiyi_day (
    date_val date NOT NULL,
    day_ganzhi_idx integer,
    day_stem integer,
    day_branch integer,
    solar_term_id integer,
    run_type text,
    xiu_men_palace integer,
    tai_yi_palace integer,
    xi_shen_palace integer,
    palace_1_score integer,
    palace_2_score integer,
    palace_3_score integer,
    palace_4_score integer,
    palace_5_score integer,
    palace_6_score integer,
    palace_7_score integer,
    palace_8_score integer,
    palace_9_score integer,
    chart_data jsonb
);


--
-- Name: t_taiyi_hours; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.t_taiyi_hours (
    date_val date NOT NULL,
    hour_branch integer NOT NULL,
    spirit_name text,
    spirit_score integer,
    is_noble boolean,
    is_kong_wang boolean
);


--
-- Name: t_time_grid_hourly; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.t_time_grid_hourly (
    dt_utc text NOT NULL,
    dt_gmt0 text NOT NULL,
    year bigint NOT NULL,
    month bigint NOT NULL,
    day bigint NOT NULL,
    hour bigint NOT NULL,
    weekday bigint NOT NULL
);


--
-- Name: TABLE t_time_grid_hourly; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.t_time_grid_hourly IS 'Сетка двухчасовых слотов (основа для t_bazi_hourly)';


--
-- Name: t_tung_shu_daily; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.t_tung_shu_daily (
    calendar_date date NOT NULL,
    year_pillar text,
    month_pillar text,
    day_pillar text,
    year_stem text,
    year_branch text,
    month_stem text,
    month_branch text,
    day_stem text,
    day_branch text,
    solar_term_id integer,
    solar_term_char text,
    solar_term_name_ru text,
    nayin_element text,
    nayin_name text,
    day_officer_char text,
    day_officer_name_ru text,
    day_officer_category text,
    constellation_char text,
    constellation_name_ru text,
    constellation_direction text,
    constellation_nature text,
    belt_type text,
    belt_stars text,
    moon_phase_name text,
    moon_phase_pct real,
    tongshu_phase_name_ru text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    year_nayin_element text,
    year_nayin_name text,
    month_nayin_element text,
    month_nayin_name text,
    day_nayin_element text,
    day_nayin_name text,
    year_period integer,
    month_period integer,
    day_period integer,
    year_element_num integer,
    month_element_num integer,
    day_element_num integer,
    hexagram_family_same integer,
    production_chain integer,
    lunar_day integer
);


--
-- Name: spr_element_display element_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_element_display ALTER COLUMN element_id SET DEFAULT nextval('public.spr_element_display_element_id_seq'::regclass);


--
-- Name: spr_scdg id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_scdg ALTER COLUMN id SET DEFAULT nextval('public.spr_scdg_id_seq'::regclass);


--
-- Name: t_crm_calculation id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_crm_calculation ALTER COLUMN id SET DEFAULT nextval('public.t_crm_calculation_id_seq'::regclass);


--
-- Name: t_crm_client id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_crm_client ALTER COLUMN id SET DEFAULT nextval('public.t_crm_client_id_seq'::regclass);


--
-- Name: t_crm_note id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_crm_note ALTER COLUMN id SET DEFAULT nextval('public.t_crm_note_id_seq'::regclass);


--
-- Name: t_crm_session id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_crm_session ALTER COLUMN id SET DEFAULT nextval('public.t_crm_session_id_seq'::regclass);


--
-- Name: t_profile id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_profile ALTER COLUMN id SET DEFAULT nextval('public.t_profile_id_seq'::regclass);


--
-- Name: t_profile_birth_chart id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_profile_birth_chart ALTER COLUMN id SET DEFAULT nextval('public.t_profile_birth_chart_id_seq'::regclass);


--
-- Name: t_profile_history id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_profile_history ALTER COLUMN id SET DEFAULT nextval('public.t_profile_history_id_seq'::regclass);


--
-- Name: spr_analysis_scope spr_analysis_scope_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_analysis_scope
    ADD CONSTRAINT spr_analysis_scope_pkey PRIMARY KEY (scope_code);


--
-- Name: spr_bazi_qi_phase spr_bazi_qi_phase_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_bazi_qi_phase
    ADD CONSTRAINT spr_bazi_qi_phase_pkey PRIMARY KEY (id);


--
-- Name: spr_black_rabbit_day_joey spr_black_rabbit_day_joey_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_black_rabbit_day_joey
    ADD CONSTRAINT spr_black_rabbit_day_joey_pkey PRIMARY KEY (first_day_jiazi_id, lunar_day);


--
-- Name: spr_black_rabbit_hour_joey spr_black_rabbit_hour_joey_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_black_rabbit_hour_joey
    ADD CONSTRAINT spr_black_rabbit_hour_joey_pkey PRIMARY KEY (day_stem, hour_branch);


--
-- Name: spr_black_rabbit_matrix spr_black_rabbit_matrix_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_black_rabbit_matrix
    ADD CONSTRAINT spr_black_rabbit_matrix_pkey PRIMARY KEY (jiazi_id, lunar_day);


--
-- Name: spr_black_rabbit_scores spr_black_rabbit_scores_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_black_rabbit_scores
    ADD CONSTRAINT spr_black_rabbit_scores_pkey PRIMARY KEY (star_name);


--
-- Name: spr_column_comment spr_column_comment_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_column_comment
    ADD CONSTRAINT spr_column_comment_pkey PRIMARY KEY (table_name, column_name);


--
-- Name: spr_day_officer_mapping spr_day_officer_mapping_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_day_officer_mapping
    ADD CONSTRAINT spr_day_officer_mapping_pkey PRIMARY KEY (month_branch_id, day_branch_id);


--
-- Name: spr_earthly_branch spr_earthly_branch_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_earthly_branch
    ADD CONSTRAINT spr_earthly_branch_pkey PRIMARY KEY (branch_id);


--
-- Name: spr_element_display spr_element_display_element_name_ru_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_element_display
    ADD CONSTRAINT spr_element_display_element_name_ru_key UNIQUE (element_name_ru);


--
-- Name: spr_element_display spr_element_display_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_element_display
    ADD CONSTRAINT spr_element_display_pkey PRIMARY KEY (element_id);


--
-- Name: spr_flying_star_map spr_flying_star_map_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_flying_star_map
    ADD CONSTRAINT spr_flying_star_map_pkey PRIMARY KEY (center_star, palace);


--
-- Name: spr_gates spr_gates_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_gates
    ADD CONSTRAINT spr_gates_pkey PRIMARY KEY (id);


--
-- Name: spr_gods spr_gods_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_gods
    ADD CONSTRAINT spr_gods_pkey PRIMARY KEY (id);


--
-- Name: spr_heavenly_stem spr_heavenly_stem_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_heavenly_stem
    ADD CONSTRAINT spr_heavenly_stem_pkey PRIMARY KEY (stem_id);


--
-- Name: spr_hour_stars spr_hour_stars_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_hour_stars
    ADD CONSTRAINT spr_hour_stars_pkey PRIMARY KEY (day_branch, yin_yang, hour_branch);


--
-- Name: spr_indicator spr_indicator_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_indicator
    ADD CONSTRAINT spr_indicator_pkey PRIMARY KEY (indicator_id);


--
-- Name: spr_indicator_scope spr_indicator_scope_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_indicator_scope
    ADD CONSTRAINT spr_indicator_scope_pkey PRIMARY KEY (indicator_id, scope_code);


--
-- Name: spr_indicator_value spr_indicator_value_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_indicator_value
    ADD CONSTRAINT spr_indicator_value_pkey PRIMARY KEY (value_id);


--
-- Name: spr_jiazi_extended spr_jiazi_extended_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_jiazi_extended
    ADD CONSTRAINT spr_jiazi_extended_pkey PRIMARY KEY (jiazi_id);


--
-- Name: spr_leader_stems spr_leader_stems_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_leader_stems
    ADD CONSTRAINT spr_leader_stems_pkey PRIMARY KEY (idx);


--
-- Name: spr_master_dano_mapping spr_master_dano_mapping_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_master_dano_mapping
    ADD CONSTRAINT spr_master_dano_mapping_pkey PRIMARY KEY (month_branch_id, day_stem_id, day_branch_id);


--
-- Name: spr_month_stars spr_month_stars_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_month_stars
    ADD CONSTRAINT spr_month_stars_pkey PRIMARY KEY (year_branch, month_branch);


--
-- Name: spr_pillar_cycle spr_pillar_cycle_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_pillar_cycle
    ADD CONSTRAINT spr_pillar_cycle_pkey PRIMARY KEY (cycle_index);


--
-- Name: spr_pillar_hour_rule spr_pillar_hour_rule_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_pillar_hour_rule
    ADD CONSTRAINT spr_pillar_hour_rule_pkey PRIMARY KEY (day_stem_id, hour_branch_id);


--
-- Name: spr_pillar_month_rule spr_pillar_month_rule_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_pillar_month_rule
    ADD CONSTRAINT spr_pillar_month_rule_pkey PRIMARY KEY (year_stem_id, month_index);


--
-- Name: spr_qimen_templates spr_qimen_templates_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_qimen_templates
    ADD CONSTRAINT spr_qimen_templates_pkey PRIMARY KEY (template_id);


--
-- Name: spr_scdg spr_scdg_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_scdg
    ADD CONSTRAINT spr_scdg_pkey PRIMARY KEY (id);


--
-- Name: spr_skdg_hexagram_pairs spr_skdg_hexagram_pairs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_skdg_hexagram_pairs
    ADD CONSTRAINT spr_skdg_hexagram_pairs_pkey PRIMARY KEY (jiazi_id_a, jiazi_id_b);


--
-- Name: spr_skdg_wuxing_relation spr_skdg_wuxing_relation_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_skdg_wuxing_relation
    ADD CONSTRAINT spr_skdg_wuxing_relation_pkey PRIMARY KEY (group_a, group_b);


--
-- Name: spr_solar_term spr_solar_term_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_solar_term
    ADD CONSTRAINT spr_solar_term_pkey PRIMARY KEY (solar_term_id);


--
-- Name: spr_stars spr_stars_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_stars
    ADD CONSTRAINT spr_stars_pkey PRIMARY KEY (id);


--
-- Name: spr_table_comment spr_table_comment_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_table_comment
    ADD CONSTRAINT spr_table_comment_pkey PRIMARY KEY (table_name);


--
-- Name: spr_taiyi_gate_seq spr_taiyi_gate_seq_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_taiyi_gate_seq
    ADD CONSTRAINT spr_taiyi_gate_seq_pkey PRIMARY KEY (cycle_type, seq_idx);


--
-- Name: spr_taiyi_gates spr_taiyi_gates_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_taiyi_gates
    ADD CONSTRAINT spr_taiyi_gates_pkey PRIMARY KEY (id);


--
-- Name: spr_taiyi_jianchu spr_taiyi_jianchu_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_taiyi_jianchu
    ADD CONSTRAINT spr_taiyi_jianchu_pkey PRIMARY KEY (id);


--
-- Name: spr_taiyi_kong_wang spr_taiyi_kong_wang_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_taiyi_kong_wang
    ADD CONSTRAINT spr_taiyi_kong_wang_pkey PRIMARY KEY (day_stem_id, hour_branch_id);


--
-- Name: spr_taiyi_noble spr_taiyi_noble_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_taiyi_noble
    ADD CONSTRAINT spr_taiyi_noble_pkey PRIMARY KEY (day_stem_id, hour_branch_id);


--
-- Name: spr_taiyi_palace_ring spr_taiyi_palace_ring_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_taiyi_palace_ring
    ADD CONSTRAINT spr_taiyi_palace_ring_pkey PRIMARY KEY (palace_id);


--
-- Name: spr_taiyi_qing_long_start spr_taiyi_qing_long_start_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_taiyi_qing_long_start
    ADD CONSTRAINT spr_taiyi_qing_long_start_pkey PRIMARY KEY (day_branch_id);


--
-- Name: spr_taiyi_spirits spr_taiyi_spirits_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_taiyi_spirits
    ADD CONSTRAINT spr_taiyi_spirits_pkey PRIMARY KEY (id);


--
-- Name: spr_taiyi_star_start spr_taiyi_star_start_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_taiyi_star_start
    ADD CONSTRAINT spr_taiyi_star_start_pkey PRIMARY KEY (cycle_type, decade_idx);


--
-- Name: spr_taiyi_stars spr_taiyi_stars_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_taiyi_stars
    ADD CONSTRAINT spr_taiyi_stars_pkey PRIMARY KEY (id);


--
-- Name: spr_taiyi_xi_shen spr_taiyi_xi_shen_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_taiyi_xi_shen
    ADD CONSTRAINT spr_taiyi_xi_shen_pkey PRIMARY KEY (day_stem_id);


--
-- Name: spr_tongshu_black_rabbit_rating spr_tongshu_black_rabbit_rating_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_tongshu_black_rabbit_rating
    ADD CONSTRAINT spr_tongshu_black_rabbit_rating_pkey PRIMARY KEY (star_name);


--
-- Name: spr_tongshu_black_rabbit_star spr_tongshu_black_rabbit_star_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_tongshu_black_rabbit_star
    ADD CONSTRAINT spr_tongshu_black_rabbit_star_pkey PRIMARY KEY (cycle_index, lunar_day, method_code);


--
-- Name: spr_tongshu_branch_combo_rule spr_tongshu_branch_combo_rule_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_tongshu_branch_combo_rule
    ADD CONSTRAINT spr_tongshu_branch_combo_rule_pkey PRIMARY KEY (rule_id);


--
-- Name: spr_tongshu_guigu_outcome spr_tongshu_guigu_outcome_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_tongshu_guigu_outcome
    ADD CONSTRAINT spr_tongshu_guigu_outcome_pkey PRIMARY KEY (outcome_number);


--
-- Name: spr_tongshu_jiazi_profile spr_tongshu_jiazi_profile_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_tongshu_jiazi_profile
    ADD CONSTRAINT spr_tongshu_jiazi_profile_pkey PRIMARY KEY (cycle_index);


--
-- Name: spr_tongshu_phase_mapping spr_tongshu_phase_mapping_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_tongshu_phase_mapping
    ADD CONSTRAINT spr_tongshu_phase_mapping_pkey PRIMARY KEY (day_stem, phase_id);


--
-- Name: spr_tongshu_phase spr_tongshu_phase_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_tongshu_phase
    ADD CONSTRAINT spr_tongshu_phase_pkey PRIMARY KEY (phase_id);


--
-- Name: spr_tongshu_shensha_rule spr_tongshu_shensha_rule_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_tongshu_shensha_rule
    ADD CONSTRAINT spr_tongshu_shensha_rule_pkey PRIMARY KEY (rule_id);


--
-- Name: spr_shensha_config spr_shensha_config_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_shensha_config
    ADD CONSTRAINT spr_shensha_config_pkey PRIMARY KEY (config_id);


--
-- Name: spr_tongshu_stem_combo_rule spr_tongshu_stem_combo_rule_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_tongshu_stem_combo_rule
    ADD CONSTRAINT spr_tongshu_stem_combo_rule_pkey PRIMARY KEY (rule_id);


--
-- Name: spr_tongshu_ten_god spr_tongshu_ten_god_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_tongshu_ten_god
    ADD CONSTRAINT spr_tongshu_ten_god_pkey PRIMARY KEY (day_stem, god_code);


--
-- Name: spr_yanqin_day_constellation spr_yanqin_day_constellation_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_yanqin_day_constellation
    ADD CONSTRAINT spr_yanqin_day_constellation_pkey PRIMARY KEY (dow, branch_group);


--
-- Name: spr_yellow_black_matrix spr_yellow_black_matrix_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_yellow_black_matrix
    ADD CONSTRAINT spr_yellow_black_matrix_pkey PRIMARY KEY (month_branch, day_branch);


--
-- Name: spr_yellow_black_stars spr_yellow_black_stars_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_yellow_black_stars
    ADD CONSTRAINT spr_yellow_black_stars_pkey PRIMARY KEY (id);


--
-- Name: t_analysis_date t_analysis_date_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_analysis_date
    ADD CONSTRAINT t_analysis_date_pkey PRIMARY KEY (hour_id, rule_id);


--
-- Name: t_analysis_day t_analysis_day_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_analysis_day
    ADD CONSTRAINT t_analysis_day_pkey PRIMARY KEY (date_val, rule_id, result_value, year_pillar, month_pillar, day_pillar);


--
-- Name: t_analysis_direction_day t_analysis_direction_day_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_analysis_direction_day
    ADD CONSTRAINT t_analysis_direction_day_pkey PRIMARY KEY (date_val, palace_no, system_type, rule_id, year_pillar, month_pillar, day_pillar);


--
-- Name: t_analysis_direction_hour t_analysis_direction_hour_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_analysis_direction_hour
    ADD CONSTRAINT t_analysis_direction_hour_pkey PRIMARY KEY (hour_id, palace_no, system_type, rule_id);


--
-- Name: t_analysis_direction_month t_analysis_direction_month_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_analysis_direction_month
    ADD CONSTRAINT t_analysis_direction_month_pkey PRIMARY KEY (year, month, palace_no, system_type, rule_id, year_pillar, month_pillar);


--
-- Name: t_analysis_direction t_analysis_direction_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_analysis_direction
    ADD CONSTRAINT t_analysis_direction_pkey PRIMARY KEY (hour_id, palace_no, system_type, chart_level, rule_id);


--
-- Name: t_analysis_direction_year t_analysis_direction_year_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_analysis_direction_year
    ADD CONSTRAINT t_analysis_direction_year_pkey PRIMARY KEY (year, palace_no, system_type, rule_id, year_pillar);


--
-- Name: t_analysis_hour t_analysis_hour_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_analysis_hour
    ADD CONSTRAINT t_analysis_hour_pkey PRIMARY KEY (hour_id, rule_id);


--
-- Name: t_analysis_month t_analysis_month_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_analysis_month
    ADD CONSTRAINT t_analysis_month_pkey PRIMARY KEY (year, month, rule_id, result_value, year_pillar, month_pillar);


--
-- Name: t_analysis_year t_analysis_year_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_analysis_year
    ADD CONSTRAINT t_analysis_year_pkey PRIMARY KEY (year, rule_id, result_value, year_pillar);


--
-- Name: t_bazi_hourly t_bazi_hourly_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_bazi_hourly
    ADD CONSTRAINT t_bazi_hourly_pkey PRIMARY KEY (tz_offset_hours, slot_start_date_utc, slot_start_time_utc);


--
-- Name: t_crm_calculation t_crm_calculation_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_crm_calculation
    ADD CONSTRAINT t_crm_calculation_pkey PRIMARY KEY (id);


--
-- Name: t_crm_client t_crm_client_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_crm_client
    ADD CONSTRAINT t_crm_client_pkey PRIMARY KEY (id);


--
-- Name: t_crm_note t_crm_note_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_crm_note
    ADD CONSTRAINT t_crm_note_pkey PRIMARY KEY (id);


--
-- Name: t_crm_session t_crm_session_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_crm_session
    ADD CONSTRAINT t_crm_session_pkey PRIMARY KEY (id);


--
-- Name: t_event t_event_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_event
    ADD CONSTRAINT t_event_pkey PRIMARY KEY (id);


--
-- Name: t_flying_stars t_flying_stars_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_flying_stars
    ADD CONSTRAINT t_flying_stars_pkey PRIMARY KEY (hour_id, palace);


--
-- Name: t_profile_birth_chart t_profile_birth_chart_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_profile_birth_chart
    ADD CONSTRAINT t_profile_birth_chart_pkey PRIMARY KEY (id);


--
-- Name: t_profile_history t_profile_history_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_profile_history
    ADD CONSTRAINT t_profile_history_pkey PRIMARY KEY (id);


--
-- Name: t_profile t_profile_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_profile
    ADD CONSTRAINT t_profile_pkey PRIMARY KEY (id);


--
-- Name: t_qumen_chauby_hourly t_qumen_chauby_hourly_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_qumen_chauby_hourly
    ADD CONSTRAINT t_qumen_chauby_hourly_pkey PRIMARY KEY (chart_id);


--
-- Name: t_qumen_dgiren_day t_qumen_dgiren_day_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_qumen_dgiren_day
    ADD CONSTRAINT t_qumen_dgiren_day_pkey PRIMARY KEY (chart_id);


--
-- Name: t_qumen_dgiren_hourly t_qumen_dgiren_hourly_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_qumen_dgiren_hourly
    ADD CONSTRAINT t_qumen_dgiren_hourly_pkey PRIMARY KEY (chart_id);


--
-- Name: t_qumen_dgiren_month t_qumen_dgiren_month_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_qumen_dgiren_month
    ADD CONSTRAINT t_qumen_dgiren_month_pkey PRIMARY KEY (chart_id);


--
-- Name: t_qumen_dgiren_year t_qumen_dgiren_year_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_qumen_dgiren_year
    ADD CONSTRAINT t_qumen_dgiren_year_pkey PRIMARY KEY (chart_id);


--
-- Name: t_qumen_tayi_day t_qumen_tayi_day_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_qumen_tayi_day
    ADD CONSTRAINT t_qumen_tayi_day_pkey PRIMARY KEY (date_val, palace_no);


--
-- Name: t_rule_registry t_rule_registry_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_rule_registry
    ADD CONSTRAINT t_rule_registry_pkey PRIMARY KEY (rule_id);


--
-- Name: t_rule_scope t_rule_scope_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_rule_scope
    ADD CONSTRAINT t_rule_scope_pkey PRIMARY KEY (rule_id, scope_type);


--
-- Name: t_solar_term_time_hko t_solar_term_time_hko_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_solar_term_time_hko
    ADD CONSTRAINT t_solar_term_time_hko_pkey PRIMARY KEY (year, solar_term_id);


--
-- Name: t_solar_term_time t_solar_term_time_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_solar_term_time
    ADD CONSTRAINT t_solar_term_time_pkey PRIMARY KEY (year, solar_term_id);


--
-- Name: t_sys_calculation_log t_sys_calculation_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_sys_calculation_log
    ADD CONSTRAINT t_sys_calculation_log_pkey PRIMARY KEY (id);


--
-- Name: t_taiyi_day t_taiyi_day_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_taiyi_day
    ADD CONSTRAINT t_taiyi_day_pkey PRIMARY KEY (date_val);


--
-- Name: t_taiyi_hours t_taiyi_hours_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_taiyi_hours
    ADD CONSTRAINT t_taiyi_hours_pkey PRIMARY KEY (date_val, hour_branch);


--
-- Name: t_tung_shu_daily t_tung_shu_daily_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_tung_shu_daily
    ADD CONSTRAINT t_tung_shu_daily_pkey PRIMARY KEY (calendar_date);


--
-- Name: t_profile_birth_chart uq_profile_birth_chart; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_profile_birth_chart
    ADD CONSTRAINT uq_profile_birth_chart UNIQUE (profile_id);


--
-- Name: idx_bazi_hourly_local; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_bazi_hourly_local ON public.t_bazi_hourly USING btree (tz_offset_hours, slot_start_date_local, slot_start_time_local);


--
-- Name: idx_bazi_hourly_utc; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_bazi_hourly_utc ON public.t_bazi_hourly USING btree (tz_offset_hours, slot_start_date_utc, slot_start_time_utc);


--
-- Name: idx_fs_hour; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_fs_hour ON public.t_flying_stars USING btree (hour_id);


--
-- Name: idx_jiazi_stem_branch; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_jiazi_stem_branch ON public.spr_jiazi_extended USING btree (stem, branch);


--
-- Name: idx_profile_birth_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_profile_birth_date ON public.t_profile USING btree (birth_date);


--
-- Name: idx_profile_history_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_profile_history_created_at ON public.t_profile_history USING btree (created_at);


--
-- Name: idx_profile_history_profile_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_profile_history_profile_id ON public.t_profile_history USING btree (profile_id);


--
-- Name: idx_profile_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_profile_name ON public.t_profile USING btree (name);


--
-- Name: idx_qi_phase_stem_branch; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_qi_phase_stem_branch ON public.spr_bazi_qi_phase USING btree (stem_char, branch_char);


--
-- Name: idx_qimen_cb_hr_hour; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_qimen_cb_hr_hour ON public.t_qumen_chauby_hourly USING btree (hour_id);


--
-- Name: idx_qimen_d_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_qimen_d_date ON public.t_qumen_dgiren_day USING btree (year_pillar, month_pillar, day_pillar);


--
-- Name: idx_qimen_hr_hour; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_qimen_hr_hour ON public.t_qumen_dgiren_hourly USING btree (hour_id);


--
-- Name: idx_qimen_templates_rasklad; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_qimen_templates_rasklad ON public.spr_qimen_templates USING btree (rasklad_id, palace_no);


--
-- Name: idx_qimen_templates_stems; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_qimen_templates_stems ON public.spr_qimen_templates USING btree (heaven_stem, earth_stem);


--
-- Name: idx_taiyi_hours_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_taiyi_hours_date ON public.t_taiyi_hours USING btree (date_val);


--
-- Name: ix_t_crm_calculation_calculation_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_t_crm_calculation_calculation_type ON public.t_crm_calculation USING btree (calculation_type);


--
-- Name: ix_t_crm_calculation_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_t_crm_calculation_id ON public.t_crm_calculation USING btree (id);


--
-- Name: ix_t_crm_client_email; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_t_crm_client_email ON public.t_crm_client USING btree (email);


--
-- Name: ix_t_crm_client_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_t_crm_client_id ON public.t_crm_client USING btree (id);


--
-- Name: ix_t_crm_client_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_t_crm_client_name ON public.t_crm_client USING btree (name);


--
-- Name: ix_t_crm_client_phone; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_t_crm_client_phone ON public.t_crm_client USING btree (phone);


--
-- Name: ix_t_crm_note_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_t_crm_note_id ON public.t_crm_note USING btree (id);


--
-- Name: ix_t_crm_session_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_t_crm_session_date ON public.t_crm_session USING btree (date);


--
-- Name: ix_t_crm_session_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_t_crm_session_id ON public.t_crm_session USING btree (id);


--
-- Name: t_profile trg_profile_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_profile_updated_at BEFORE UPDATE ON public.t_profile FOR EACH ROW EXECUTE FUNCTION public.update_profile_updated_at();


--
-- Name: spr_tongshu_black_rabbit_star spr_tongshu_black_rabbit_star_cycle_index_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spr_tongshu_black_rabbit_star
    ADD CONSTRAINT spr_tongshu_black_rabbit_star_cycle_index_fkey FOREIGN KEY (cycle_index) REFERENCES public.spr_tongshu_jiazi_profile(cycle_index);


--
-- Name: t_crm_calculation t_crm_calculation_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_crm_calculation
    ADD CONSTRAINT t_crm_calculation_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.t_crm_client(id) ON DELETE CASCADE;


--
-- Name: t_crm_note t_crm_note_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_crm_note
    ADD CONSTRAINT t_crm_note_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.t_crm_client(id) ON DELETE CASCADE;


--
-- Name: t_crm_session t_crm_session_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_crm_session
    ADD CONSTRAINT t_crm_session_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.t_crm_client(id) ON DELETE CASCADE;


--
-- Name: t_profile_birth_chart t_profile_birth_chart_profile_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_profile_birth_chart
    ADD CONSTRAINT t_profile_birth_chart_profile_id_fkey FOREIGN KEY (profile_id) REFERENCES public.t_profile(id) ON DELETE CASCADE;


--
-- Name: t_profile_history t_profile_history_profile_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_profile_history
    ADD CONSTRAINT t_profile_history_profile_id_fkey FOREIGN KEY (profile_id) REFERENCES public.t_profile(id) ON DELETE CASCADE;


--
-- Name: t_solar_term_time_hko t_solar_term_time_hko_solar_term_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_solar_term_time_hko
    ADD CONSTRAINT t_solar_term_time_hko_solar_term_id_fkey FOREIGN KEY (solar_term_id) REFERENCES public.spr_solar_term(solar_term_id);


--
-- Name: t_solar_term_time t_solar_term_time_solar_term_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_solar_term_time
    ADD CONSTRAINT t_solar_term_time_solar_term_id_fkey FOREIGN KEY (solar_term_id) REFERENCES public.spr_solar_term(solar_term_id);


--
-- PostgreSQL database dump complete
--

\unrestrict oMjAS6ar2WZJ6sYi3ptgq8AqfODepklvipbTI52IfaVJscbjyXU9efoFQ79sOfZ

