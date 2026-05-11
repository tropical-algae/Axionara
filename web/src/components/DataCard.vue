<template>
  <RouterLink class="data-card" :to="to">
    <div class="card-head">
      <StatusBadge :status="item.dataset.status" />
      <small>{{ item.dataset.source_format?.toUpperCase() }}</small>
    </div>
    <h3>{{ item.dataset.title }}</h3>
    <p>{{ item.profile?.public_summary || item.dataset.description || "该数据资产尚未生成公开摘要，等待分析管线补齐。" }}</p>
    <div class="tag-row">
      <span v-for="tag in item.tags?.slice(0, 4)" :key="tag">{{ tag }}</span>
    </div>
    <div class="card-foot">
      <span>{{ bytes(item.dataset.file_size_bytes) }}</span>
      <ArrowUpRight :size="17" />
    </div>
  </RouterLink>
</template>

<script setup lang="ts">
import { ArrowUpRight } from "lucide-vue-next";

import StatusBadge from "@/components/StatusBadge.vue";
import type { CatalogDataset } from "@/api/types";
import { bytes } from "@/utils/format";

defineProps<{ item: CatalogDataset; to: string }>();
</script>
