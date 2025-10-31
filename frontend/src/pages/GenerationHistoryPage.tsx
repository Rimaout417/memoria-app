import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { useAIStore } from '../store/aiStore';
import { AIGenerationResponse } from '../api/aiApi';

export default function GenerationHistoryPage() {
    const [savingId, setSavingId] = useState<number | null>(null);
    const [saveTitle, setSaveTitle] = useState('');
    const [showSaveModal, setShowSaveModal] = useState(false);
    const [selectedGeneration, setSelectedGeneration] = useState<AIGenerationResponse | null>(null);

    const { logout, username } = useAuthStore();
    const {
        generationHistory,
        historyTotal,
        historyPage,
        isLoadingHistory,
        error,
        fetchGenerationHistory,
        saveAsNote,
        clearError
    } = useAIStore();

    const navigate = useNavigate();

    useEffect(() => {
        fetchGenerationHistory(1);
    }, []);

    const handlePageChange = (newPage: number) => {
        fetchGenerationHistory(newPage);
    };

    const handleSaveAsNote = (generation: AIGenerationResponse) => {
        setSelectedGeneration(generation);
        setSaveTitle(`AI生成: ${new Date(generation.created_date).toLocaleDateString('ja-JP')}`);
        setShowSaveModal(true);
    };

    const handleSaveSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!selectedGeneration || !saveTitle.trim()) {
            return;
        }

        setSavingId(selectedGeneration.id);

        try {
            await saveAsNote(selectedGeneration.id, saveTitle);
            alert('ノートとして保存しました');
            setShowSaveModal(false);
            setSaveTitle('');
            setSelectedGeneration(null);
        } catch (error) {
            console.error('Failed to save as note:', error);
            alert('ノートの保存に失敗しました');
        } finally {
            setSavingId(null);
        }
    };

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    const totalPages = Math.ceil(historyTotal / 20);

    if (isLoadingHistory && generationHistory.length === 0) {
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
                    <h1 className="text-2xl font-bold text-gray-900">🤖 AI生成履歴</h1>
                    <div className="flex items-center gap-4">
                        <span className="text-gray-600">{username}</span>
                        <button
                            onClick={() => navigate('/notes')}
                            className="px-4 py-2 text-blue-600 hover:text-blue-700"
                        >
                            ノート一覧
                        </button>
                        <button
                            onClick={() => navigate('/favorites')}
                            className="px-4 py-2 text-blue-600 hover:text-blue-700"
                        >
                            お気に入り
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
                {error && (
                    <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                        <p className="text-red-800">{error}</p>
                        <button
                            onClick={clearError}
                            className="mt-2 text-sm text-red-600 hover:text-red-800 underline"
                        >
                            閉じる
                        </button>
                    </div>
                )}

                {generationHistory.length === 0 ? (
                    <div className="text-center py-12">
                        <p className="text-gray-500 text-lg">AI生成履歴がありません</p>
                        <button
                            onClick={() => navigate('/notes')}
                            className="mt-4 px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                        >
                            ノートからアイデアを生成
                        </button>
                    </div>
                ) : (
                    <>
                        <div className="space-y-4">
                            {generationHistory.map((generation) => (
                                <div
                                    key={generation.id}
                                    className="bg-white p-6 rounded-lg shadow hover:shadow-md transition-shadow"
                                >
                                    <div className="flex justify-between items-start mb-4">
                                        <div className="flex-1">
                                            <div className="flex items-center gap-3 mb-2">
                                                <span className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm font-medium">
                                                    {generation.ai_provider.toUpperCase()}
                                                </span>
                                                <span className="text-sm text-gray-500">
                                                    {new Date(generation.created_date).toLocaleString('ja-JP')}
                                                </span>
                                            </div>
                                            <p className="text-sm text-gray-600 mb-2">
                                                <strong>プロンプト:</strong> {generation.prompt}
                                            </p>
                                            <p className="text-sm text-gray-500">
                                                使用ノート: {generation.note_ids.length}件
                                            </p>
                                        </div>
                                        <button
                                            onClick={() => handleSaveAsNote(generation)}
                                            disabled={savingId === generation.id}
                                            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center gap-2"
                                        >
                                            {savingId === generation.id ? (
                                                <>
                                                    <span className="animate-spin">⏳</span>
                                                    <span>保存中...</span>
                                                </>
                                            ) : (
                                                <>
                                                    <span>💾</span>
                                                    <span>ノートとして保存</span>
                                                </>
                                            )}
                                        </button>
                                    </div>

                                    <div className="mt-4 p-4 bg-gray-50 rounded border border-gray-200">
                                        <h4 className="text-sm font-semibold text-gray-700 mb-2">生成されたコンテンツ:</h4>
                                        <p className="text-gray-800 whitespace-pre-wrap">{generation.generated_content}</p>
                                    </div>
                                </div>
                            ))}
                        </div>

                        {/* Pagination */}
                        {totalPages > 1 && (
                            <div className="mt-8 flex justify-center items-center gap-2">
                                <button
                                    onClick={() => handlePageChange(historyPage - 1)}
                                    disabled={historyPage === 1 || isLoadingHistory}
                                    className="px-4 py-2 bg-white border border-gray-300 rounded hover:bg-gray-50 disabled:bg-gray-100 disabled:cursor-not-allowed"
                                >
                                    前へ
                                </button>

                                <div className="flex gap-1">
                                    {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                                        let pageNum;
                                        if (totalPages <= 5) {
                                            pageNum = i + 1;
                                        } else if (historyPage <= 3) {
                                            pageNum = i + 1;
                                        } else if (historyPage >= totalPages - 2) {
                                            pageNum = totalPages - 4 + i;
                                        } else {
                                            pageNum = historyPage - 2 + i;
                                        }

                                        return (
                                            <button
                                                key={pageNum}
                                                onClick={() => handlePageChange(pageNum)}
                                                disabled={isLoadingHistory}
                                                className={`px-4 py-2 rounded ${historyPage === pageNum
                                                        ? 'bg-blue-600 text-white'
                                                        : 'bg-white border border-gray-300 hover:bg-gray-50'
                                                    } disabled:cursor-not-allowed`}
                                            >
                                                {pageNum}
                                            </button>
                                        );
                                    })}
                                </div>

                                <button
                                    onClick={() => handlePageChange(historyPage + 1)}
                                    disabled={historyPage === totalPages || isLoadingHistory}
                                    className="px-4 py-2 bg-white border border-gray-300 rounded hover:bg-gray-50 disabled:bg-gray-100 disabled:cursor-not-allowed"
                                >
                                    次へ
                                </button>
                            </div>
                        )}

                        <div className="mt-4 text-center text-sm text-gray-500">
                            全{historyTotal}件中 {(historyPage - 1) * 20 + 1}〜{Math.min(historyPage * 20, historyTotal)}件を表示
                        </div>
                    </>
                )}
            </main>

            {/* Save as Note Modal */}
            {showSaveModal && selectedGeneration && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
                    <div className="bg-white rounded-lg max-w-2xl w-full p-6">
                        <h2 className="text-2xl font-bold mb-4">ノートとして保存</h2>
                        <form onSubmit={handleSaveSubmit}>
                            <div className="mb-4">
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    ノートのタイトル
                                </label>
                                <input
                                    type="text"
                                    required
                                    value={saveTitle}
                                    onChange={(e) => setSaveTitle(e.target.value)}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    placeholder="タイトルを入力"
                                    maxLength={200}
                                />
                            </div>

                            <div className="mb-6">
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    プレビュー
                                </label>
                                <div className="p-4 bg-gray-50 rounded border border-gray-200 max-h-60 overflow-y-auto">
                                    <p className="text-gray-800 whitespace-pre-wrap text-sm">
                                        {selectedGeneration.generated_content}
                                    </p>
                                </div>
                            </div>

                            <div className="flex justify-end gap-3">
                                <button
                                    type="button"
                                    onClick={() => {
                                        setShowSaveModal(false);
                                        setSaveTitle('');
                                        setSelectedGeneration(null);
                                    }}
                                    className="px-4 py-2 text-gray-700 hover:text-gray-900"
                                    disabled={savingId !== null}
                                >
                                    キャンセル
                                </button>
                                <button
                                    type="submit"
                                    disabled={savingId !== null}
                                    className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                                >
                                    {savingId !== null ? '保存中...' : '保存'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
