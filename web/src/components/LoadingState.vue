<template>
  <section class="loading-state">
    <span />
    <p>{{ text || "正在同步数据流..." }}</p>
  </section>
</template>

<script setup lang="ts">
defineProps<{ text?: string }>();
</script>
