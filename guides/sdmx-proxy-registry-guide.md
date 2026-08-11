# Configuring SDMX Registries on a Proxy Data Source

This document covers the `proxyConfig` block of a `PROXY_SDMX30` data source — the **registries** the StatGPT SDMX
Proxy fronts, the **per-registry query settings** that make each one answer correctly, and the **agency routing** that
decides which registry serves which agency.

A `PROXY_SDMX30` data source points at the proxy instead of connecting to a registry directly. It is the recommended
connector: one data source covers many providers, and new registries are added by editing `proxyConfig` from the Admin
Portal.

> This guide covers the settings you need to add a registry and get correct answers out of it. The
> [full field reference](https://github.com/epam/statgpt-sdmx-proxy/blob/development/sdmx-proxy-config/README.md) lists
> every field. This guide extends the [Administrator Guide](./admin-guide.md#adding-a-data-source), which covers adding
> and editing the data source itself.

## Table of Contents

- [The model](#the-model)
- [Adding a registry](#adding-a-registry)
  - [Minimum block](#minimum-block)
- [Registry compatibility settings](#registry-compatibility-settings)
- [Fixtures](#fixtures)
- [Formats](#formats)
- [Resilience](#resilience)
- [Operational notes](#operational-notes)
- [Full field reference](#full-field-reference)
- [Related resources](#related-resources)


## The model

The configuration has three levels:

1. **Data source** (`PROXY_SDMX30`) — StatGPT's handle on the proxy. `sdmxConfig.url` points at the proxy.
2. **Registries** (`proxyConfig.configs`) — one entry per upstream API. Each is configured per SDMX version, because a
   registry can behave differently on its 2.1 and 3.0 endpoints. A version configures up to three endpoints —
   structure, data, availability.
3. **Agency routing** (`proxyConfig.agencies`) — which registry answers for an agency ID as it appears in SDMX URLs.
   `primaryRegistry` names the registry. `allowSubAgencies: true` extends it to dot-separated descendants, so `IMF.STA`
   is served by the registry configured for `IMF`.

**Routing is explicit.** An agency with no `agencies` entry is rejected, even if a registry of the same name exists. A
registry in `configs` with no agency entry is unreachable.

**`structureFanOutEnabled` is a root-level switch.** When true, a structure query that names no agency (`agencyID=*`)
is sent to every registry that supports the requested structure type and the results are merged. When false, that query
is rejected. A comma-separated list of agencies (`agencyID=BIS,IMF`) is rejected either way. The schema default is
`false`; the configuration shipped with the proxy sets it to `true`.

---

## Adding a registry

### Minimum block

The IMF entry from the shipped configuration:

```yaml
proxyConfig:
  configs:
    - name: IMF                        # routing key; must match agencies[].primaryRegistry
      description: International Monetary Fund
      versions:
        SDMX_3_0:                      # or SDMX_2_1 — key and sdmxVersion must agree
          sdmxVersion: SDMX_3_0
          structureEndpointConfig:
            url: https://api.imf.org/external/sdmx/3.0/structure/
            supportedFormats: [JSON_STRUCTURE_2_0_0]
            defaultFormat: JSON_STRUCTURE_2_0_0
            supportedStructures:       # unset: every structure query is rejected
              - datastructure
              - conceptscheme
              - codelist
              - dataflow
              - hierarchy
              - hierarchyassociation
              - metadatastructure
              - metadataflow
              - metadataprovisionagreement
          dataEndpointConfig:
            url: https://api.imf.org/external/sdmx/3.0/data/
            supportedFormats: [JSON_DATA_2_0_0, CSV_DATA_2_0_0]
            defaultFormat: JSON_DATA_2_0_0
            replaceEmptyDimensionsWithWildcard: true   # IMF wants explicit wildcards in a key
          availabilityEndpointConfig:
            url: https://api.imf.org/external/sdmx/3.0/availability/
            supportedFormats: [JSON_STRUCTURE_2_0_0]
            defaultFormat: JSON_STRUCTURE_2_0_0
            availabilityEnabled: true  # unset: availability queries are rejected
          # per-endpoint `fixtures` and `resilienceConfig` omitted here — see the sections below
  agencies:
    - name: IMF                        # agency ID as it appears in SDMX URLs
      primaryRegistry: IMF             # without this entry the registry is unreachable
      allowSubAgencies: true           # IMF.STA, IMF.RES, ... route here too
```

**Four things to set explicitly:**

- **An `agencies` entry** — without one the registry serves nothing.
- **`supportedStructures`** — structure types outside this set are rejected. Unset means the empty set, so every
  structure query fails. Values used in the shipped configuration: `agencyscheme`, `categoryscheme`, `codelist`,
  `conceptscheme`, `dataflow`, `datastructure`, `hierarchy`, `hierarchyassociation`, `metadataflow`,
  `metadataprovisionagreement`, `metadatastructure`.
- **`availabilityEnabled`** — defaults to `false`. Availability is used in dataset onboarding and querying, so leaving it off makes the registry unusable.
- **`defaultFormat`** — the format requested from the registry.

---

## Registry compatibility settings

The settings below let the proxy adapt a request to what a particular registry expects.

| Symptom | Setting | Endpoint |
|---------|---------|----------|
| A key with empty positions (`..L_T.P_F3`) returns nothing, while explicit wildcards work | `replaceEmptyDimensionsWithWildcard: true` | data |
| A key of all wildcards (`*.*.*.*`) returns an empty response, while a single `*` works | `mergeAllWildcardKey: true` | data, availability |
| Availability expects the dimensions listed rather than `*` as the component ID | `unwrapStarComponentId: true` | availability |
| Narrowing a query barely changes the result, and availability queries get slow | `convertKeyToFilters: true` | data, availability |
| The `limit` parameter has no effect, so broad queries return everything | `supportsLimit: false` | data |
| Availability filters return nothing, while the registry answers the same filters expressed another way | `unwrapFilterParameters: true` | availability |

`unwrapFilterParameters` is not needed by any registry in the shipped configuration — `convertKeyToFilters` is the
better fit for the one case where it might apply.

> **⚠️ SDMX 3.0 only.** `convertKeyToFilters` and `unwrapStarComponentId` apply to SDMX 3.0 only. Setting either inside
> an `SDMX_2_1` block makes the configuration invalid, and the save is rejected.

**Emulating `limit`.** `supportsLimit: false` lets the proxy cap the response size itself. Two settings tune that:
`limitEmulationTolerance` (default `1.2`, range `1.0`–`10.0`) allows the result to overshoot the requested limit by that
factor, and `limitEmulationProbeBudget` (default `8`, range `1`–`64`) limits how much work goes into hitting it. Raising
the budget slows every request.

---

## Fixtures

Where a registry's response differs from what StatGPT expects, a fixture adjusts it on the way through. Add one when
the matching symptom appears. Each is scoped to an endpoint, and several can be listed for the same endpoint.

| Endpoint | Type | Adjusts |
|----------|------|---------|
| structure | `DSD_ATTRIBUTE_ATTACHMENT_LEVEL` | Attribute attachment levels on a data structure |
| structure | `VERSION_WILDCARD` | Wildcard versions in structure responses |
| structure | `ANNOTATION_VALUE_TO_TEXT` | Annotation values that would otherwise not reach StatGPT |
| structure | `PRESERVE_METADATA_ATTRIBUTE_USAGES` | Metadata attribute usages on a data structure |
| availability | `MOVE_CUBE_REGION_COMPONENTS_TO_KEY_VALUES` | Where components appear in an availability response |
| data | `TIME_PERIOD_MONTHLY_NORMALIZATION` | Monthly periods returned as `2024-03` into the `2024-M03` form StatGPT uses to recognise monthly data |
| data | `PRESERVE_METADATA_ATTRIBUTES` | Metadata attribute values in data responses |

---

## Formats

Each endpoint declares which formats the registry can return (`supportedFormats`) and which one to ask it for
(`defaultFormat`). The proxy converts the response to whatever the client asked for. The
[reference](https://github.com/epam/statgpt-sdmx-proxy/blob/development/sdmx-proxy-config/README.md#enum-sdmxformat)
lists the available format values.

`bypassEnabled` is off by default, and every shipped registry leaves it off. Turning it on lets a response go straight
to the client whenever the registry already returns the requested format. That is faster, but such a response keeps any
defects the [fixtures](#fixtures) above would have corrected.

---

## Resilience

`resilienceConfig` is set per registry per version. All durations are in milliseconds; connect and read timeouts default
to `30000`. Four independent blocks sit below it:

- **`circuitBreaker`** — pause calls to a registry that is not responding, and resume after a wait.
- **`retry`** — server and network errors.
- **`rateLimit`** — cap outbound requests.
- **`rateLimitRetry`** — wait and retry when a registry answers "too many requests".

---

## Operational notes

**`rateLimitRetry` changes need a proxy restart** before they take effect. Every other setting applies without one.

---

## Full field reference

Every field, with required/default/allowed values, is maintained next to the code by the proxy team:

- [Registry configuration schema](https://github.com/epam/statgpt-sdmx-proxy/blob/development/sdmx-proxy-config/README.md)
  — registries, per-version and per-endpoint settings, resilience, agencies, fixtures, and formats.
- [Config server](https://github.com/epam/statgpt-sdmx-proxy/blob/development/sdmx-proxy-config-server/README.md)
  — storage backends, environment variables, and the forced-reseed flow.

---

## Related resources

- [Administrator Guide](./admin-guide.md#adding-a-data-source) — adding and editing data sources, datasets, channels.
- [Module 05 — Data Sources & Channel Configuration](../learning/administration/05-data-sources-and-channels.md) — data
  source configuration in the onboarding course.
- [Services](../architecture/services.md#-statgpt-sdmx-proxy) — where the proxy and its config server sit.
- [SDMX Compatibility & Requirements](../architecture/sdmx-compatibility.md) — what an upstream registry must provide.
- [statgpt-sdmx-proxy](https://github.com/epam/statgpt-sdmx-proxy) — the proxy itself.
