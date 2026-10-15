# Доступ к daic-brand

Здесь выдают доступ к приватному репозиторию `b0nduel/daic-brand` с контекстом бренда DAIC.

## Как получить доступ

1. Откройте задачу с меткой **access**: [«Получить доступ к daic-brand»](https://github.com/b0nduel/daic-brand-join/issues?q=is%3Aissue+label%3Aaccess).
2. Оставьте комментарий с **кодовым словом**. Слово сообщает тот, кто дал вам ссылку.
   Бот сразу удалит комментарий, чтобы слово не оставалось на виду.
3. Через минуту на GitHub придёт приглашение. Примите его: https://github.com/b0nduel/daic-brand/invitations
4. Готово. У вас есть право создавать свои ветки в `daic-brand`.

## Как загрузить контекст

```bash
git clone https://github.com/b0nduel/daic-brand.git
cd daic-brand
git checkout -b context/<ваш-ник>-<тема>
mkdir -p context/<ваш-ник>-<тема>
cp context/_template/CONTEXT.md context/<ваш-ник>-<тема>/CONTEXT.md
# заполните CONTEXT.md, добавьте свои файлы
git add context/<ваш-ник>-<тема>
git commit -m "context: <ник> — <тема>"
git push -u origin context/<ваш-ник>-<тема>
```

Правила:
- Работайте только в своей ветке и своей папке.
- Не меняйте `main`, `context/main/` и чужие папки.
- Если что-то нужно влить в общий контекст, откройте Pull Request.

## Инструкция для ИИ-агента (Claude Code, Codex, Cursor…)

Нужен `gh`, авторизованный под вашим GitHub-аккаунтом (`gh auth login`).

> 1. Получи доступ: `gh issue list -R b0nduel/daic-brand-join -l access` — найди номер задачи, затем
>    `gh issue comment <номер> -R b0nduel/daic-brand-join --body "<кодовое слово>"`.
> 2. Подожди ~1 минуту и прими приглашение:
>    `gh api user/repository_invitations --jq '.[] | select(.repository.full_name=="b0nduel/daic-brand") | .id'`, затем
>    `gh api -X PATCH user/repository_invitations/<id>`.
> 3. `gh repo clone b0nduel/daic-brand`, прочитай `README.md`, `CONTRIBUTING.md` и `context/main/BRIEF.md`.
> 4. Создай ветку `context/<ник>-<тема>`, сохрани итог нашей работы в `context/<ник>-<тема>/CONTEXT.md` по шаблону `context/_template/CONTEXT.md` (плюс полезные файлы), закоммить и запушь эту ветку. `main` не трогай.
