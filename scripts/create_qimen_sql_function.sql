CREATE OR REPLACE FUNCTION compute_qimen_chart(
    p_hour_id TEXT,
    p_solar_term_id INT,
    p_day_stem TEXT,
    p_day_branch TEXT,
    p_hour_stem TEXT,
    p_hour_branch TEXT,
    p_forced_ju INT DEFAULT NULL,
    p_forced_yin_yang TEXT DEFAULT NULL
) RETURNS JSONB AS $$
BEGIN
    RETURN (
        WITH 
        -- 0-based indexes for stems and branches
        stem_idx AS (
            SELECT stem_char, stem_id - 1 AS idx 
            FROM spr_heavenly_stem
        ),
        branch_idx AS (
            SELECT branch_char, branch_id - 1 AS idx 
            FROM spr_earthly_branch
        ),
        
        -- jiazi cycle index for day pillar
        day_cycle AS (
            SELECT ((6 * ds.idx - 5 * db.idx + 60) % 60) AS cycle_idx
            FROM stem_idx ds, branch_idx db
            WHERE ds.stem_char = p_day_stem AND db.branch_char = p_day_branch
        ),
        
        -- jiazi cycle index for hour pillar
        hour_cycle AS (
            SELECT ((6 * hs.idx - 5 * hb.idx + 60) % 60) AS cycle_idx
            FROM stem_idx hs, branch_idx hb
            WHERE hs.stem_char = p_hour_stem AND hb.branch_char = p_hour_branch
        ),
        
        -- determine ju_num, yin_yang, is_yang
        params AS (
            SELECT
                CASE 
                    WHEN p_forced_ju IS NOT NULL AND p_forced_yin_yang IS NOT NULL THEN p_forced_ju
                    ELSE COALESCE(
                        (SELECT CASE 
                            WHEN dc.cycle_idx / 5 % 3 = 0 THEN st.upper_ju
                            WHEN dc.cycle_idx / 5 % 3 = 1 THEN st.middle_ju
                            ELSE st.lower_ju
                        END
                        FROM day_cycle dc, spr_solar_term st
                        WHERE st.solar_term_id = p_solar_term_id),
                        1
                    )
                END AS ju_num,
                CASE
                    WHEN p_forced_yin_yang IS NOT NULL THEN p_forced_yin_yang
                    WHEN p_solar_term_id BETWEEN 10 AND 21 THEN 'Yin'
                    ELSE 'Yang'
                END AS yin_yang,
                CASE
                    WHEN p_forced_yin_yang IS NOT NULL THEN (p_forced_yin_yang = 'Yang')
                    WHEN p_solar_term_id BETWEEN 10 AND 21 THEN FALSE
                    ELSE TRUE
                END AS is_yang
        ),
        
        -- earth plate (di pan)
        earth_plate AS (
            SELECT 
                CASE WHEN p.is_yang 
                    THEN ((p.ju_num - 1 + (t.ord - 1)) % 9) + 1
                    ELSE (((p.ju_num - 1 - (t.ord - 1)) % 9) + 9) % 9 + 1
                END AS palace_no,
                t.stem
            FROM params p,
            LATERAL (VALUES 
                (1, '戊'), (2, '己'), (3, '庚'), (4, '辛'), 
                (5, '壬'), (6, '癸'), (7, '丁'), (8, '丙'), (9, '乙')
            ) AS t(ord, stem)
        ),
        
        -- leader (xun shou) info
        leader_info AS (
            SELECT 
                ls.stem AS leader_stem,
                ep.palace_no AS leader_palace,
                CASE WHEN ep.palace_no = 5 THEN 2 ELSE ep.palace_no END AS origin_palace_for_leader,
                (SELECT star_char FROM spr_qimen_stars WHERE star_id = CASE WHEN ep.palace_no = 5 THEN 2 ELSE ep.palace_no END) AS zhi_fu_star,
                (SELECT gate_char FROM spr_qimen_gates WHERE gate_id = CASE WHEN ep.palace_no = 5 THEN 2 ELSE ep.palace_no END) AS zhi_shi_gate
            FROM hour_cycle hc
            CROSS JOIN params p
            JOIN spr_leader_stems ls ON ls.idx = hc.cycle_idx / 10
            JOIN earth_plate ep ON ep.stem = ls.stem
        ),
        
        -- target stem and palace for heaven plate
        target_info AS (
            SELECT 
                CASE WHEN p_hour_stem = '甲' THEN l.leader_stem ELSE p_hour_stem END AS target_stem,
                ep.palace_no AS target_palace,
                CASE WHEN ep.palace_no = 5 THEN 2 ELSE ep.palace_no END AS target_palace_effective
            FROM leader_info l
            JOIN earth_plate ep ON ep.stem = CASE WHEN p_hour_stem = '甲' THEN l.leader_stem ELSE p_hour_stem END
        ),
        
        -- common sequences
        star_seq AS (SELECT ARRAY[1, 8, 3, 4, 9, 2, 7, 6] AS seq),
        gate_seq AS (SELECT ARRAY[1, 8, 3, 4, 9, 2, 7, 6] AS seq),
        ring_seq AS (SELECT ARRAY[1, 8, 3, 4, 9, 2, 7, 6] AS seq),
        gods_arr AS (
            SELECT array_agg(spirit_char ORDER BY spirit_id) AS gods 
            FROM spr_qimen_spirits
        ),
        
        -- heaven plate offset
        heaven_star_offset AS (
            SELECT 
                (((array_position(s.seq, t.target_palace_effective) - 1)
                - (array_position(s.seq, l.origin_palace_for_leader) - 1)) % 8 + 8) % 8 AS offset
            FROM star_seq s, target_info t, leader_info l
        ),
        
        -- heaven plate (tian pan) + star plate
        heaven_plate AS (
            SELECT 
                s.seq[(((i - 1 + o.offset) % 8 + 8) % 8) + 1] AS palace_no,
                ep.stem AS heaven_stem,
                qs.star_char AS star_name,
                CASE WHEN s.seq[i] = 2 THEN ep5.stem END AS center_stem
            FROM star_seq s
            CROSS JOIN generate_series(1, 8) AS i
            CROSS JOIN heaven_star_offset o
            JOIN earth_plate ep ON ep.palace_no = s.seq[i]
            LEFT JOIN earth_plate ep5 ON ep5.palace_no = 5
            JOIN spr_qimen_stars qs ON qs.star_id = s.seq[i]
        ),
        
        -- gate movement info
        gate_info AS (
            SELECT 
                hc.cycle_idx - (hc.cycle_idx / 10) * 10 AS diff,
                CASE WHEN p.is_yang
                    THEN ((l.leader_palace - 1 + (hc.cycle_idx - (hc.cycle_idx / 10) * 10)) % 9) + 1
                    ELSE (((l.leader_palace - 1 - (hc.cycle_idx - (hc.cycle_idx / 10) * 10)) % 9) + 9) % 9 + 1
                END AS target_gate_palace
            FROM hour_cycle hc, params p, leader_info l
        ),
        
        -- gate plate offset
        gate_offset AS (
            SELECT 
                (((array_position(s.seq, CASE WHEN g.target_gate_palace = 5 THEN 2 ELSE g.target_gate_palace END) - 1)
                - (array_position(s.seq, l.origin_palace_for_leader) - 1)) % 8 + 8) % 8 AS g_offset
            FROM gate_seq s, gate_info g, leader_info l
        ),
        
        -- gate plate
        gate_plate AS (
            SELECT 
                s.seq[(((i - 1 + o.g_offset) % 8 + 8) % 8) + 1] AS palace_no,
                qg.gate_char AS gate_name
            FROM gate_seq s
            CROSS JOIN generate_series(1, 8) AS i
            CROSS JOIN gate_offset o
            JOIN spr_qimen_gates qg ON qg.gate_id = s.seq[i]
        ),
        
        -- spirit plate
        spirit_plate AS (
            SELECT 
                s.seq[((((array_position(s.seq, t.target_palace_effective) - 1 + 
                    CASE WHEN p.is_yang THEN (g.i - 1) ELSE -(g.i - 1) END) % 8) + 8) % 8) + 1] AS palace_no,
                ga.gods[g.i] AS spirit_name
            FROM ring_seq s
            CROSS JOIN generate_series(1, 8) AS g(i)
            CROSS JOIN target_info t
            CROSS JOIN gods_arr ga
            CROSS JOIN params p
        ),
        
        -- assemble all palaces
        palaces AS (
            SELECT 
                p.palace_no,
                COALESCE(ep.stem, '') AS earth_stem,
                CASE WHEN COALESCE(ep.stem, '') = l.leader_stem THEN 1 ELSE 0 END AS is_fou_tou_earth,
                CASE WHEN p.palace_no = 5 THEN '' ELSE COALESCE(hp.heaven_stem, '') END AS heaven_stem,
                CASE WHEN (COALESCE(hp.heaven_stem, '') = l.leader_stem OR COALESCE(hp.center_stem, '') = l.leader_stem) THEN 1 ELSE 0 END AS is_fou_tou_heaven,
                CASE WHEN p.palace_no = 5 THEN '禽' ELSE COALESCE(hp.star_name, '') END AS star,
                CASE WHEN (CASE WHEN p.palace_no = 5 THEN '禽' ELSE COALESCE(hp.star_name, '') END) = l.zhi_fu_star THEN 1 ELSE 0 END AS is_main_star,
                COALESCE(gp.gate_name, '') AS gate,
                CASE WHEN COALESCE(gp.gate_name, '') = l.zhi_shi_gate THEN 1 ELSE 0 END AS is_main_gate,
                COALESCE(sp.spirit_name, '') AS spirit
            FROM generate_series(1, 9) AS p(palace_no)
            LEFT JOIN earth_plate ep ON ep.palace_no = p.palace_no
            LEFT JOIN heaven_plate hp ON hp.palace_no = p.palace_no
            LEFT JOIN gate_plate gp ON gp.palace_no = p.palace_no
            LEFT JOIN spirit_plate sp ON sp.palace_no = p.palace_no
            CROSS JOIN leader_info l
        )
        
        SELECT jsonb_build_object(
            'hour_id', p_hour_id,
            'chart_num', (SELECT ju_num FROM params),
            'yin_yang', (SELECT yin_yang FROM params),
            'palaces', jsonb_object_agg(
                p.palace_no::text,
                jsonb_build_object(
                    'palace_no', p.palace_no,
                    'earth_stem', p.earth_stem,
                    'is_fou_tou_earth', p.is_fou_tou_earth,
                    'heaven_stem', p.heaven_stem,
                    'is_fou_tou_heaven', p.is_fou_tou_heaven,
                    'star', p.star,
                    'is_main_star', p.is_main_star,
                    'gate', p.gate,
                    'is_main_gate', p.is_main_gate,
                    'spirit', p.spirit
                )
            )
        )
        FROM palaces p
    );
END;
$$ LANGUAGE plpgsql;
