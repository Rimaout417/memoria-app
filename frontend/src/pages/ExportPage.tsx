import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { getNotes, importNotes } from '../api/noteApi';
import { getFavorites } from '../api/favoriteApi';
import { useAuthStore } from '../store/authStore';

export default function ExportPage() {
  const [exporting, setExporting] = useState(false);
  const [importing, setImporting] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { logout, username } = useAuthStore();
  const navigate = useNavigate();

  const handleExportAll = async () => {
    setExporting(true);
    try {
      const notes = await getNotes();
      const json = JSON.stringify(notes, null, 2);
      const blob = new Blob([json], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `notes_${new Date().toISOString().split('T')[0]}.json`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to export notes:', error);
      alert('エクスポートに失敗しました');
    } finally {
      setExporting(false);
    }
  };

  const handleExportFavorites = async () => {
    setExporting(true);
    try {
      const favorites = await getFavorites();
      const json = JSON.stringify(favorites, null, 2);
      const blob = new Blob([json], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `favorites_${new Date().toISOString().split('T')[0]}.json`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to export favorites:', error);
      alert('エクスポートに失敗しました');
    } finally {
      setExporting(false);
    }
  };

  const handleImport = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setImporting(true);
    try {
      const text = await file.text();
      const notes = JSON.parse(text);

      if (!Array.isArray(notes)) {
        alert('無効なファイル形式です');
        return;
      }

      const result = await importNotes(notes);
      alert(`${result.count}件のノートをインポートしました`);

      // ファイル入力をリセット
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (error) {
      console.error('Failed to import notes:', error);
      alert('インポートに失敗しました');
    } finally {
      setImporting(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">📤 エクスポート / インポート</h1>
          <div className="flex items-center gap-4">
            <span className="text-gray-600 dark:text-gray-400">{username}</span>
            <button
              onClick={() => navigate('/notes')}
              className="px-4 py-2 text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300"
            >
              ノート一覧
            </button>
            <button
              onClick={() => navigate('/favorites')}
              className="px-4 py-2 text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300"
            >
              お気に入り
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
      <main className="max-w-4xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-8 mb-6">
          <h2 className="text-xl font-semibold mb-6 text-gray-900 dark:text-white">データをインポート</h2>

          <div className="border dark:border-gray-700 rounded-lg p-6">
            <h3 className="text-lg font-medium mb-2 text-gray-900 dark:text-white">JSONファイルからインポート</h3>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              エクスポートしたJSONファイルからノートをインポートします
            </p>
            <input
              ref={fileInputRef}
              type="file"
              accept=".json"
              onChange={handleImport}
              disabled={importing}
              className="hidden"
              id="import-file"
            />
            <label
              htmlFor="import-file"
              className={`inline-block px-6 py-2 bg-green-600 text-white rounded hover:bg-green-700 cursor-pointer ${importing ? 'opacity-50 cursor-not-allowed' : ''
                }`}
            >
              {importing ? 'インポート中...' : 'ファイルを選択'}
            </label>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-8">
          <h2 className="text-xl font-semibold mb-6 text-gray-900 dark:text-white">データをエクスポート</h2>

          <div className="space-y-4">
            <div className="border dark:border-gray-700 rounded-lg p-6">
              <h3 className="text-lg font-medium mb-2 text-gray-900 dark:text-white">すべてのノート</h3>
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                すべてのノートをJSON形式でエクスポートします
              </p>
              <button
                onClick={handleExportAll}
                disabled={exporting}
                className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
              >
                {exporting ? 'エクスポート中...' : 'エクスポート'}
              </button>
            </div>

            <div className="border dark:border-gray-700 rounded-lg p-6">
              <h3 className="text-lg font-medium mb-2 text-gray-900 dark:text-white">お気に入りのノート</h3>
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                お気に入りに登録したノートのみをJSON形式でエクスポートします
              </p>
              <button
                onClick={handleExportFavorites}
                disabled={exporting}
                className="px-6 py-2 bg-yellow-600 text-white rounded hover:bg-yellow-700 disabled:opacity-50"
              >
                {exporting ? 'エクスポート中...' : 'エクスポート'}
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
