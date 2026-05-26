<template>
  <section class="empty-state">
    <component :is="icon || Database" :size="32" />
    <strong>{{ title }}</strong>
    <p>{{ description }}</p>
  </section>
</template>

<script setup lang="ts">
import { Database } from "lucide-vue-next";

defineProps<{ title: string; description: string; icon?: unknown }>();
</script>
