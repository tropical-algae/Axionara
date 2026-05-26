<!-- version list -->

## v0.0.1 (2026-05-26)

### Bug Fixes

- Add socks proxy support for http clients
  ([`41f5fb3`](https://github.com/tropical-algae/Axionara/commit/41f5fb3029abad8372c72f2cb0543585a79a8d13))

- **config**: Provide sqlite cache database default for containerized deployments without external
  settings
  ([`3e7694c`](https://github.com/tropical-algae/Axionara/commit/3e7694c82cb4e90f5bd7871f93ea1d28521661d6))

- **web**: Read backend error messages
  ([`437075e`](https://github.com/tropical-algae/Axionara/commit/437075ec9062bb7d148ba6619a5cc978e5fbba87))

- **web**: Update service modules to call explicit versioned backend API endpoint paths
  ([`a034df4`](https://github.com/tropical-algae/Axionara/commit/a034df40ed48ef19daf8d9566f901776f395df9f))

### Chores

- Add alembic migration baseline
  ([`e6fda8f`](https://github.com/tropical-algae/Axionara/commit/e6fda8f2c193b18c80e09d7ae0065ec3037d7e93))

- **web**: Configure Vite environment variables for API routing and development ports
  ([`f00db65`](https://github.com/tropical-algae/Axionara/commit/f00db651dbfd02f1340355911a26334ae753de37))

- **web**: Scaffold vite frontend
  ([`36c9b4c`](https://github.com/tropical-algae/Axionara/commit/36c9b4c1a5c992dcd7852131b6013164d133e8ad))

### Features

- Add admin dataset job queries
  ([`dc8e072`](https://github.com/tropical-algae/Axionara/commit/dc8e0720c3e11ea1dbf35d2f238a47a3ad75061e))

- Add authorized content qa
  ([`e20d052`](https://github.com/tropical-algae/Axionara/commit/e20d0524c9ebe2cc20d96b2bd0e6cc8cbe863d50))

- Add dataset export jobs
  ([`14c6906`](https://github.com/tropical-algae/Axionara/commit/14c690691c819925476aa8940384d201c4097a12))

- Add job retry endpoints
  ([`e5f2d88`](https://github.com/tropical-algae/Axionara/commit/e5f2d88e63dde9b642566bfff5076dcf4d600241))

- Add optional llm analysis summaries
  ([`3944f2e`](https://github.com/tropical-algae/Axionara/commit/3944f2ea5586cc238e9a3f5fc1c55f811e7848f5))

- Add public catalog rag qa
  ([`fd0df47`](https://github.com/tropical-algae/Axionara/commit/fd0df47993c0f577c1c8f20367be78588006803d))

- Add review audit archive flow
  ([`1462515`](https://github.com/tropical-algae/Axionara/commit/14625151c39e8a9c2bc08a5473e7fd4817ae44f9))

- Add storage health checks
  ([`cfb46a3`](https://github.com/tropical-algae/Axionara/commit/cfb46a37a1006fc16ed009182969469d54df77f9))

- Enhance tabular cleaning statistics
  ([`8c95dfb`](https://github.com/tropical-algae/Axionara/commit/8c95dfb9e779d4fc1807981cd968c445b825d1fb))

- Extract document text with markitdown
  ([`470e243`](https://github.com/tropical-algae/Axionara/commit/470e24333520c8c79ac662cada806b9bf96fdb53))

- Implement dataset lifecycle workflow
  ([`63aa771`](https://github.com/tropical-algae/Axionara/commit/63aa771ded0bf143f99f5253c76ba30897b70caa))

- Load agent prompts from markdown files
  ([`2ef2b29`](https://github.com/tropical-algae/Axionara/commit/2ef2b29705588b7c34804bfdfafb641895348a60))

- Support sql script uploads
  ([`4fab479`](https://github.com/tropical-algae/Axionara/commit/4fab4794faabd64a41d8de2b56d055e9b414f5d2))

- Support xlsx analysis export
  ([`fcc9952`](https://github.com/tropical-algae/Axionara/commit/fcc99524dad4c71bb72ceb2f883d5a04afdaf3c2))

- **agent**: Add authorized content qa tool
  ([`a8241df`](https://github.com/tropical-algae/Axionara/commit/a8241dfe2b3f5282ed8391ccb417e41160139988))

- **agent**: Add dataset qa prompt templates
  ([`af40a74`](https://github.com/tropical-algae/Axionara/commit/af40a741ae05259268305b395721986968b4aa85))

- **agent**: Add public dataset qa tools
  ([`8e14666`](https://github.com/tropical-algae/Axionara/commit/8e146668a9e17bb2112b7bfcbd508e74a5a228f1))

- **agent**: Run dataset qa through inference service
  ([`35781de`](https://github.com/tropical-algae/Axionara/commit/35781de838fa30cf8e44215b088b6f689fe87301))

- **agent**: Support named agent instances
  ([`18ec234`](https://github.com/tropical-algae/Axionara/commit/18ec23417afaaf363599aa29cab587c4091c5997))

- **api**: Accept upload governance fields
  ([`0fda5c3`](https://github.com/tropical-algae/Axionara/commit/0fda5c33f404d4055984a6fe9eec75939d7ae913))

- **api**: Add dataset qa retrieval services
  ([`dea96e0`](https://github.com/tropical-algae/Axionara/commit/dea96e08630b9172182f35fb8cdba167fa0a1663))

- **api**: Route ask endpoints through dataset qa agent
  ([`781c4a4`](https://github.com/tropical-algae/Axionara/commit/781c4a467345f9d1e0cf705f01107631a6db2618))

- **db**: Add dataset governance metadata
  ([`7b5f164`](https://github.com/tropical-algae/Axionara/commit/7b5f164f51254b3c20ca27a960a2210d9279861f))

- **deploy**: Package frontend assets prompts nginx proxy and cache directories in image
  ([`bf7e2b3`](https://github.com/tropical-algae/Axionara/commit/bf7e2b3a68769f15712695d9b4dd74fca0afa8a0))

- **init**: Init project
  ([`bf4aa25`](https://github.com/tropical-algae/Axionara/commit/bf4aa256228388839d92349a38c84f3c39362b4e))

- **web**: Add admin operations views
  ([`d7c9a5d`](https://github.com/tropical-algae/Axionara/commit/d7c9a5d3d86de2ebf7af982b685828047a72049b))

- **web**: Add application stores
  ([`5981f64`](https://github.com/tropical-algae/Axionara/commit/5981f645e31b1bf0c31bdf71a010a33ec9cac5dc))

- **web**: Add consumer data workspace
  ([`2ff9c87`](https://github.com/tropical-algae/Axionara/commit/2ff9c874ee5bc1fed0ec60ec8deac14135451d95))

- **web**: Add data marketplace views
  ([`259e546`](https://github.com/tropical-algae/Axionara/commit/259e546f23ecf90c1df3d775b3c131d31ebcb697))

- **web**: Add home and auth pages
  ([`e4439f1`](https://github.com/tropical-algae/Axionara/commit/e4439f1d4ddaf35d9d36ea4e49fd9bd762bda954))

- **web**: Add persistent threejs backdrop
  ([`055d488`](https://github.com/tropical-algae/Axionara/commit/055d4888e05447353dcaae7726f4797e5254bfb4))

- **web**: Add provider upload workspace
  ([`1a0e178`](https://github.com/tropical-algae/Axionara/commit/1a0e17800039c1f9c02df385ac1cca3b95e2d8cd))

- **web**: Add shell and shared UI
  ([`1c6ad81`](https://github.com/tropical-algae/Axionara/commit/1c6ad811301fb38135d639c33d1859506fda7385))

- **web**: Add typed API client
  ([`c243c45`](https://github.com/tropical-algae/Axionara/commit/c243c45148e0f75bb1a80dc2f2250c22efa662d6))

- **web**: Wire app routing and transitions
  ([`d0805af`](https://github.com/tropical-algae/Axionara/commit/d0805af5800b0fc86d75a167547e9db1ebb4461f))

### Performance Improvements

- **web**: Smooth copilot drawer transitions
  ([`fb81336`](https://github.com/tropical-algae/Axionara/commit/fb8133656982a67af68e3157464b7363f6e51137))

### Refactoring

- **web**: Replace fetch request layer with typed axios client and normalized errors
  ([`54df9bc`](https://github.com/tropical-algae/Axionara/commit/54df9bc92c28cd746d497c1e4c7d51093ebdb028))

### Testing

- Isolate pytest database and storage
  ([`8d70fd7`](https://github.com/tropical-algae/Axionara/commit/8d70fd7384768c13e40cd4f9495d1cd9c747bf40))

- **api**: Cover uploaded asset metadata
  ([`669e627`](https://github.com/tropical-algae/Axionara/commit/669e627c353abb6553c9f5a681c246fe7a109d06))

- **api**: Mock dataset qa agent tool calls
  ([`57f15e9`](https://github.com/tropical-algae/Axionara/commit/57f15e9e769dca05e518a7d521ed6b56714a5709))
