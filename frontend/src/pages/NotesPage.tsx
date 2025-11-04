import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getNotes, createNote, updateNote, deleteNote, Note, NoteCreate, NoteUpdate } from '../api/noteApi';
import { addFavorite, removeFavorite, isFavorite } from '../api/favoriteApi';
import { useAuthStore } from '../store/authStore';
import { useAIStore } from '../store/aiStore';
import IdeaGenerationModal from '../components/IdeaGenerationModal';

export default function NotesPage() {
  const [notes, setNotes] = useState<Note[]>([]);
  const [favorites, setFavorites] = useState<Set<number>>(new Set());
  const [loading, setLoading] = useState(true);
  const [editingNote, setEditingNote] = useState<Note | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [showAIModal, setShowAIModal] = useState(false);
  const [formData, setFormData] = useState({ title: '', content: '' });
  const { logout, username } = useAuthStore();
  const { selectedNoteIds, toggleNoteSelection, clearSelection } = useAIStore();
  const navigate = useNavigate();

  useEffect(() => {
    loadNotes();
  }, []);

  const loadNotes = async () => {
    try {
      const data = await getNotes();
      setNotes(data);

      // お気に入り状態をチェック
      const favSet = new Set<number>();
      for (const note of data) {
        const isFav = await isFavorite(note.id);
        if (isFav) favSet.add(note.id);
      }
      setFavorites(favSet);
    } catch (error) {
      console.error('Failed to load notes:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingNote(null);
    setFormData({ title: '', content: '' });
    setShowModal(true);
  };

  const handleEdit = (note: Note) => {
    setEditingNote(note);
    setFormData({ title: note.title, content: note.content });
    setShowModal(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      if (editingNote) {
        const updated = await updateNote(editingNote.id, formData as NoteUpdate);
        setNotes(notes.map(n => n.id === updated.id ? updated : n));
      } else {
        const created = await createNote(formData as NoteCreate);
        setNotes([created, ...notes]);
      }
      setShowModal(false);
    } catch (error) {
      console.error('Failed to save note:', error);
      alert('ノートの保存に失敗しました');
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('このノートを削除しますか？')) return;

    try {
      await deleteNote(id);
      setNotes(notes.filter(n => n.id !== id));
      favorites.delete(id);
      setFavorites(new Set(favorites));
    } catch (error) {
      console.error('Failed to delete note:', error);
      alert('ノートの削除に失敗しました');
    }
  };

  const handleToggleFavorite = async (noteId: number) => {
    try {
      if (favorites.has(noteId)) {
        await removeFavorite(noteId);
        favorites.delete(noteId);
      } else {
        await addFavorite(noteId);
        favorites.add(noteId);
      }
      setFavorites(new Set(favorites));
    } catch (error) {
      console.error('Failed to toggle favorite:', error);
      alert('お気に入りの更新に失敗しました');
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleAIGeneration = () => {
    setShowAIModal(true);
  };

  const handleAIModalClose = () => {
    setShowAIModal(false);
  };

  const handleNoteSaved = () => {
    // Reload notes after saving generated content as a note
    loadNotes();
    clearSelection();
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
          <h1 className="text-2xl font-bold text-gray-900">📝 マイノート</h1>
          <div className="flex items-center gap-4">
            <span className="text-gray-600">{username}</span>
            <button
              onClick={() => navigate('/favorites')}
              className="px-4 py-2 text-blue-600 hover:text-blue-700"
            >
              お気に入り
            </button>
            <button
              onClick={() => navigate('/ai-history')}
              className="px-4 py-2 text-blue-600 hover:text-blue-700"
            >
              AI履歴
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
        <div className="mb-6 flex items-center gap-4">
          <button
            onClick={handleCreate}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
          >
            ＋ 新規ノート
          </button>

          {selectedNoteIds.length > 0 && (
            <>
              <button
                onClick={handleAIGeneration}
                className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 font-medium flex items-center gap-2"
              >
                <span>🤖</span>
                <span>AIでアイデア生成 ({selectedNoteIds.length})</span>
              </button>
              <button
                onClick={clearSelection}
                className="px-4 py-2 text-gray-600 hover:text-gray-800"
              >
                選択解除
              </button>
            </>
          )}
        </div>

        {notes.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">ノートがありません</p>
            <p className="text-gray-400 mt-2">「新規ノート」ボタンから作成してください</p>
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {notes.map((note) => (
              <div
                key={note.id}
                className={`bg-white p-6 rounded-lg shadow hover:shadow-md transition-all ${selectedNoteIds.includes(note.id) ? 'ring-2 ring-purple-500' : ''
                  }`}
              >
                <div className="flex justify-between items-start mb-2">
                  <div className="flex items-start gap-3 flex-1">
                    <input
                      type="checkbox"
                      checked={selectedNoteIds.includes(note.id)}
                      onChange={() => toggleNoteSelection(note.id)}
                      className="mt-1 h-5 w-5 text-purple-600 rounded focus:ring-purple-500 cursor-pointer"
                      title="AIアイデア生成用に選択"
                    />
                    <h3 className="text-lg font-semibold text-gray-900 flex-1">
                      {note.title}
                    </h3>
                  </div>
                  <button
                    onClick={() => handleToggleFavorite(note.id)}
                    className={`text-xl ${favorites.has(note.id) ? 'text-yellow-500' : 'text-gray-300'} hover:text-yellow-500`}
                    title={favorites.has(note.id) ? 'お気に入りから削除' : 'お気に入りに追加'}
                  >
                    {favorites.has(note.id) ? '⭐' : '☆'}
                  </button>
                </div>
                <p className="text-gray-600 mb-4 line-clamp-3 whitespace-pre-wrap ml-8">
                  {note.content}
                </p>
                <div className="flex justify-between items-center ml-8">
                  <div className="text-sm text-gray-400">
                    {new Date(note.updated_date).toLocaleDateString('ja-JP')}
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleEdit(note)}
                      className="px-3 py-1 text-sm text-blue-600 hover:text-blue-700"
                    >
                      編集
                    </button>
                    <button
                      onClick={() => handleDelete(note.id)}
                      className="px-3 py-1 text-sm text-red-600 hover:text-red-700"
                    >
                      削除
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {/* Note Edit/Create Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full p-6">
            <h2 className="text-2xl font-bold mb-4">
              {editingNote ? 'ノートを編集' : '新規ノート'}
            </h2>
            <form onSubmit={handleSubmit}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  タイトル
                </label>
                <input
                  type="text"
                  required
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="ノートのタイトル"
                />
              </div>
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  内容
                </label>
                <textarea
                  required
                  rows={10}
                  value={formData.content}
                  onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="ノートの内容"
                />
              </div>
              <div className="flex justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 text-gray-700 hover:text-gray-900"
                >
                  キャンセル
                </button>
                <button
                  type="submit"
                  className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  {editingNote ? '更新' : '作成'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* AI Idea Generation Modal */}
      <IdeaGenerationModal
        isOpen={showAIModal}
        onClose={handleAIModalClose}
        onNoteSaved={handleNoteSaved}
      />
    </div>
  );
}
