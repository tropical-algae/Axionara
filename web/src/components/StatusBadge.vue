<template>
  <span class="status-badge" :data-status="status.toLowerCase()">{{ label }}</span>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { titleCase } from "@/utils/format";

const props = defineProps<{ status?: string | null }>();
const labels: Record<string, string> = {
  uploaded: "已上传",
  processing_review: "分析中",
  reviewed: "待审核",
  published: "已发布",
  rejected: "已拒绝",
  archived: "已归档",
  pending: "待处理",
  queued: "已排队",
  running: "运行中",
  succeeded: "已完成",
  failed: "失败",
  approved: "已通过",
  completed: "已完成"
};

const status = computed(() => props.status || "unknown");
const label = computed(() => labels[status.value] || titleCase(status.value));
</script>
