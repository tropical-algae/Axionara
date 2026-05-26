import type { DatasetAsset } from "@/api/types";

const updateFrequencyLabels: Record<string, string> = {
  one_time: "一次性",
  daily: "每日",
  weekly: "每周",
  monthly: "每月",
  quarterly: "季度",
  yearly: "年度",
  irregular: "不定期"
};

const sensitivityLabels: Record<string, string> = {
  public: "公开",
  internal: "内部",
  sensitive: "敏感",
  restricted: "受限"
};

const visibilityLabels: Record<string, string> = {
  market_after_review: "审核后进入数据市场",
  authorized_only: "仅授权可见",
  private_review: "暂不公开"
};

const accessPolicyLabels: Record<string, string> = {
  direct_request: "直接申请",
  approval_required: "审批授权",
  contract_required: "合同授权",
  internal_only: "内部使用"
};

function label(map: Record<string, string>, value?: string | null) {
  if (!value) return "";
  return map[value] || value;
}

function dateRange(start?: string | null, end?: string | null) {
  if (start && end) return `${start} 至 ${end}`;
  return start || end || "";
}

export function publicMetadataRows(dataset?: DatasetAsset | null) {
  if (!dataset) return [];
  return [
    { label: "业务分类", value: dataset.category },
    { label: "来源机构", value: dataset.source_organization },
    { label: "覆盖时间", value: dateRange(dataset.coverage_start, dataset.coverage_end) },
    { label: "更新频率", value: label(updateFrequencyLabels, dataset.update_frequency) },
    { label: "授权方式", value: label(accessPolicyLabels, dataset.access_policy) },
    { label: "使用限制", value: dataset.usage_restrictions }
  ].filter((row) => Boolean(row.value));
}

export function governedMetadataRows(dataset?: DatasetAsset | null) {
  if (!dataset) return [];
  return [
    ...publicMetadataRows(dataset),
    { label: "敏感等级", value: label(sensitivityLabels, dataset.sensitivity_level) },
    { label: "公开意图", value: label(visibilityLabels, dataset.intended_visibility) },
    { label: "联系人", value: dataset.contact_name },
    { label: "联系邮箱", value: dataset.contact_email }
  ].filter((row) => Boolean(row.value));
}
