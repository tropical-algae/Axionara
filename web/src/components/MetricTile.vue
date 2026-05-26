<template>
  <article class="metric-tile" :class="{ intense }">
    <span>{{ label }}</span>
    <strong>{{ value }}</strong>
    <em>{{ caption }}</em>
  </article>
</template>

<script setup lang="ts">
defineProps<{ label: string; value: string | number; caption?: string; intense?: boolean }>();
</script>
