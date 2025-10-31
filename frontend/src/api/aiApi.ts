import { apiClient } from './axiosConfig';

// Type definitions matching backend schemas
export interface AIGenerationRequest {
    note_ids: number[];
    prompt?: string;
    ai_provider?: 'openai' | 'anthropic' | 'gemini';
}

export interface AIGenerationResponse {
    id: number;
    generated_content: string;
    ai_provider: string;
    note_ids: number[];
    prompt: string;
    created_date: string;
}

export interface SaveAsNoteRequest {
    generation_id: number;
    title: string;
}

export interface GenerationListResponse {
    items: AIGenerationResponse[];
    total: number;
    page: number;
    per_page: number;
}

export interface ErrorResponse {
    detail: string;
    error_code?: string;
    retry_after?: number;
}

/**
 * Generate an idea using AI based on selected notes
 * @param data - Request data containing note IDs, optional prompt, and AI provider
 * @returns Generated idea response
 * @throws Error with message from backend on failure
 */
export const generateIdea = async (data: AIGenerationRequest): Promise<AIGenerationResponse> => {
    try {
        const response = await apiClient.post<AIGenerationResponse>('/api/ai/generate-idea', data);
        return response.data;
    } catch (error: any) {
        // Handle specific error responses
        if (error.response?.data?.detail) {
            throw new Error(error.response.data.detail);
        }
        throw new Error('Failed to generate idea. Please try again.');
    }
};

/**
 * Get AI generation history for the current user
 * @param page - Page number (default: 1)
 * @param perPage - Items per page (default: 20)
 * @returns Paginated list of AI generations
 * @throws Error with message from backend on failure
 */
export const getGenerations = async (
    page: number = 1,
    perPage: number = 20
): Promise<GenerationListResponse> => {
    try {
        const response = await apiClient.get<GenerationListResponse>(
            `/api/ai/generations?page=${page}&per_page=${perPage}`
        );
        return response.data;
    } catch (error: any) {
        if (error.response?.data?.detail) {
            throw new Error(error.response.data.detail);
        }
        throw new Error('Failed to fetch generation history. Please try again.');
    }
};

/**
 * Save a generated idea as a new note
 * @param data - Request data containing generation ID and note title
 * @returns Created note
 * @throws Error with message from backend on failure
 */
export const saveAsNote = async (data: SaveAsNoteRequest): Promise<any> => {
    try {
        const response = await apiClient.post('/api/ai/save-as-note', data);
        return response.data;
    } catch (error: any) {
        if (error.response?.data?.detail) {
            throw new Error(error.response.data.detail);
        }
        throw new Error('Failed to save as note. Please try again.');
    }
};
