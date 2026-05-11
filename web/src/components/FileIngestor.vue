<template>
  <label class="file-ingestor" :class="{ active: Boolean(modelValue) }">
    <input type="file" @change="onChange" />
    <UploadCloud :size="38" />
    <strong>{{ modelValue?.name || "拖入或选择数据文件" }}</strong>
    <span>{{ modelValue ? `${(modelValue.size / 1024 / 1024).toFixed(2)} MB` : "CSV / JSON / PDF / TXT / XLSX" }}</span>
  </label>
</template>

<script setup lang="ts">
import { UploadCloud } from "lucide-vue-next";

defineProps<{ modelValue: File | null }>();
const emit = defineEmits<{ "update:modelValue": [file: File | null] }>();

function onChange(event: Event) {
  const input = event.target as HTMLInputElement;
  emit("update:modelValue", input.files?.[0] ?? null);
}
</script>
