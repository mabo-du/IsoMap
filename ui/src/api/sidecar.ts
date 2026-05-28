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
