-- =========================================================
-- 本番問題（スコアアタック）のランキング
-- Supabase の SQL Editor に貼り付けて、まとめて実行する
-- （何度実行しても大丈夫。ルールを変えた時はこのファイルを丸ごと再実行する）
--
-- スコアの計算はゲーム側の systems/score.py と同じにすること
--   1問のスコア
--     基礎スコア = その問題で拾ったコインの合計
--     正解       = 基礎スコア × 2 × 連続正解の倍率（2問目 1.1 / 3問目 1.2 / 4問目 1.3 / 5問目 1.5）
--     不正解     = 基礎スコア × 0.5
--     時間切れ   = 0点
--   最終スコア = 問題スコアの合計 + 全問正解ボーナス 5000点 + 残り時間の合計 × 150点
--
-- ゲーム側の設定と合わせること
--   問題数                5
--   制限時間              60秒   (scenes/production_scene.py の TIME_LIMIT)
--   1問のコインの最大合計 5700点 (data/exam/case*.csv の coin_* の枚数 × 金額)
--   理論上の最高点        119540点
-- =========================================================


-- ---------------------------------------------------------
-- スコアのテーブル
-- ---------------------------------------------------------

create table if not exists public.scores (
    id            bigint generated always as identity primary key,

    -- キーボードで入力できる文字だけ（A-Z, 0-9, ! ? # @）、1〜15文字
    nickname      text     not null
                  check (char_length(nickname) between 1 and 15
                         and nickname ~ '^[A-Z0-9!?#@]+$'),

    -- 都道府県コード（1 = 北海道 ... 47 = 沖縄県）
    prefecture    smallint not null check (prefecture between 1 and 47),

    -- 合計スコアと正解数は、サーバー側で details から計算する
    score         integer  not null,
    correct_count smallint not null check (correct_count between 0 and 5),

    -- 1問ごとの結果
    -- [{"is_correct": bool, "time_up": bool, "remaining_seconds": int, "coin_score": int}, ...]
    details       jsonb    not null,

    -- 登録日時はサーバーの時刻で記録する
    created_at    timestamptz not null default now()
);

-- スコアの範囲（ルールを変えた時に作り直せるよう、名前を付けて別に定義する）
alter table public.scores drop constraint if exists scores_score_check;
alter table public.scores add constraint scores_score_check check (score between 0 and 119540);

-- ランキングの並び順（スコアが高い順 → 同点なら新しい順）
create index if not exists scores_ranking_idx
    on public.scores (score desc, created_at desc, id desc);

-- テーブルは直接読み書きさせない（下の2つの関数からだけ使う）
alter table public.scores enable row level security;
revoke all on table public.scores from anon, authenticated;


-- ---------------------------------------------------------
-- スコアを登録する
--   入力を確認し、details から合計スコアを計算して登録する
--   戻り値: {"id": 登録した行の id, "rank": 順位, "score": 合計スコア}
-- ---------------------------------------------------------

create or replace function public.submit_score(
    p_nickname   text,
    p_prefecture integer,
    p_details    jsonb
)
returns json
language plpgsql
security definer
set search_path = public
as $$
declare
    question_count        constant integer := 5;
    time_limit            constant integer := 60;
    max_coin_score        constant integer := 5700;
    all_correct_bonus     constant integer := 5000;
    time_bonus_per_second constant integer := 150;

    item       jsonb;
    is_correct boolean;
    time_up    boolean;
    remaining  integer;
    coins      integer;
    multiplier integer;

    streak          integer := 0;
    question_total  integer := 0;
    remaining_total integer := 0;
    total_correct   integer := 0;
    total_score     integer;

    new_id   bigint;
    new_rank bigint;
begin
    -- ニックネーム
    if p_nickname is null
       or char_length(p_nickname) not between 1 and 15
       or p_nickname !~ '^[A-Z0-9!?#@]+$' then
        raise exception 'invalid nickname';
    end if;

    -- 都道府県
    if p_prefecture is null or p_prefecture not between 1 and 47 then
        raise exception 'invalid prefecture';
    end if;

    -- 1問ごとの結果
    if p_details is null
       or jsonb_typeof(p_details) <> 'array'
       or jsonb_array_length(p_details) <> question_count then
        raise exception 'invalid details';
    end if;

    -- 出題順に計算する（連続正解の倍率が順番で変わるため）
    for item in select value from jsonb_array_elements(p_details) with ordinality as t(value, n) order by n loop
        -- 項目が無い場合（NULL）もはじくため is distinct from で比べる
        if jsonb_typeof(item -> 'is_correct') is distinct from 'boolean'
           or jsonb_typeof(item -> 'time_up') is distinct from 'boolean'
           or jsonb_typeof(item -> 'remaining_seconds') is distinct from 'number'
           or jsonb_typeof(item -> 'coin_score') is distinct from 'number' then
            raise exception 'invalid details';
        end if;

        is_correct := (item ->> 'is_correct')::boolean;
        time_up    := (item ->> 'time_up')::boolean;
        remaining  := (item ->> 'remaining_seconds')::numeric::integer;
        coins      := (item ->> 'coin_score')::numeric::integer;

        if remaining not between 0 and time_limit then
            raise exception 'invalid remaining_seconds';
        end if;

        -- コインは10点単位で、マップにある分まで
        if coins not between 0 and max_coin_score or coins % 10 <> 0 then
            raise exception 'invalid coin_score';
        end if;

        -- 時間切れなら正解ではあり得ず、残り時間も0秒
        if time_up and (is_correct or remaining <> 0) then
            raise exception 'invalid details';
        end if;

        if time_up then
            streak := 0;

        elsif is_correct then
            streak := streak + 1;
            total_correct := total_correct + 1;

            -- 連続正解の倍率（10倍した整数。11 = 1.1倍）
            multiplier := case streak
                when 1 then 10
                when 2 then 11
                when 3 then 12
                when 4 then 13
                else 15
            end;

            question_total := question_total + coins * 2 * multiplier / 10;

        else
            streak := 0;
            question_total := question_total + coins / 2;
        end if;

        remaining_total := remaining_total + remaining;
    end loop;

    total_score := question_total
                 + case when total_correct = question_count then all_correct_bonus else 0 end
                 + remaining_total * time_bonus_per_second;

    insert into public.scores (nickname, prefecture, score, correct_count, details)
    values (p_nickname, p_prefecture, total_score, total_correct, p_details)
    returning id into new_id;

    -- 同点なら新しい方が上なので、「自分より高い人の数 + 1」が順位になる
    select count(*) + 1 into new_rank
    from public.scores
    where score > total_score;

    return json_build_object('id', new_id, 'rank', new_rank, 'score', total_score);
end;
$$;


-- ---------------------------------------------------------
-- ランキング（上位30件）を取得する
--   並び順: スコアが高い順 → 同点なら新しい順
--   日時は日本時間の "YYYY/MM/DD HH:MM"
-- ---------------------------------------------------------

create or replace function public.get_ranking()
returns table (
    id         bigint,
    rank       bigint,
    score      integer,
    nickname   text,
    prefecture smallint,
    created_at text
)
language sql
stable
security definer
set search_path = public
as $$
    select
        s.id,
        row_number() over (order by s.score desc, s.created_at desc, s.id desc) as rank,
        s.score,
        s.nickname,
        s.prefecture,
        to_char(s.created_at at time zone 'Asia/Tokyo', 'YYYY/MM/DD HH24:MI') as created_at
    from public.scores s
    order by s.score desc, s.created_at desc, s.id desc
    limit 30;
$$;


-- ---------------------------------------------------------
-- 権限: ゲーム（anon）からはこの2つの関数だけを呼べるようにする
-- ---------------------------------------------------------

revoke all on function public.submit_score(text, integer, jsonb) from public;
revoke all on function public.get_ranking() from public;

grant execute on function public.submit_score(text, integer, jsonb) to anon;
grant execute on function public.get_ranking() to anon;

-- API に関数の変更をすぐ反映させる
notify pgrst, 'reload schema';
