#!/usr/bin/env python3
"""Invites commenters with the code word on the access issue to the private repo.

Runs once per invocation (systemd timer). Reads:
  /etc/daic-invite/token  GitHub token of the repo owner
  /etc/daic-invite/code   code word
State (last processed comment id): /var/lib/daic-invite/state.json
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

DOOR = "b0nduel/daic-brand-join"
TARGET = "b0nduel/daic-brand"
OWNER = "b0nduel"
ISSUE = 1
ETC = "/etc/daic-invite"
STATE = "/var/lib/daic-invite/state.json"


def read(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""


TOKEN = read(f"{ETC}/token")
CODE = read(f"{ETC}/code").lower()


def api(method, path, body=None, tries=4):
    for i in range(tries):
        try:
            return _api(method, path, body)
        except urllib.error.HTTPError:
            raise
        except (urllib.error.URLError, TimeoutError, OSError):
            if i == tries - 1:
                raise
            time.sleep(3)


def _api(method, path, body=None):
    req = urllib.request.Request(
        "https://api.github.com" + path,
        method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "daic-invite",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        raw = r.read()
        return json.loads(raw) if raw else None


def reply(text):
    api("POST", f"/repos/{DOOR}/issues/{ISSUE}/comments", {"body": text})


def main():
    if not TOKEN or not CODE:
        print("token or code missing, skipping")
        return
    try:
        state = json.loads(read(STATE) or "{}")
    except ValueError:
        state = {}
    last = state.get("last_id", 0)

    comments, page = [], 1
    while True:
        batch = api("GET", f"/repos/{DOOR}/issues/{ISSUE}/comments?per_page=100&page={page}")
        comments += batch
        if len(batch) < 100:
            break
        page += 1
    try:
        for c in sorted(comments, key=lambda c: c["id"]):
            if c["id"] <= last:
                continue
            user = c["user"]
            login = user["login"]
            if login != OWNER and user.get("type") == "User":
                handle(c, login)
            # A comment counts as processed only after every step for it succeeded,
            # so a network failure mid-way retries it on the next run.
            last = c["id"]
    finally:
        os.makedirs(os.path.dirname(STATE), exist_ok=True)
        with open(STATE, "w") as f:
            json.dump({"last_id": last}, f)


def handle(c, login):
    if CODE not in (c.get("body") or "").lower():
        delete(c)
        reply(f"@{login} кодовое слово не подошло. Уточните его у того, кто дал ссылку, и напишите комментарий ещё раз.")
        print(f"{login}: wrong code")
        return
    try:
        api("PUT", f"/repos/{TARGET}/collaborators/{login}", {"permission": "push"})
    except urllib.error.HTTPError as e:
        delete(c)
        reply(f"@{login} не получилось отправить приглашение (ошибка {e.code}). Напишите владельцу репозитория.")
        print(f"{login}: invite failed {e.code}")
        return
    delete(c)
    reply(
        f"@{login} приглашение отправлено. Примите его: https://github.com/{TARGET}/invitations\n"
        f"Дальше — инструкция в README: https://github.com/{DOOR}#readme"
    )
    print(f"{login}: invited")


def delete(c):
    try:
        api("DELETE", f"/repos/{DOOR}/issues/comments/{c['id']}")
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise


if __name__ == "__main__":
    try:
        main()
    except urllib.error.HTTPError as e:
        print(f"GitHub API error {e.code}: {e.read()[:300]!r}", file=sys.stderr)
        sys.exit(1)
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        print(f"network error, will retry next run: {e}", file=sys.stderr)
        sys.exit(1)
