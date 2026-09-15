# Privacy

Article is built to respect the same privacy principle it checks for in
other projects, so here is exactly what each piece does and does not
collect.

## The CLI (`article check`)

Runs entirely on your machine. It reads files under the path you give it and
prints or writes results locally. It does **not** phone home, does not
collect personal data, and makes no network request at all — unless you pass
`--report-url`.

## The backend API (opt-in, via `--report-url`)

If you choose to report a run, the CLI sends exactly this to the backend:

- the **project name** you provide (defaults to a directory name),
- the **charter name and version** that was run,
- the **score and per-principle results** (status + short message),
- a **server-generated timestamp**.

It does not collect: file contents, source code, IP addresses beyond normal
HTTP server logs, cookies, or any user-identifying information. There is no
tracking, no analytics, and no third-party data sharing. Deleting a self-hosted
backend's database deletes all of the above.

## Your own deployment

If you self-host the backend (see [`render.yaml`](render.yaml)), you control
the database entirely; this policy describes the reference implementation's
behavior, not a hosted service operated on your behalf.
