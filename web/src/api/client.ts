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

const service = axios.create({
  baseURL: normalizeBaseUrl(import.meta.env.VITE_API_BASE_URL || "/"),
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

async function request<T = unknown, Data = unknown>(config: RequestConfig<Data>): Promise<T> {
  const response = await service.request<T, AxiosResponse<T>, Data>(config);
  return response.data;
}

export const api = {
  get: <T>(url: string, params?: object) => request<T>({ url, method: "get", params }),
  post: <T, Data = unknown>(url: string, data?: Data, params?: object) => request<T, Data>({ url, method: "post", data, params }),
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
