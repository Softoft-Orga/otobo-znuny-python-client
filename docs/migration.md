# Migration from the combined `otobo-znuny` client

Version 2.0 splits the monolithic client into product-specific SDKs while keeping compatibility imports.

## Recommended imports

| Before (deprecated) | After |
| --- | --- |
| `from otobo_znuny.clients.otobo_client import OTOBOZnunyClient` | `from otobo import OTOBOClient` or `from znuny import ZnunyClient` |
| `from otobo_znuny_python_client import OTOBOZnunyClient` | `from otobo import OTOBOClient` |
| `OTOBOError` | `from otobo import OTOBOError` or `from znuny import ZnunyError` |

## Compatibility window

These continue to work in 2.x but are deprecated:

- `otobo_znuny.*`
- `otobo_znuny_python_client.*`
- Combined CLI command `setup-otobo-znuny-system`

## CLI changes

| Legacy | New |
| --- | --- |
| Combined auto-detect CLI | `otobo-cli` or `znuny-cli` |
| `setup-otobo-znuny-system` | `otobo-cli setup-system` / `znuny-cli setup-system` |

## Shared internals

REST models, mappers, and the async client implementation moved to `otrs_gi_core`. Application code should not import `otrs_gi_core` directly unless you maintain connector code.
