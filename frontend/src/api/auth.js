const ACCESS_TOKEN_KEY = "summarix_access_token";
const REFRESH_TOKEN_KEY = "summarix_refresh_token";
const USER_KEY = "summarix_user";

export function storeTokens(payload) {
  localStorage.setItem(ACCESS_TOKEN_KEY, payload.access);
  localStorage.setItem(REFRESH_TOKEN_KEY, payload.refresh);
  localStorage.setItem(USER_KEY, JSON.stringify(payload.user));
}

export function getAccessToken() {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function getCurrentUser() {
  const raw = localStorage.getItem(USER_KEY);
  return raw ? JSON.parse(raw) : null;
}

export function logout() {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}
