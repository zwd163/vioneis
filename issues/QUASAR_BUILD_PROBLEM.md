# Frontend Build Error Solution

## Problem Description
When building the frontend using `quasar build`, encountered crypto error:
```
Error: error:0308010C:digital envelope routines::unsupported
```

## Root Cause
This error occurs because Node.js 17+ uses OpenSSL 3.0, which removed support for older algorithms used by webpack 4.

## Solution
Set the Node.js environment variable to enable legacy OpenSSL provider before running build:

```powershell
$env:NODE_OPTIONS="--openssl-legacy-provider"
quasar build --verbose
```

## Alternative Solutions
1. Downgrade Node.js to v16.x
2. Update webpack and related dependencies

## Verification
After applying the solution:
1. The build completes successfully
2. `dist/spa/index.html` is generated correctly
3. All static assets are properly bundled

## Related Files
- `templates/src/index.template.html`
- `templates/dist/spa/index.html`

## References
- [Node.js OpenSSL Changes](https://github.com/nodejs/node/issues/40455)
- [Webpack Issue #14532](https://github.com/webpack/webpack/issues/14532)