const API_PREFIX = "/api/v1";

type QueryValue = string | number | boolean | null | undefined;
type Query = Record<string, QueryValue> | object;

export class ApiError extends Error {
  status: number;
  detail: unknown;

  constructor(message: string, status: number, detail: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

function token(): string | null {
  return localStorage.getItem("axionara.token");
}

function buildUrl(path: string, query?: Query): string {
  const url = new URL(`${API_PREFIX}${path}`, window.location.origin);
  Object.entries(query ?? {}).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      url.searchParams.set(key, String(value));
    }
  });
  return url.pathname + url.search;
}

async function parseError(response: Response): Promise<never> {
  let detail: unknown = await response.text();
  try {
    detail = JSON.parse(String(detail));
  } catch {
    // Keep text response.
  }
  const message =
    typeof detail === "object" && detail && "detail" in detail
      ? String((detail as { detail: unknown }).detail)
      : response.statusText;
  throw new ApiError(message || "Request failed", response.status, detail);
}

async function request<T>(method: string, path: string, body?: unknown, query?: Query): Promise<T> {
  const headers = new Headers();
  const accessToken = token();
  if (accessToken) headers.set("Authorization", `Bearer ${accessToken}`);

  let payload: BodyInit | undefined;
  if (body instanceof FormData || body instanceof URLSearchParams) {
    payload = body;
  } else if (body !== undefined) {
    headers.set("Content-Type", "application/json");
    payload = JSON.stringify(body);
  }

  const response = await fetch(buildUrl(path, query), { method, headers, body: payload });
  if (!response.ok) return parseError(response);
  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

export const api = {
  get: <T>(path: string, query?: Query) => request<T>("GET", path, undefined, query),
  post: <T>(path: string, body?: unknown, query?: Query) => request<T>("POST", path, body, query),
  async download(path: string, filename: string) {
    const headers = new Headers();
    const accessToken = token();
    if (accessToken) headers.set("Authorization", `Bearer ${accessToken}`);
    const response = await fetch(buildUrl(path), { headers });
    if (!response.ok) return parseError(response);
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = filename;
    anchor.click();
    URL.revokeObjectURL(url);
  }
};
