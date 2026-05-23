# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v1.0.2] - 2026-05-23

### Added
- Load API credentials from a `.env` file via `python-dotenv`; raise a clear error at startup if any are missing
- Add `.env.example` as a setup template

### Fixed
- Replace unmaintained `fuzzywuzzy` with `rapidfuzz` (compatible API, significantly faster)
- Suppress Google API discovery cache deprecation warning in `google-api-python-client` 2.x

### Security
- Bump `google-api-python-client` 1.12.8 → 2.196.0
- Bump `google-api-core` 1.23.0 → 2.30.3
- Bump `google-auth` 1.23.0 → 2.53.0
- Bump `google-auth-httplib2` 0.0.4 → 0.4.0
- Bump `googleapis-common-protos` 1.52.0 → 1.75.0
- Bump `uritemplate` 3.0.1 → 4.2.0

## [v1.0.1] - 2026-05-22

### Fixed
- Replace abandoned `youtube-dl` with maintained `yt-dlp` fork, resolving RCE vulnerability (Dependabot alert #61)
- Fix audio filename extension stripping to handle any source format, not just `.webm`
- Fix `Image.ANTIALIAS` usage removed in Pillow 10 — replaced with `Image.LANCZOS`
- Fix broken `user_settings.txt` parsing (missing quotes, syntax error, undefined variable)
- Fix output directory falling back to `~/Music` when not set in `user_settings.txt`

### Security
- Bump `Pillow` 8.0.1 → 12.2.0 (28 CVEs resolved, including CRITICAL arbitrary code execution CVE-2023-50447)
- Bump `urllib3` 1.26.2 → 2.7.0 (8 CVEs resolved, including HIGH decompression-bomb bypasses)
- Bump `protobuf` 3.14.0 → 7.35.0 (3 CVEs resolved)
- Bump `requests` 2.25.0 → 2.34.2 (3 CVEs resolved)
- Bump `spotipy` 2.16.1 → 2.26.0 (XSS, auth token permissions, path traversal CVEs resolved)
- Bump `pyinstaller` 4.1 → 6.20.0 (2 local privilege escalation CVEs resolved)
- Bump `pyasn1` 0.4.8 → 0.6.3 (unbounded recursion DoS resolved)
- Bump `idna` 2.10 → 3.16 (2 DoS CVEs resolved)
- Bump `rsa` 4.6 → 4.9.1 (timing attack CVE-2020-25658 resolved)
- Bump `certifi` 2020.11.8 → 2026.5.20 (stale root certificates resolved)
- Bump `future` 0.18.2 → 1.0.0 (DoS CVE-2022-40899 resolved)
- Bump `httplib2` 0.18.1 → 0.31.2 (ReDoS CVE-2021-21240 resolved)
- Bump `pyasn1-modules` 0.2.8 → 0.4.2
- Bump `pyinstaller-hooks-contrib` 2020.10 → 2026.5
- Remove unused `pafy` dependency

[v1.0.2]: https://github.com/wiraszka/music-downloader/releases/tag/v1.0.2
[v1.0.1]: https://github.com/wiraszka/music-downloader/releases/tag/v1.0.1
