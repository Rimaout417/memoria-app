import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Axiosインスタンスを作成
export const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// リクエストインターセプター：自動的にトークンを追加
apiClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// レスポンスインターセプター：401エラーでログアウト
apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            // トークンが無効な場合、ローカルストレージをクリア
            localStorage.removeItem('access_token');
            localStorage.removeItem('username');
            // ログインページにリダイレクト
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);
