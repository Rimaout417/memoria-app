import { apiClient } from './axiosConfig';
import { Note } from './noteApi';

export interface Favorite {
  id: number;
  note_id: number;
  user_id: number;
  created_date: string;
}

// お気に入り一覧取得
export const getFavorites = async (): Promise<Note[]> => {
  const response = await apiClient.get<Note[]>('/api/favorites');
  return response.data;
};

// お気に入り追加
export const addFavorite = async (noteId: number): Promise<Favorite> => {
  const response = await apiClient.post<Favorite>('/api/favorites', { note_id: noteId });
  return response.data;
};

// お気に入り削除
export const removeFavorite = async (noteId: number): Promise<void> => {
  await apiClient.delete(`/api/favorites/${noteId}`);
};

// お気に入り状態確認
export const isFavorite = async (noteId: number): Promise<boolean> => {
  try {
    const favorites = await getFavorites();
    return favorites.some(note => note.id === noteId);
  } catch {
    return false;
  }
};
