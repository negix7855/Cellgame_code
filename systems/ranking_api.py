import asyncio
import json
import sys

import ranking_config

# 応答がなければ諦めるまでの秒数
TIMEOUT_SECONDS = 10

# ブラウザ（pygbag）では JavaScript の fetch で通信する。
# pygbag の platform.jsiter は、ジェネレータが最後に yield した値を返すので、
# 応答が来るまでは空の yield を続け、最後に結果（JSON 文字列）を1回だけ yield する。
_BROWSER_JS = """
window.CellRanking = window.CellRanking || {};
window.CellRanking.request = function* (url, headersJson, body, timeoutMs) {
    var result = null;
    var controller = new AbortController();
    var timer = setTimeout(function () { controller.abort(); }, timeoutMs);

    fetch(url, {
        method: "POST",
        headers: JSON.parse(headersJson),
        body: body,
        signal: controller.signal
    })
    .then(function (resp) {
        return resp.text().then(function (text) {
            result = JSON.stringify({status: resp.status, text: text});
        });
    })
    .catch(function (err) {
        result = JSON.stringify({status: 0, text: String(err)});
    })
    .finally(function () {
        clearTimeout(timer);
    });

    while (result === null) {
        yield;
    }
    yield result;
};
"""

_browser_ready = False


class RankingError(Exception):
    """ランキングの通信に失敗した時のエラー（メッセージはそのまま画面に出せる）"""


# =========================
# ゲームから使う関数
# =========================

def is_configured():
    """接続先（ranking_config.py）が設定されているか"""
    return bool(ranking_config.SUPABASE_URL and ranking_config.SUPABASE_KEY)


def make_details(results):
    """本番の結果（ProductionScene.get_result() のリスト）を送信用の形にする"""
    return [
        {
            "is_correct": bool(r["is_correct"]),
            "remaining_seconds": int(r["remaining_seconds"]),
            "time_up": bool(r["time_up"]),
        }
        for r in results
    ]


async def submit_score(nickname, prefecture, details):
    """スコアを登録する。戻り値: {"id": ..., "rank": ..., "score": ...}"""
    return await _call_rpc("submit_score", {
        "p_nickname": nickname,
        "p_prefecture": prefecture,
        "p_details": details,
    })


async def fetch_ranking():
    """上位30件を取得する。
    戻り値: [{"id", "rank", "score", "nickname", "prefecture", "created_at"}, ...]
    """
    return await _call_rpc("get_ranking", {})


# =========================
# 通信
# =========================

async def _call_rpc(name, args):
    if not is_configured():
        raise RankingError("ランキングの接続先が設定されていません")

    url = f"{ranking_config.SUPABASE_URL.rstrip('/')}/rest/v1/rpc/{name}"
    body = json.dumps(args)

    if sys.platform == "emscripten":
        status, text = await _request_browser(url, _make_headers(), body)
    else:
        status, text = await asyncio.to_thread(_request_desktop, url, _make_headers(), body)

    if status == 0:
        raise RankingError("通信できませんでした")

    if not 200 <= status < 300:
        raise RankingError(f"通信に失敗しました（{status}: {_error_message(text)}）")

    return json.loads(text) if text else None


def _make_headers():
    key = ranking_config.SUPABASE_KEY

    headers = {
        "apikey": key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # 従来の anon key（JWT）は Authorization ヘッダーにも入れる。
    # 新しい publishable key（sb_publishable_...）は apikey だけでよい
    if not key.startswith("sb_"):
        headers["Authorization"] = f"Bearer {key}"

    return headers


def _error_message(text):
    try:
        return json.loads(text).get("message", text)
    except (ValueError, AttributeError):
        return text


async def _request_browser(url, headers, body):
    global _browser_ready

    import platform

    if not _browser_ready:
        platform.window.eval(_BROWSER_JS)
        _browser_ready = True

    raw = await platform.jsiter(
        platform.window.CellRanking.request(url, json.dumps(headers), body, TIMEOUT_SECONDS * 1000)
    )

    result = json.loads(raw)

    return result["status"], result["text"]


def _request_desktop(url, headers, body):
    import urllib.error
    import urllib.request

    request = urllib.request.Request(url, data=body.encode("utf-8"), headers=headers, method="POST")

    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            return response.status, response.read().decode("utf-8")

    except urllib.error.HTTPError as error:
        return error.code, error.read().decode("utf-8")

    except (urllib.error.URLError, TimeoutError, OSError):
        return 0, ""
