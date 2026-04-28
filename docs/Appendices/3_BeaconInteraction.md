# Appendix 3: Beacon Interaction

![U3A Logo](../img/u3a-logo.png){style="float: right; max-width: 180px; height: auto; margin: -4.5rem 0 0.5rem 1rem;"}

This appendix documents the current Playwright automation path used to authenticate to Beacon and download the Members and Groups exports.

## Runtime Preconditions

The Beacon automation expects the following configuration values:

- `[beacon] portal_url`
- `[beacon] site_name`
- `[beacon] username`
- `[beacon] password`
- `[beacon_export] members_link_name`
- `[beacon_export] groups_link_name`
- `[beacon_export] download_dir`

If `site_name` or either export link name is missing, the run fails with a clear configuration error before attempting extraction.

## Login Flow

The automated login sequence is:

1. Open Beacon login page from `portal_url`.
2. Accept optional cookies if the consent button appears.
3. Open the site selector and choose `site_name`.
4. Fill username and password fields.
5. Click Enter and wait for the page to settle.
6. Detect login failure by checking whether the final URL still looks like a login page.

On failure, the process raises a login error asking the operator to verify credentials and site name.

## Data Extraction Flow

For each sync run, extraction is performed in this order:

1. Navigate to `Data export & backup`.
2. Click the `members_link_name` link and capture the download as `members.xlsx`.
3. Return to Home.
4. Navigate again to `Data export & backup`.
5. Click the `groups_link_name` link and capture the download as `groups.xlsx`.
6. Return to Home and attempt logout.

Download handling details:

- Browser context is created with downloads enabled.
- Each download waits up to 60 seconds.
- Failed downloads raise an explicit runtime error.
- Files are saved into `beacon_export.download_dir`.

## Discovering Link Names

Link names must match Beacon link text exactly. For each organisation, confirm values using recorder mode:

```bash
python -m invoke playwright-record
```

Then navigate manually to `Data export & backup` and record the exact Members and Groups link labels in `config/config.ini`.

## Known Portal Quirks

Observed and handled quirks:

- Cookie consent banner is intermittent; automation treats it as optional.
- Site selector uses Select2 search; site must be selected before credentials are submitted.
- Export links are organisation-specific labels and can change over time.
- Logout may occasionally fail due to timing or page state; this is non-fatal because session expiry is sufficient.

## Operational Notes

- Run dry-run first in a new environment to validate login and extraction without WordPress writes.
- Keep Beacon credentials out of version control.
- If login suddenly starts failing, first re-check `site_name` and export link labels in Beacon.
