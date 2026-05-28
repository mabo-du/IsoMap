import { invoke } from "@tauri-apps/api/core";

export interface ImportResult {
  columns: string[];
  preview: Record<string, any>[];
  inferred_types: Record<string, { type: string; confidence: string }>;
  total_rows: number;
}

// In a real app, this would use tauri-plugin-shell to communicate with the python sidecar via stdin/stdout.
// For now, we will mock the invoke if we're not running in Tauri, or assume a rust command wraps it.

export const importDataset = async (filePath: string, sheetName?: string): Promise<ImportResult> => {
  try {
    // We assume a rust command 'import_dataset_cmd' is exposed which forwards to the sidecar.
    const result: ImportResult = await invoke("import_dataset_cmd", { filePath, sheetName });
    return result;
  } catch (error) {
    console.error("Failed to import dataset", error);
    throw error;
  }
};

export const getSheetNames = async (filePath: string): Promise<string[]> => {
  try {
    const result: { sheets: string[] } = await invoke("get_sheet_names_cmd", { filePath });
    return result.sheets;
  } catch (error) {
    console.error("Failed to get sheet names", error);
    throw error;
  }
};

export interface MappingSuggestion {
  target: string;
  confidence: number;
  method: string;
}

export const mapColumns = async (filePath: string, schemaName: string, sheetName?: string): Promise<Record<string, MappingSuggestion[]>> => {
  try {
    const result: { mappings: Record<string, MappingSuggestion[]> } = await invoke("map_columns_cmd", { filePath, schemaName, sheetName });
    return result.mappings;
  } catch (error) {
    console.error("Failed to map columns", error);
    throw error;
  }
};

export const saveOverride = async (sourceColumn: string, targetField: string, schemaName: string): Promise<boolean> => {
  try {
    const result: { success: boolean } = await invoke("save_override_cmd", { sourceColumn, targetField, schemaName });
    return result.success;
  } catch (error) {
    console.error("Failed to save override", error);
    throw error;
  }
};

