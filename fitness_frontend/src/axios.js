import axios from 'axios';
import { jwtDecode } from "jwt-decode";

const isTokenExpired = (token) => {
  if (!token) return true;
  try {
    const decoded = jwtDecode(token);
    const currentTime = Date.now() / 1000;
    return decoded.exp < currentTime;
  } catch (error) {
    console.error("Invalid token:", error);
    return true;
  }
};

const refreshAccessToken = async () => {
  const refreshToken = localStorage.getItem("refresh_token");
  if (!refreshToken) {
    throw new Error("No refresh token available");
  }

  try {
    const apiUrl = import.meta.env.VITE_BACKEND_API_URL;
    const response = await axios.post(`${apiUrl}/auth/refresh`, {
      refresh_token: refreshToken,
    });

    localStorage.setItem("access_token", response.data.access_token);
    return response.data.access_token;
  } catch (error) {
    console.error("Failed to refresh access token", error);
    throw error;
  }
};

let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });

  failedQueue = [];
};

axios.interceptors.request.use(
  async (config) => {
    const accessToken = localStorage.getItem("access_token");

    if (accessToken && isTokenExpired(accessToken)) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((newToken) => {
            config.headers.Authorization = `Bearer ${newToken}`;
            return config;
          })
          .catch((error) => {
            return Promise.reject(error);
          });
      }

      isRefreshing = true;

      try {
        const newAccessToken = await refreshAccessToken();
        config.headers.Authorization = `Bearer ${newAccessToken}`;
        processQueue(null, newAccessToken);
        return config;
      } catch (error) {
        processQueue(error, null);
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        window.location.href = "/login";
        return Promise.reject(error);
      } finally {
        isRefreshing = false;
      }
    } else if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default axios;
