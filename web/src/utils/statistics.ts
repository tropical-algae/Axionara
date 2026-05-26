import { bytes, compact, percent } from "@/utils/format";

export interface StatisticTile {
  label: string;
  value: string;
  caption: string;
}

export interface FieldProfile {
  name: string;
  normalizedName: string;
  type: string;
  nullable: boolean;
  nullCount: number;
  nullRatio: number;
  uniqueCount: number;
}

export interface NormalizedPublicStatistics {
  representation: string;
  sourceFormat: string;
  contentType: string;
  fileSize: string;
  etag: string;
  tiles: StatisticTile[];
  fields: FieldProfile[];
  structure: StatisticTile[];
  fallback: boolean;
  raw: Record<string, unknown>;
}

function record(value: unknown): Record<string, unknown> {
  return value && typeof value === "object" && !Array.isArray(value) ? (value as Record<string, unknown>) : {};
}

function number(value: unknown): number {
  const parsed = typeof value === "number" ? value : Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

function string(value: unknown, fallback = "-"): string {
  return typeof value === "string" && value.trim() ? value : fallback;
}

function fieldProfiles(value: unknown): FieldProfile[] {
  if (!Array.isArray(value)) return [];
  return value.map((item) => {
    const row = record(item);
    return {
      name: string(row.name),
      normalizedName: string(row.normalized_name),
      type: string(row.inferred_type, "unknown"),
      nullable: Boolean(row.nullable),
      nullCount: number(row.null_count),
      nullRatio: number(row.null_ratio),
      uniqueCount: number(row.unique_count)
    };
  });
}

export function normalizePublicStatistics(value?: Record<string, unknown> | null): NormalizedPublicStatistics {
  const raw = value ?? {};
  const common = record(raw.common);
  const tabular = record(raw.tabular);
  const hierarchical = record(raw.hierarchical);
  const document = record(raw.document);
  const representation = string(common.representation_type, string(raw.representation_type));

  const base = {
    representation,
    sourceFormat: string(common.source_format, string(raw.source_format)).toUpperCase(),
    contentType: string(common.content_type, string(raw.content_type)),
    fileSize: bytes(number(common.file_size_bytes || raw.file_size_bytes)),
    etag: string(common.etag, string(raw.etag)),
    raw
  };

  if (!Object.keys(common).length && !representation) {
    return { ...base, representation: "-", tiles: [], fields: [], structure: [], fallback: true };
  }

  if (representation === "tabular" || Object.keys(tabular).length > 0) {
    return {
      ...base,
      representation: "tabular",
      fallback: false,
      tiles: [
        { label: "记录数", value: compact(tabular.record_count), caption: "结构化样本规模" },
        { label: "字段数", value: compact(tabular.column_count), caption: "可解析字段数量" },
        { label: "重复行", value: compact(tabular.duplicate_row_count), caption: percent(tabular.duplicate_row_ratio) },
        { label: "缺失值", value: compact(tabular.missing_value_count), caption: percent(tabular.missing_value_ratio) }
      ],
      fields: fieldProfiles(tabular.column_profiles),
      structure: [
        { label: "主键候选", value: compact(tabular.primary_key_candidates), caption: "自动识别结果" },
        { label: "采样窗口", value: compact(tabular.sample_size), caption: "分析覆盖范围" }
      ]
    };
  }

  if (representation === "document" || Object.keys(document).length > 0) {
    return {
      ...base,
      representation: "document",
      fallback: false,
      tiles: [
        { label: "可提取字符", value: compact(document.extractable_text_chars), caption: "文本解析规模" },
        { label: "提取比例", value: percent(document.extractable_text_ratio), caption: "公开文本可用性" },
        { label: "解析状态", value: string(document.text_extraction_status), caption: string(document.text_extraction_engine, "extractor") },
        { label: "截断", value: document.text_extraction_truncated ? "是" : "否", caption: "内容边界" }
      ],
      fields: [],
      structure: []
    };
  }

  if (representation === "hierarchical" || Object.keys(hierarchical).length > 0) {
    return {
      ...base,
      representation: "hierarchical",
      fallback: false,
      tiles: [
        { label: "根结构", value: string(hierarchical.root_type), caption: "层级入口" },
        { label: "节点规模", value: compact(hierarchical.node_count), caption: "解析节点" },
        { label: "最大深度", value: compact(hierarchical.max_depth), caption: "嵌套复杂度" }
      ],
      fields: [],
      structure: [
        { label: "数组节点", value: compact(hierarchical.array_count), caption: "可展开序列" },
        { label: "对象节点", value: compact(hierarchical.object_count), caption: "结构单元" }
      ]
    };
  }

  return { ...base, tiles: [], fields: [], structure: [], fallback: true };
}
