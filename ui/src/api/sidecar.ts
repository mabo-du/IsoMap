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

export interface SpatialPreview {
  geojson: any;
  bbox: {
    min_lon: number;
    min_lat: number;
    max_lon: number;
    max_lat: number;
  } | null;
}

export const getSpatialPreview = async (filePath: string, latCol: string, lonCol: string, sheetName?: string): Promise<SpatialPreview> => {
  try {
    const result: SpatialPreview = await invoke("get_spatial_preview_cmd", { filePath, latCol, lonCol, sheetName });
    return result;
  } catch (error) {
    console.error("Failed to get spatial preview", error);
    throw error;
  }
};

export interface ValidationReportData {
  valid: boolean;
  message?: string;
  errors: {
    column: string;
    row: number;
    value: any;
    check: string;
    message: string;
  }[];
  row_errors: Record<number, { column: string; message: string }[]>;
}

export const validateDataset = async (filePath: string, schemaName: string, appliedMappings: Record<string, string>, sheetName?: string): Promise<ValidationReportData> => {
  try {
    const result: { report: ValidationReportData } = await invoke("validate_dataset_cmd", { filePath, schemaName, appliedMappings, sheetName });
    return result.report;
  } catch (error) {
    console.error("Failed to validate dataset", error);
    throw error;
  }
};



