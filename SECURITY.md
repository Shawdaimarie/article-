# Security Policy

## Reporting a Vulnerability

If you find a security issue in Article (the CLI, the backend API, or the
charter itself), please report it privately rather than opening a public
issue:

- Open a [GitHub Security Advisory](https://github.com/Shawdaimarie/article-/security/advisories/new)
  for this repository, **or**
- Email the maintainer listed on the [GitHub profile](https://github.com/Shawdaimarie)
  with a description of the issue and, if possible, steps to reproduce it.

We aim to acknowledge reports within 5 business days.

## Supported Versions

Article follows semantic versioning. Only the latest minor release on the
current major version receives security fixes.

| Version | Supported |
| ------- | --------- |
| 1.x     | Yes       |

## Scope

- The `article` CLI only ever *reads* files in the target project — it does
  not execute code from the project it is checking.
- The backend API stores only what a caller explicitly submits to `/runs`
  (a project name and a set of check results). It does not accept or execute
  arbitrary code.
