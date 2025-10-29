import { apiClient } from './axiosConfig';

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface UserResponse {
  id: number;
  username: string;
  is_active: boolean;
  created_date: string;
}

// ログイン
export const login = async (data: LoginRequest): Promise<AuthResponse> => {
  // FastAPIのOAuth2PasswordRequestFormはform-dataを期待
  const formData = new URLSearchParams();
  formData.append('username', data.username);
  formData.append('password', data.password);

  const response = await apiClient.post<AuthResponse>('/api/auth/login', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });
  
  // トークンをローカルストレージに保存
  localStorage.setItem('access_token', response.data.access_token);
  localStorage.setItem('username', data.username);
  
  return response.data;
};

// ユーザー登録
export const register = async (data: RegisterRequest): Promise<UserResponse> => {
  const response = await apiClient.post<UserResponse>('/api/auth/register', data);
  return response.data;
};

// ログアウト
export const logout = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('username');
};

// 現在のユーザー情報を取得
export const getCurrentUser = async (): Promise<UserResponse> => {
  const response = await apiClient.get<UserResponse>('/api/auth/me');
  return response.data;
};

// トークンの存在確認
export const isAuthenticated = (): boolean => {
  return !!localStorage.getItem('access_token');
};
