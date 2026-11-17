# Lichtblick

This folder is a build of [Lichtblick](https://github.com/lichtblick-suite/lichtblick) v1.31.0 (commit a6c0f86d7e050132df0f0b3717ad5f3ea917bafb),
licensed under the Mozilla Public License 2.0 (`LICENSE.txt`). Its source is at that link. The changes, all in
`lichtblick-static-loaders.patch`:

- the app loads panels and layouts shipped beside it in `static/` (new file `StaticSiteLoaders.ts`, and a
  `layoutLoaders` option passed from `WebRoot.tsx` through `SharedRoot` to `StudioApp`);
- an asset URL relative to the page, such as the car model, resolves against the page (`MessagePipeline/store.ts`);
- the left sidebar starts closed, and the launch-preference screen is off (`WorkspaceContextProvider.tsx`, `WebRoot.tsx`).

`static/errol-vehicle-controls.foxe` holds the Errol Vehicle Controls panels (MIT). `data/lexus.glb` is derived
from the Lexus model in Autoware's sample_vehicle (Apache-2.0).
