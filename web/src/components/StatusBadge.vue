<template>
  <span class="status-badge" :data-status="status.toLowerCase()">{{ label }}</span>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { titleCase } from "@/utils/format";

const props = defineProps<{ status?: string | null }>();
const status = computed(() => props.status || "unknown");
const label = computed(() => titleCase(status.value));
</script>
