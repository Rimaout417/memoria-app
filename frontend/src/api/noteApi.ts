import { apiClient } from './axiosConfig';

export interface Note {
  id: number;
  title: string;
  content: string;
  created_date: string;
  updated_date: string;
  user_id: number;
}

export interface NoteCreate {
  title: string;
  content: string;
}

export interface NoteUpdate {
  title?: string;
  content?: string;
}

// ノート一覧取得
export const getNotes = async (): Promise<Note[]> => {
  const response = await apiClient.get<Note[]>('/api/notes');
  return response.data;
};

// ノート詳細取得
export const getNote = async (id: number): Promise<Note> => {
  const response = await apiClient.get<Note>(`/api/notes/${id}`);
  return response.data;
};

// ノート作成
export const createNote = async (data: NoteCreate): Promise<Note> => {
  const response = await apiClient.post<Note>('/api/notes', data);
  return response.data;
};

// ノート更新
export const updateNote = async (id: number, data: NoteUpdate): Promise<Note> => {
  const response = await apiClient.put<Note>(`/api/notes/${id}`, data);
  return response.data;
};

// ノート削除
export const deleteNote = async (id: number): Promise<void> => {
  await apiClient.delete(`/api/notes/${id}`);
};

// ノートインポート
export const importNotes = async (notes: any[]): Promise<{ message: string; count: number }> => {
  const response = await apiClient.post<{ message: string; count: number }>('/api/notes/import', notes);
  return response.data;
};
