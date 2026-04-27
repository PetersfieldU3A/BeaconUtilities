# Project Overview

![U3A Logo](img/u3a-logo.png){style="float: right; max-width: 180px; height: auto; margin: -4.5rem 0 0.5rem 1rem;"}

## Purpose

To programmatically access Beacon, the U3A CRM, and use that data to automatically populate pages on the Petersfield U3A WordPress website. As Beacon does not provide a user-accessible API, Playwright browser automation is used to mimic user interaction.

## Core Objectives

1. **Beacon Automation** — Use Playwright to log in to Beacon and retrieve member, group, and event data.
2. **WordPress Integration** — Publish or update WordPress pages and posts via the WordPress REST API using data retrieved from Beacon.
3. **Reliability** — Robust error handling and logging so failures are visible and recoverable.
4. **Cross-Platform Compatibility** — Operate on Windows 11 and macOS.

## System Architecture

### Components

- **Beacon Portal + Playwright** — Automates browser login and data extraction from the Beacon CRM.
- **Integration Application** — Python CLI handling scraping, transformation, and publishing.
- **WordPress REST API** — Receives structured content for page/post creation and updates.

### Workflow

1. Authenticate with Beacon via Playwright.
2. Scrape required data (members, groups, events, etc.).
3. Map Beacon data to WordPress content structures.
4. POST or PUT content to the WordPress REST API.
5. Log results and update run state.
