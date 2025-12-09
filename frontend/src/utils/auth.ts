import type { AxiosResponse } from "axios";

const TOKEN_KEY: string = "doc_star_token";

/**
 * LocalStorage에서 액세스 토큰을 가져옵니다.
 * @returns {string | null} 저장된 토큰 문자열 또는 null
 */
export const getToken = (): string | null => {
  return localStorage.getItem(TOKEN_KEY);
};

/**
 * LocalStorage에 액세스 토큰을 저장합니다.
 * @param {string} token - 저장할 토큰 문자열
 */
export const setToken = (token: string): void => {
  localStorage.setItem(TOKEN_KEY, token);
};

/**
 * LocalStorage에서 액세스 토큰을 삭제합니다.
 */
export const removeToken = (): void => {
  localStorage.removeItem(TOKEN_KEY);
};

/**
 * 사용자가 로그인되어 있는지 확인합니다.
 * @returns {boolean} 토큰이 존재하면 true
 */
export const isAuthenticated = (): boolean => {
  return !!getToken();
};

/**
 * HTTP 요청의 Authorization 헤더 값을 'Bearer <token>' 형식으로 가져옵니다.
 * @returns {string} Authorization 헤더 값
 */
export const getAuthHeader = (): string => {
  const token: string | null = getToken();
  return token ? `Bearer ${token}` : "";
};

/**
 * 응답 객체에서 Authorization 헤더를 파싱하여 토큰을 추출합니다.
 * @param {Response} res - fetch API의 Response 객체 (또는 유사한 headers 속성을 가진 객체)
 * @returns {string | null} 추출된 토큰 문자열 또는 null
 */
export const extractTokenFromHeader = (res: Pick<AxiosResponse, "headers">): string | null => {
  const authHeaderValue = res.headers["authorization"];

  const authHeader: string | null =
    (Array.isArray(authHeaderValue)
      ? authHeaderValue[0]?.toString()
      : authHeaderValue?.toString()) || null;

  if (!authHeader) return null;

  const parts: string[] = authHeader.split(" ");
  if (parts.length !== 2) return null;

  const [scheme, token] = parts;
  return scheme === "Bearer" ? token : null;
};
