# Pin typhonjs-escomplex
Add `"typhonjs-escomplex": "0.1.0"` (exact) to `dependencies` and regenerate the lock. The lock must pin the tree listed in the spec, §1: `@typhonjs/babel-parser` 0.2.0, `@babel/parser` 7.29.9, `typhonjs-escomplex-module`/`-project` 0.1.0, the `escomplex-plugin-*` packages 0.1.0 and `typhonjs-escomplex-commons` 0.1.1. Update the Dockerfile header comment ("the npm tools (jscpd 5.4.1, typhonjs-escomplex 0.1.0) ...").

## Files to Change
- `docker/js_complexity/package.json`: add the exact pin.
- `docker/js_complexity/package-lock.json`: regenerate.
- `docker/js_complexity/Dockerfile`: update the comment only (`lib/` is already copied).
