import { useState, useEffect } from 'react';
import { useAIStore } from '../store/aiStore';

interface IdeaGenerationModalProps {
    isOpen: boolean;
    onClose: () => void;
    onNoteSaved?: () => void;
}

export default function IdeaGenerationModal({ isOpen, onClose, onNoteSaved }: IdeaGenerationModalProps) {
    const [prompt, setPrompt] = useState('');
    const [aiProvider, setAiProvider] = useState<'openai' | 'anthropic' | 'gemini'>('openai');
    const [saveTitle, setSaveTitle] = useState('');
    const [showSaveForm, setShowSaveForm] = useState(false);
    const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' | 'info' } | null>(null);

    const {
        selectedNoteIds,
        isGenerating,
        generatedContent,
        error,
        generateIdea,
        saveAsNote,
        clearGeneration,
        clearError
    } = useAIStore();

    // Clear state when modal opens/closes
    useEffect(() => {
        if (!isOpen) {
            setPrompt('');
            setSaveTitle('');
            setShowSaveForm(false);
            clearGeneration();
            clearError();
            setToast(null);
        }
    }, [isOpen, clearGeneration, clearError]);

    // Show toast for errors
    useEffect(() => {
        if (error) {
            showToast(getErrorMessage(error), 'error');
        }
    }, [error]);

    const showToast = (message: string, type: 'success' | 'error' | 'info') => {
        setToast({ message, type });
        setTimeout(() => setToast(null), 5000);
    };

    const getErrorMessage = (errorMsg: string): string => {
        // Rate limit error
        if (errorMsg.includes('429') || errorMsg.toLowerCase().includes('rate limit')) {
            const retryMatch = errorMsg.match(/(\d+)\s*(秒|分|時間)/);
            if (retryMatch) {
                return `レート制限に達しました。${retryMatch[0]}後に再試行してください。`;
            }
            return 'レート制限に達しました。しばらく待ってから再試行してください。';
        }

        // Timeout error
        if (errorMsg.toLowerCase().includes('timeout') || errorMsg.includes('30')) {
            return 'リクエストがタイムアウトしました。ノートの内容を減らすか、後でもう一度お試しください。';
        }

        // AI service unavailable
        if (errorMsg.includes('503') || errorMsg.includes('利用できません')) {
            return 'AIサービスが一時的に利用できません。しばらく待ってから再試行してください。';
        }

        // Token limit error
        if (errorMsg.includes('長すぎます') || errorMsg.toLowerCase().includes('token')) {
            return '選択したノートの内容が長すぎます。ノートの数を減らしてください。';
        }

        // Note not found
        if (errorMsg.includes('404') || errorMsg.includes('見つかりません')) {
            return '選択したノートが見つかりません。ページを更新してください。';
        }

        // Authentication error
        if (errorMsg.includes('401') || errorMsg.includes('認証')) {
            return '認証エラーが発生しました。再度ログインしてください。';
        }

        // Generic error
        return errorMsg || 'エラーが発生しました。もう一度お試しください。';
    };

    const handleGenerate = async () => {
        if (selectedNoteIds.length === 0) {
            showToast('ノートを選択してください', 'error');
            return;
        }

        if (prompt.length > 2000) {
            showToast('プロンプトは2000文字以内で入力してください', 'error');
            return;
        }

        try {
            await generateIdea(prompt || undefined, aiProvider);
            showToast('アイデアを生成しました！', 'success');
            setShowSaveForm(true);
        } catch (err: any) {
            // Check if AI is disabled on server
            if (err?.message?.includes('AI機能は現在利用できません') ||
                err?.message?.includes('APIキーが設定されていません')) {
                showToast('AI機能は現在利用できません。ローカル環境でお試しください。', 'info');
            }
            console.error('Generation error:', err);
        }
    };

    const handleSaveAsNote = async () => {
        if (!generatedContent) return;

        if (!saveTitle.trim()) {
            showToast('タイトルを入力してください', 'error');
            return;
        }

        if (saveTitle.length > 200) {
            showToast('タイトルは200文字以内で入力してください', 'error');
            return;
        }

        try {
            await saveAsNote(generatedContent.id, saveTitle);
            showToast('ノートとして保存しました！', 'success');
            setTimeout(() => {
                onNoteSaved?.();
                onClose();
            }, 1500);
        } catch (err) {
            // Error is handled by useEffect
            console.error('Save error:', err);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white dark:bg-gray-800 rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
                {/* Toast Notification */}
                {toast && (
                    <div className={`fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg z-50 ${toast.type === 'success' ? 'bg-green-500' :
                        toast.type === 'error' ? 'bg-red-500' :
                            'bg-blue-500'
                        } text-white`}>
                        {toast.message}
                    </div>
                )}

                {/* Header */}
                <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                    <div className="flex justify-between items-center">
                        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                            🤖 AIアイデア生成
                        </h2>
                        <button
                            onClick={onClose}
                            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 text-2xl"
                        >
                            ×
                        </button>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                        選択中のノート: {selectedNoteIds.length}件
                    </p>
                </div>

                {/* Content */}
                <div className="p-6 space-y-6">
                    {/* AI Provider Selection */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            AIプロバイダー
                        </label>
                        <select
                            value={aiProvider}
                            onChange={(e) => setAiProvider(e.target.value as 'openai' | 'anthropic' | 'gemini')}
                            disabled={isGenerating}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:bg-gray-100 dark:disabled:bg-gray-800 disabled:cursor-not-allowed"
                        >
                            <option value="openai">OpenAI (GPT-4)</option>
                            <option value="anthropic">Anthropic (Claude)</option>
                            <option value="gemini">Google (Gemini)</option>
                        </select>
                    </div>

                    {/* Prompt Input */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            プロンプト（オプション）
                            <span className="text-gray-500 dark:text-gray-400 text-xs ml-2">
                                {prompt.length}/2000文字
                            </span>
                        </label>
                        <textarea
                            value={prompt}
                            onChange={(e) => setPrompt(e.target.value)}
                            disabled={isGenerating}
                            rows={4}
                            maxLength={2000}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:bg-gray-100 dark:disabled:bg-gray-800 disabled:cursor-not-allowed"
                            placeholder="例: これらのノートから新しいプロジェクトのアイデアを3つ提案してください"
                        />
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                            空欄の場合、デフォルトのプロンプトが使用されます
                        </p>
                    </div>

                    {/* AI Feature Notice */}
                    <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                        <div className="flex items-start gap-3">
                            <span className="text-2xl">ℹ️</span>
                            <div className="flex-1">
                                <h4 className="text-sm font-semibold text-blue-900 dark:text-blue-200 mb-1">
                                    AI機能について
                                </h4>
                                <p className="text-sm text-blue-800 dark:text-blue-300">
                                    本番環境ではAI機能は無効化されています。この機能を使用するには、ローカル環境でAPIキーを設定してください。
                                </p>
                                <p className="text-xs text-blue-700 dark:text-blue-400 mt-2">
                                    対応プロバイダー: OpenAI (GPT-4), Anthropic (Claude), Google (Gemini)
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* Generate Button */}
                    {!generatedContent && (
                        <button
                            onClick={handleGenerate}
                            disabled={isGenerating || selectedNoteIds.length === 0}
                            className="w-full px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-300 disabled:cursor-not-allowed font-medium flex items-center justify-center gap-2"
                        >
                            {isGenerating ? (
                                <>
                                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                                    <span>生成中...</span>
                                </>
                            ) : (
                                <>
                                    <span>✨</span>
                                    <span>アイデアを生成（デモ）</span>
                                </>
                            )}
                        </button>
                    )}

                    {/* Generated Content Display */}
                    {generatedContent && (
                        <div className="space-y-4">
                            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 border border-gray-200 dark:border-gray-600">
                                <div className="flex justify-between items-start mb-2">
                                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                                        生成結果
                                    </h3>
                                    <span className="text-xs text-gray-500 dark:text-gray-400 bg-white dark:bg-gray-800 px-2 py-1 rounded">
                                        {generatedContent.ai_provider}
                                    </span>
                                </div>
                                <div className="text-gray-700 dark:text-gray-200 whitespace-pre-wrap max-h-96 overflow-y-auto">
                                    {generatedContent.generated_content}
                                </div>
                            </div>

                            {/* Save as Note Section */}
                            {showSaveForm && (
                                <div className="space-y-3">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                            ノートのタイトル
                                            <span className="text-gray-500 dark:text-gray-400 text-xs ml-2">
                                                {saveTitle.length}/200文字
                                            </span>
                                        </label>
                                        <input
                                            type="text"
                                            value={saveTitle}
                                            onChange={(e) => setSaveTitle(e.target.value)}
                                            maxLength={200}
                                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                                            placeholder="生成されたアイデアのタイトル"
                                        />
                                    </div>
                                    <button
                                        onClick={handleSaveAsNote}
                                        disabled={!saveTitle.trim()}
                                        className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed font-medium"
                                    >
                                        📝 ノートとして保存
                                    </button>
                                </div>
                            )}

                            {/* Regenerate Button */}
                            <button
                                onClick={() => {
                                    clearGeneration();
                                    setShowSaveForm(false);
                                    setSaveTitle('');
                                }}
                                className="w-full px-4 py-2 text-purple-600 dark:text-purple-400 hover:text-purple-700 dark:hover:text-purple-300 font-medium"
                            >
                                🔄 別のアイデアを生成
                            </button>
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="p-6 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
                    <div className="flex justify-end gap-3">
                        <button
                            onClick={onClose}
                            className="px-6 py-2 text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white font-medium"
                        >
                            閉じる
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
