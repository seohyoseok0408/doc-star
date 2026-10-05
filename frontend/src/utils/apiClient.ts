import axios, { AxiosHeaders, AxiosError } from "axios";
import type {
  AxiosInstance,
  AxiosResponse,
  AxiosResponseHeaders,
  InternalAxiosRequestConfig,
} from "axios";

import { getAuthHeader, removeToken, setToken } from "./auth";

const BASE_URL: string | undefined = import.meta.env.VITE_BACKEND_API_BASE_URL;

export interface ApiResponse<T> {
  message: string;
  data: T;
}

type RetryableRequestConfig = InternalAxiosRequestConfig & { _retry?: boolean };

// Axios 인스턴스 생성
const apiClient: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// --- 요청 인터셉터 (Authorization 헤더 자동 추가) ---
apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  // Bearer .. 토큰 획득
  const auth: string = getAuthHeader();
  if (!config.headers) {
    config.headers = new AxiosHeaders();
  }
  if (auth) {
    (config.headers as AxiosHeaders).set("Authorization", auth);
  }
  return config;
});

// --- 응답 인터셉터 (에러 핸들링 및 토큰 재발급) ---
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    const status: number | undefined = error.response?.status;
    const originalRequest = error.config as RetryableRequestConfig | undefined;

    // 401 Unauthorized 에러 처리 및 토큰 재발급 시도
    if (status === 401 && originalRequest && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const reissueRes: AxiosResponse = await axios.post(
          `${BASE_URL}/jwt/refresh`,
          {},
          { withCredentials: true } // refresh token 쿠키 전송
        );

        const headers = reissueRes.headers as AxiosResponseHeaders;
        const authHeader = headers["authorization"]?.toString();
        const newAccessToken = authHeader?.split(" ")[1];

        if (newAccessToken) {
          setToken(newAccessToken);
          originalRequest.headers.set("Authorization", `Bearer ${newAccessToken}`);
          return apiClient(originalRequest);
        }
      } catch (reissueError) {
        console.error("토큰 재발급 실패", reissueError);
        removeToken();
        window.location.href = "/login";
        return Promise.reject(reissueError);
      }
    }
    if (status && status >= 500) {
      alert("서버에 문제가 발생했습니다. 잠시 후 다시 시도해주세요.");
    }
    return Promise.reject(error);
  }
);

// --- 응답 핸들링 (공통) ---
/**
 * Axios 응답에서 서버의 ApiResponse<T> Wrapper를 벗겨내고 실제 데이터 T만 반환합니다.
 * @param response AxiosResponse<ApiResponse<T>>
 * @returns T (실제 데이터)
 */
// AxiosResponse의 제네릭을 ApiResponse<T>로 설정
const handleResponse = <T>(response: AxiosResponse<ApiResponse<T>>): T => {
  return response.data.data;
};

// --- API 호출 함수 ---
export const apiGet = async <T>(url: string): Promise<T> => {
  const response: AxiosResponse<ApiResponse<T>> = await apiClient.get(url);
  return handleResponse<T>(response);
};

export const apiPost = async <T>(url: string, body: unknown): Promise<T> => {
  const response: AxiosResponse<ApiResponse<T>> = await apiClient.post(url, body);
  return handleResponse<T>(response);
};

// FormData(multipart/form-data) 전용. Content-Type을 undefined로 비워야 브라우저가 boundary 포함한 헤더를 자동 생성함
export const apiUpload = async <T>(url: string, formData: FormData): Promise<T> => {
  const response: AxiosResponse<ApiResponse<T>> = await apiClient.post(url, formData, {
    headers: { "Content-Type": undefined },
  });
  return handleResponse<T>(response);
};

export const apiPut = async <T>(url: string, body: unknown): Promise<T> => {
  const response: AxiosResponse<ApiResponse<T>> = await apiClient.put(url, body);
  return handleResponse<T>(response);
};

export const apiPatch = async <T>(url: string, body: unknown): Promise<T> => {
  const response: AxiosResponse<ApiResponse<T>> = await apiClient.patch(url, body);
  return handleResponse<T>(response);
};

export const apiDelete = async <T>(url: string): Promise<T> => {
  const response: AxiosResponse<ApiResponse<T>> = await apiClient.delete(url);
  return handleResponse<T>(response);
};

// --- 에러 정보 추출 ---
export const extractErrorInfo = (
  error: unknown
): { status: number | undefined; message: string } => {
  if (axios.isAxiosError<{ message?: string }>(error)) {
    const status = error.response?.status;
    const data = error.response?.data;

    if (data?.message) {
      return { status, message: data.message };
    }

    return { status, message: "요청 처리 중 오류가 발생했습니다." };
  }

  return {
    status: undefined,
    message: "네트워크 오류 또는 알 수 없는 오류입니다.",
  };
};
