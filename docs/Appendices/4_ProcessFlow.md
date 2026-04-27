# Appendix 4: Application Process Flow

![U3A Logo](../img/u3a-logo.png){style="float: right; max-width: 180px; height: auto; margin: -4.5rem 0 0.5rem 1rem;"}

Process flow diagrams will be added here as the application workflows are defined.

## Diagram 1: Overview (placeholder)

```mermaid
%%{init: {"themeVariables": {"fontSize": "18px"}}}%%
graph TD
    A[Start Sync Command] --> B[Load config.ini]
    B --> C[Preflight checks]
    C --> D[Login to Beacon via Playwright]
    D --> E[Extract data from Beacon]
    E --> F[Map to WordPress content]
    F --> G[POST/PUT to WordPress REST API]
    G --> H[Log results and update state]
    H --> I[End]
```
