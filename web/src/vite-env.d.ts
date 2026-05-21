/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string;
  readonly VITE_WEB_PORT?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
