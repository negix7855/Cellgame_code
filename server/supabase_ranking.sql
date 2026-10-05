-- =========================================================
-- 本番問題（スコアアタック）のランキング
-- Supabase の SQL Editor に貼り付けて、まとめて実行する
--
-- ゲーム側（scenes/production_scene.py）の設定と合わせること
--   問題数            5
--   制限時間          60秒   (TIME_LIMIT)
--   正解時の倍率      2倍    (CORRECT_MULTIPLIER)
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
    score         integer  not null check (score between 0 and 600),
    correct_count smallint not null check (correct_count between 0 and 5),

    -- 1問ごとの結果 [{"is_correct": bool, "remaining_seconds": int, "time_up": bool}, ...]
    details       jsonb    not null,

    -- 登録日時はサーバーの時刻で記録する
    created_at    timestamptz not null default now()
);

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
    question_count constant integer := 5;
    time_limit     constant integer := 60;
    multiplier     constant integer := 2;

    item       jsonb;
    is_correct boolean;
    time_up    boolean;
    remaining  integer;

    total_score   integer := 0;
    total_correct integer := 0;

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

    for item in select value from jsonb_array_elements(p_details) loop
        -- 項目が無い場合（NULL）もはじくため is distinct from で比べる
        if jsonb_typeof(item -> 'is_correct') is distinct from 'boolean'
           or jsonb_typeof(item -> 'time_up') is distinct from 'boolean'
           or jsonb_typeof(item -> 'remaining_seconds') is distinct from 'number' then
            raise exception 'invalid details';
        end if;

        is_correct := (item ->> 'is_correct')::boolean;
        time_up    := (item ->> 'time_up')::boolean;
        remaining  := (item ->> 'remaining_seconds')::numeric::integer;

        if remaining not between 0 and time_limit then
            raise exception 'invalid remaining_seconds';
        end if;

        -- 時間切れなら正解ではあり得ない
        if time_up and is_correct then
            raise exception 'invalid details';
        end if;

        if is_correct then
            total_score   := total_score + remaining * multiplier;
            total_correct := total_correct + 1;
        end if;
    end loop;

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
