import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getFavorites, removeFavorite } from '../api/favoriteApi';
import { Note } from '../api/noteApi';
import { useAuthStore } from '../store/authStore';

export default function FavoritesPage() {
  const [favorites, setFavorites] = useState<Note[]>([]);
  const [loading, setLoading] = useState(true);
  const { logout, username } = useAuthStore();
  const navigate = useNavigate();

  useEffect(() => {
    loadFavorites();
  }, []);

  const loadFavorites = async () => {
    try {
      const data = await getFavorites();
      setFavorites(data);
    } catch (error) {
      console.error('Failed to load favorites:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveFavorite = async (noteId: number) => {
    if (!confirm('お気に入りから削除しますか？')) return;

    try {
      await removeFavorite(noteId);
      setFavorites(favorites.filter(note => note.id !== noteId));
    } catch (error) {
      console.error('Failed to remove favorite:', error);
      alert('お気に入りの削除に失敗しました');
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">読み込み中...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">⭐ お気に入り</h1>
          <div className="flex items-center gap-4">
            <span className="text-gray-600">{username}</span>
            <button
              onClick={() => navigate('/notes')}
              className="px-4 py-2 text-blue-600 hover:text-blue-700"
            >
              ノート一覧
            </button>
            <button
              onClick={() => navigate('/export')}
              className="px-4 py-2 text-blue-600 hover:text-blue-700"
            >
              エクスポート
            </button>
            <button
              onClick={handleLogout}
              className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
            >
              ログアウト
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {favorites.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">お気に入りのノートがありません</p>
            <button
              onClick={() => navigate('/notes')}
              className="mt-4 px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              ノートを見る
            </button>
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {favorites.map((note) => (
              <div
                key={note.id}
                className="bg-white p-6 rounded-lg shadow hover:shadow-md transition-shadow"
              >
                <div className="flex justify-between items-start mb-2">
                  <h3 className="text-lg font-semibold text-gray-900 flex-1">
                    {note.title}
                  </h3>
                  <button
                    onClick={() => handleRemoveFavorite(note.id)}
                    className="text-yellow-500 hover:text-gray-400 text-xl"
                    title="お気に入りから削除"
                  >
                    ⭐
                  </button>
                </div>
                <p className="text-gray-600 mb-4 line-clamp-3">
                  {note.content}
                </p>
                <div className="text-sm text-gray-400">
                  {new Date(note.updated_date).toLocaleDateString('ja-JP')}
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
