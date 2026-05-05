# Appendix 6: Configuration Reference

![U3A Logo](../img/u3a-logo.png){style="float: right; max-width: 180px; height: auto; margin: -4.5rem 0 0.5rem 1rem;"}

This appendix describes every key in `config/config.ini`.

## How configuration is loaded

- The application reads `config/config.ini`.
- If values are missing, commands fail fast with a validation or runtime error.
- Paths can be relative to the project root (recommended).

## Section: [beacon]

Settings used to authenticate and control browser behavior for Beacon CRM.

| Key | Required | Example | Description |
| --- | --- | --- | --- |
| `portal_url` | Yes | `https://u3abeacon.org.uk/password.php` | Beacon login URL. |
| `site_name` | Yes | `Petersfield` | Beacon site selector label shown after login. Must match visible Beacon text. |
| `username` | Yes | `your.username` | Beacon account username. |
| `password` | Yes | `your-password` | Beacon account password. |
| `headless` | No (default `true`) | `true` | Run browser without UI. Set `false` for troubleshooting. |

Notes:
- `headless` is parsed as boolean-like text. `false`, `0`, `no`, and `off` are treated as false.

## Section: [beacon_export]

Settings used to navigate Beacon export pages and choose output locations.

| Key | Required | Example | Description |
| --- | --- | --- | --- |
| `backup_section_link_name` | Yes | `Data export & backup` | Link text for the Beacon page that contains the full-backup download link. |
| `backup_download_link_name` | Yes | `Backup all data` | Link text for the full backup workbook download action. |
| `members_link_name` | Yes | `Members and addresses` | Link text for members export. |
| `groups_link_name` | Yes | `Groups, with members, venues` | Link text for groups export. |
| `download_dir` | Yes | `downloads` | Directory used for downloaded Beacon export files. |
| `output_dir` | Command-dependent | `outputs` | Default output directory for `export-member-names` and `export-group-data`. |
| `backup_output_dir` | Yes | `outputs` | Default destination for the full-backup workbook. Can be overridden with CLI `--output-file`. |

Notes:
- Link-name fields must match the exact visible Beacon text for your tenant.
- Use `python -m invoke playwright-record` to discover correct link values.

## Section: [database]

Optional local staging database used by sync and reprocessing workflows.

| Key | Required | Example | Description |
| --- | --- | --- | --- |
| `enabled` | No (default `false`) | `true` | Enables SQLite staging database when true. |
| `path` | When enabled | `state/beacon_data.db` | SQLite database file path. |
| `persist_across_sessions` | No (default `false`) | `false` | If true, staged rows accumulate across sync sessions. |

## Section: [wordpress]

Settings for WordPress REST API publishing.

| Key | Required | Example | Description |
| --- | --- | --- | --- |
| `site_url` | Yes (for WP commands) | `https://petersfield.u3asite.uk` | Base WordPress site URL without trailing slash. |
| `username` | Yes (for WP commands) | `wp-user` | WordPress account username. |
| `application_password` | Yes (for WP commands) | `xxxx xxxx xxxx xxxx xxxx xxxx` | WordPress application password generated from user profile. |
| `members_post_type` | No (default `post`) | `post` | Post type used for member records. |
| `groups_post_type` | No (default `post`) | `post` | Post type used for group records. |

## Security guidance

- Never commit `config/config.ini` to version control.
- Rotate Beacon and WordPress credentials if they are exposed.
- Restrict file permissions for `config/config.ini` on shared machines.

## Minimal working example

```ini
[beacon]
portal_url = https://u3abeacon.org.uk/password.php
site_name = Petersfield
username = your_beacon_username
password = your_beacon_password
headless = true

[beacon_export]
backup_section_link_name = Data export & backup
backup_download_link_name = Backup all data
members_link_name = Members and addresses
groups_link_name = Groups, with members, venues
download_dir = downloads
output_dir = outputs
backup_output_dir = outputs

[database]
enabled = false
path = state/beacon_data.db
persist_across_sessions = false

[wordpress]
site_url = https://petersfield.u3asite.uk
username = your_wp_username
application_password = xxxx xxxx xxxx xxxx xxxx xxxx
members_post_type = post
groups_post_type = post
```
