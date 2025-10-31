import { create } from 'zustand';
import {
    generateIdea as apiGenerateIdea,
    getGenerations as apiGetGenerations,
    saveAsNote as apiSaveAsNote,
    AIGenerationRequest,
    AIGenerationResponse,
    GenerationListResponse
} from '../api/aiApi';

interface AIState {
    // Selected note IDs for AI generation
    selectedNoteIds: number[];

    // Loading state during AI generation
    isGenerating: boolean;

    // Generated content from AI
    generatedContent: AIGenerationResponse | null;

    // Error state
    error: string | null;

    // Generation history
    generationHistory: AIGenerationResponse[];
    historyTotal: number;
    historyPage: number;
    isLoadingHistory: boolean;

    // Actions
    setSelectedNoteIds: (ids: number[]) => void;
    toggleNoteSelection: (id: number) => void;
    clearSelection: () => void;
    generateIdea: (prompt?: string, aiProvider?: 'openai' | 'anthropic' | 'gemini') => Promise<void>;
    saveAsNote: (generationId: number, title: string) => Promise<void>;
    fetchGenerationHistory: (page?: number) => Promise<void>;
    clearGeneration: () => void;
    clearError: () => void;
}

export const useAIStore = create<AIState>((set, get) => ({
    // Initial state
    selectedNoteIds: [],
    isGenerating: false,
    generatedContent: null,
    error: null,
    generationHistory: [],
    historyTotal: 0,
    historyPage: 1,
    isLoadingHistory: false,

    // Set selected note IDs
    setSelectedNoteIds: (ids: number[]) => {
        set({ selectedNoteIds: ids, error: null });
    },

    // Toggle a single note selection
    toggleNoteSelection: (id: number) => {
        const { selectedNoteIds } = get();
        const isSelected = selectedNoteIds.includes(id);

        if (isSelected) {
            set({
                selectedNoteIds: selectedNoteIds.filter(noteId => noteId !== id),
                error: null
            });
        } else {
            set({
                selectedNoteIds: [...selectedNoteIds, id],
                error: null
            });
        }
    },

    // Clear all selections
    clearSelection: () => {
        set({ selectedNoteIds: [], error: null });
    },

    // Generate idea using AI
    generateIdea: async (prompt?: string, aiProvider: 'openai' | 'anthropic' | 'gemini' = 'openai') => {
        const { selectedNoteIds } = get();

        if (selectedNoteIds.length === 0) {
            set({ error: 'Please select at least one note' });
            return;
        }

        set({ isGenerating: true, error: null, generatedContent: null });

        try {
            const requestData: AIGenerationRequest = {
                note_ids: selectedNoteIds,
                ai_provider: aiProvider,
            };

            if (prompt) {
                requestData.prompt = prompt;
            }

            const result = await apiGenerateIdea(requestData);
            set({
                generatedContent: result,
                isGenerating: false,
                error: null
            });
        } catch (error: any) {
            set({
                error: error.message || 'Failed to generate idea',
                isGenerating: false,
                generatedContent: null
            });
            throw error;
        }
    },

    // Save generated content as a new note
    saveAsNote: async (generationId: number, title: string) => {
        set({ error: null });

        try {
            await apiSaveAsNote({ generation_id: generationId, title });
            // Successfully saved - could trigger a refresh of notes if needed
        } catch (error: any) {
            set({
                error: error.message || 'Failed to save as note'
            });
            throw error;
        }
    },

    // Fetch generation history
    fetchGenerationHistory: async (page: number = 1) => {
        set({ isLoadingHistory: true, error: null });

        try {
            const result: GenerationListResponse = await apiGetGenerations(page, 20);
            set({
                generationHistory: result.items,
                historyTotal: result.total,
                historyPage: result.page,
                isLoadingHistory: false,
                error: null
            });
        } catch (error: any) {
            set({
                error: error.message || 'Failed to fetch generation history',
                isLoadingHistory: false
            });
            throw error;
        }
    },

    // Clear generated content
    clearGeneration: () => {
        set({
            generatedContent: null,
            error: null
        });
    },

    // Clear error
    clearError: () => {
        set({ error: null });
    },
}));
