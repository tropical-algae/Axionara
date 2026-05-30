import axios, {
  type AxiosError,
  type AxiosRequestConfig,
  type AxiosResponse,
  type InternalAxiosRequestConfig
} from "axios";

interface BackendErrorResponse {
  status?: number | string;
  message?: string;
  detail?: string;
  data?: unknown;
}

export interface RequestConfig<Data = unknown> extends AxiosRequestConfig<Data> {
  suppressErrorToast?: boolean;
}

export interface RequestError {
  status: number | string;
  message: string;
  raw: unknown;
  response?: BackendErrorResponse;
}

type RequestErrorHandler = (error: RequestError) => void;

let requestErrorHandler: RequestErrorHandler | null = null;

export class ApiError extends Error {
  status: number | string;
  detail: unknown;

  constructor(message: string, status: number | string, detail: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

function normalizeBaseUrl(baseUrl: string): string {
  const normalized = baseUrl.trim();
  if (!normalized || normalized === "/") return "/";
  return normalized.replace(/\/+$/, "");
}

function token(): string | null {
  return localStorage.getItem("axionara.token");
}

function isBackendErrorResponse(value: unknown): value is BackendErrorResponse {
  return Boolean(value && typeof value === "object" && ("message" in value || "detail" in value || "status" in value));
}

export const setRequestErrorHandler = (handler: RequestErrorHandler | null) => {
  requestErrorHandler = handler;
};

export const normalizeRequestError = (error: unknown): RequestError => {
  if (!axios.isAxiosError(error)) {
    return {
      status: "UNKNOWN",
      message: error instanceof Error ? error.message : "Request failed",
      raw: error
    };
  }

  const axiosError = error as AxiosError<BackendErrorResponse>;
  const response = isBackendErrorResponse(axiosError.response?.data) ? axiosError.response.data : undefined;
  const status = response?.status ?? axiosError.response?.status ?? axiosError.code ?? "UNKNOWN";
  const message = response?.message ?? response?.detail ?? axiosError.message ?? "Request failed";

  return {
    status,
    message,
    raw: error,
    response
  };
};

const apiBaseUrl = normalizeBaseUrl(import.meta.env.VITE_API_BASE_URL || "/");

const service = axios.create({
  baseURL: apiBaseUrl,
  timeout: 10000,
  withCredentials: true
});

service.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const accessToken = token();
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
  },
  (error: unknown) => Promise.reject(error)
);

service.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: unknown) => {
    const requestConfig = axios.isAxiosError(error) ? ((error.config ?? {}) as RequestConfig) : {};
    const requestError = normalizeRequestError(error);

    if (!requestConfig.suppressErrorToast && requestErrorHandler) {
      requestErrorHandler(requestError);
    }

    return Promise.reject(new ApiError(requestError.message, requestError.status, requestError.response ?? requestError.raw));
  }
);


export interface StreamEventPayload {
  delta?: string;
  message?: string;
  [key: string]: unknown;
}

type StreamCallbackResult = void | Promise<void>;

export interface StreamOptions {
  signal?: AbortSignal;
  onDelta?: (delta: string) => StreamCallbackResult;
  onDone?: (payload: StreamEventPayload) => StreamCallbackResult;
  onEvent?: (event: string, payload: StreamEventPayload) => StreamCallbackResult;
}

function resolveApiUrl(url: string): string {
  if (/^https?:\/\//i.test(url)) return url;
  if (apiBaseUrl === "/") return url;
  const normalizedUrl = url.startsWith("/") ? url : `/${url}`;
  return `${apiBaseUrl}${normalizedUrl}`;
}

function parseStreamEvent(block: string): { event: string; payload: StreamEventPayload } | null {
  const lines = block.split(/\r?\n/);
  let event = "message";
  const data: string[] = [];

  for (const line of lines) {
    if (line.startsWith("event:")) event = line.slice(6).trim();
    if (line.startsWith("data:")) data.push(line.slice(5).trimStart());
  }

  if (!data.length) return null;
  return { event, payload: JSON.parse(data.join("\n")) as StreamEventPayload };
}

async function request<T = unknown, Data = unknown>(config: RequestConfig<Data>): Promise<T> {
  const response = await service.request<T, AxiosResponse<T>, Data>(config);
  return response.data;
}

export const api = {
  get: <T>(url: string, params?: object) => request<T>({ url, method: "get", params }),
  post: <T, Data = unknown>(url: string, data?: Data, params?: object) => request<T, Data>({ url, method: "post", data, params }),
  async stream<Data = unknown>(url: string, data: Data, options: StreamOptions = {}) {
    const headers = new Headers({
      Accept: "text/event-stream",
      "Content-Type": "application/json"
    });
    const accessToken = token();
    if (accessToken) headers.set("Authorization", `Bearer ${accessToken}`);

    const response = await fetch(resolveApiUrl(url), {
      method: "POST",
      credentials: "include",
      headers,
      body: JSON.stringify(data),
      signal: options.signal
    });

    if (!response.ok || !response.body) {
      const detail = await response.text();
      throw new ApiError(detail || response.statusText, response.status, detail);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { value, done } = await reader.read();
      buffer += decoder.decode(value ?? new Uint8Array(), { stream: !done });
      const chunks = buffer.split(/\r?\n\r?\n/);
      buffer = chunks.pop() ?? "";

      for (const chunk of chunks) {
        const parsed = parseStreamEvent(chunk);
        if (!parsed) continue;
        await options.onEvent?.(parsed.event, parsed.payload);
        if (parsed.event === "delta" && typeof parsed.payload.delta === "string") {
          await options.onDelta?.(parsed.payload.delta);
        }
        if (parsed.event === "done") await options.onDone?.(parsed.payload);
        if (parsed.event === "error") {
          throw new ApiError(String(parsed.payload.message || "Stream failed"), "STREAM", parsed.payload);
        }
      }

      if (done) break;
    }
  },
  async download(url: string, filename: string) {
    const response = await service.request<Blob>({
      url,
      method: "get",
      responseType: "blob"
    });
    const objectUrl = URL.createObjectURL(response.data);
    const anchor = document.createElement("a");
    anchor.href = objectUrl;
    anchor.download = filename;
    anchor.click();
    URL.revokeObjectURL(objectUrl);
  }
};

export default request;
