<template>
  <section class="upload-layout page-grid">
    <form class="upload-console asset-upload" @submit.prevent="submit">
      <header class="upload-hero">
        <div>
          <span class="eyebrow">ASSET INTAKE</span>
          <h1>登记并上传数据资产</h1>
          <p>提交文件前补齐来源、覆盖范围、敏感性和授权意图，审核人员可以直接判断资产是否适合进入市场。</p>
        </div>
        <button class="primary-action" type="submit" :disabled="!canSubmit || loading">
          {{ loading ? "提交中..." : "提交到分析管线" }}
        </button>
      </header>

      <section class="upload-section">
        <div class="upload-section-head">
          <span>01</span>
          <div>
            <h2>原始文件</h2>
            <p>支持 CSV、JSON、PDF、TXT、XLSX 和 SQL，系统会根据扩展名进入对应解析流程。</p>
          </div>
        </div>
        <FileIngestor v-model="form.file" />
      </section>

      <section class="upload-section">
        <div class="upload-section-head">
          <span>02</span>
          <div>
            <h2>资产说明</h2>
            <p>说明这份数据解决什么问题，属于什么业务域，方便后续检索和审核。</p>
          </div>
        </div>
        <div class="form-grid">
          <label>资产标题<input v-model="form.title" placeholder="例如：城市交通流量样本" /></label>
          <label>
            业务分类
            <select v-model="form.category">
              <option value="">选择分类</option>
              <option v-for="option in categories" :key="option" :value="option">{{ option }}</option>
            </select>
          </label>
        </div>
        <label>资产描述<textarea v-model="form.description" rows="5" placeholder="说明数据来源、核心字段、统计口径、适用场景和已知限制" /></label>
      </section>

      <section class="upload-section">
        <div class="upload-section-head">
          <span>03</span>
          <div>
            <h2>来源与覆盖</h2>
            <p>记录数据提供方、时间范围和更新节奏，避免资产上线后语义不清。</p>
          </div>
        </div>
        <div class="form-grid">
          <label>来源机构<input v-model="form.source_organization" placeholder="例如：交通运行监测中心" /></label>
          <label>
            更新频率
            <select v-model="form.update_frequency">
              <option value="">选择频率</option>
              <option v-for="option in updateFrequencies" :key="option.value" :value="option.value">{{ option.label }}</option>
            </select>
          </label>
          <label>覆盖开始<input v-model="form.coverage_start" type="date" /></label>
          <label>覆盖结束<input v-model="form.coverage_end" type="date" /></label>
        </div>
      </section>

      <section class="upload-section">
        <div class="upload-section-head">
          <span>04</span>
          <div>
            <h2>治理与授权</h2>
            <p>提前声明敏感等级、公开意图和授权方式，帮助管理员快速完成风险判断。</p>
          </div>
        </div>
        <div class="form-grid">
          <label>
            敏感等级
            <select v-model="form.sensitivity_level">
              <option value="">选择等级</option>
              <option v-for="option in sensitivityLevels" :key="option.value" :value="option.value">{{ option.label }}</option>
            </select>
          </label>
          <label>
            公开意图
            <select v-model="form.intended_visibility">
              <option value="">选择公开意图</option>
              <option v-for="option in visibilityOptions" :key="option.value" :value="option.value">{{ option.label }}</option>
            </select>
          </label>
          <label>
            授权方式
            <select v-model="form.access_policy">
              <option value="">选择授权方式</option>
              <option v-for="option in accessPolicies" :key="option.value" :value="option.value">{{ option.label }}</option>
            </select>
          </label>
          <label>联系邮箱<input v-model="form.contact_email" type="email" placeholder="用于审核沟通" /></label>
        </div>
        <div class="form-grid">
          <label>联系人<input v-model="form.contact_name" placeholder="负责人或数据 steward" /></label>
          <label>使用限制<textarea v-model="form.usage_restrictions" rows="4" placeholder="例如：仅用于研究分析，不得转售；需脱敏后公开展示" /></label>
        </div>
      </section>
    </form>

    <aside class="upload-steps upload-review">
      <div class="upload-review-card">
        <span class="eyebrow">SUBMISSION CHECK</span>
        <h2>提交检查</h2>
        <div class="check-list">
          <article v-for="item in checks" :key="item.label" :class="{ done: item.done }">
            <CheckCircle2 v-if="item.done" :size="18" />
            <CircleAlert v-else :size="18" />
            <span>{{ item.label }}</span>
          </article>
        </div>
      </div>

      <div class="upload-review-card">
        <span class="eyebrow">ASSET SNAPSHOT</span>
        <h2>{{ form.title || "未命名资产" }}</h2>
        <dl>
          <div><dt>分类</dt><dd>{{ form.category || "-" }}</dd></div>
          <div><dt>来源</dt><dd>{{ form.source_organization || "-" }}</dd></div>
          <div><dt>频率</dt><dd>{{ frequencyLabel || "-" }}</dd></div>
          <div><dt>敏感性</dt><dd>{{ sensitivityLabel || "-" }}</dd></div>
          <div><dt>授权</dt><dd>{{ accessPolicyLabel || "-" }}</dd></div>
        </dl>
      </div>

      <div class="upload-review-card">
        <strong>后续流程</strong>
        <p>提交后资产会进入文件存储、结构解析、质量统计、敏感性扫描和管理员审核。审核通过后才会出现在数据市场。</p>
      </div>
    </aside>
  </section>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { CheckCircle2, CircleAlert } from "lucide-vue-next";

import FileIngestor from "@/components/FileIngestor.vue";
import { useAuthStore } from "@/stores/auth";
import { useProviderStore } from "@/stores/provider";

const provider = useProviderStore();
const auth = useAuthStore();
const router = useRouter();
const loading = ref(false);

const categories = ["交通出行", "人口统计", "公共安全", "生态环境", "经济运行", "医疗健康", "教育科研", "企业经营", "其他"];
const updateFrequencies = [
  { value: "one_time", label: "一次性" },
  { value: "daily", label: "每日" },
  { value: "weekly", label: "每周" },
  { value: "monthly", label: "每月" },
  { value: "quarterly", label: "季度" },
  { value: "yearly", label: "年度" },
  { value: "irregular", label: "不定期" }
];
const sensitivityLevels = [
  { value: "public", label: "公开" },
  { value: "internal", label: "内部" },
  { value: "sensitive", label: "敏感" },
  { value: "restricted", label: "受限" }
];
const visibilityOptions = [
  { value: "market_after_review", label: "审核后进入数据市场" },
  { value: "authorized_only", label: "仅授权可见" },
  { value: "private_review", label: "暂不公开" }
];
const accessPolicies = [
  { value: "direct_request", label: "直接申请" },
  { value: "approval_required", label: "审批授权" },
  { value: "contract_required", label: "合同授权" },
  { value: "internal_only", label: "内部使用" }
];

const form = reactive({
  title: "",
  description: "",
  category: "",
  source_organization: auth.profile?.organization || "",
  coverage_start: "",
  coverage_end: "",
  update_frequency: "",
  sensitivity_level: "",
  intended_visibility: "market_after_review",
  access_policy: "approval_required",
  usage_restrictions: "",
  contact_name: auth.profile?.full_name || auth.profile?.username || "",
  contact_email: auth.profile?.email || "",
  file: null as File | null
});

const requiredFields = computed(() => [
  Boolean(form.file),
  Boolean(form.title.trim()),
  Boolean(form.category),
  Boolean(form.source_organization.trim()),
  Boolean(form.update_frequency),
  Boolean(form.sensitivity_level),
  Boolean(form.intended_visibility),
  Boolean(form.access_policy),
  Boolean(form.contact_email.trim())
]);
const canSubmit = computed(() => requiredFields.value.every(Boolean));
const checks = computed(() => [
  { label: "已选择原始文件", done: Boolean(form.file) },
  { label: "已填写标题和业务分类", done: Boolean(form.title.trim() && form.category) },
  { label: "已声明来源和更新频率", done: Boolean(form.source_organization.trim() && form.update_frequency) },
  { label: "已完成敏感性和授权声明", done: Boolean(form.sensitivity_level && form.intended_visibility && form.access_policy) },
  { label: "已填写审核联系人", done: Boolean(form.contact_email.trim()) }
]);
const frequencyLabel = computed(() => updateFrequencies.find((item) => item.value === form.update_frequency)?.label);
const sensitivityLabel = computed(() => sensitivityLevels.find((item) => item.value === form.sensitivity_level)?.label);
const accessPolicyLabel = computed(() => accessPolicies.find((item) => item.value === form.access_policy)?.label);

function textOrUndefined(value: string) {
  return value.trim() || undefined;
}

async function submit() {
  if (!form.file || !canSubmit.value) return;
  loading.value = true;
  try {
    await provider.upload({
      title: form.title.trim(),
      description: textOrUndefined(form.description),
      category: textOrUndefined(form.category),
      source_organization: textOrUndefined(form.source_organization),
      coverage_start: textOrUndefined(form.coverage_start),
      coverage_end: textOrUndefined(form.coverage_end),
      update_frequency: textOrUndefined(form.update_frequency),
      sensitivity_level: textOrUndefined(form.sensitivity_level),
      intended_visibility: textOrUndefined(form.intended_visibility),
      access_policy: textOrUndefined(form.access_policy),
      usage_restrictions: textOrUndefined(form.usage_restrictions),
      contact_name: textOrUndefined(form.contact_name),
      contact_email: textOrUndefined(form.contact_email),
      file: form.file
    });
    router.push(auth.role === "admin" ? "/admin/datasets" : "/provider");
  } finally {
    loading.value = false;
  }
}
</script>
