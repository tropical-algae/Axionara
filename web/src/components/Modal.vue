<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="open" class="modal-screen" @click.self="$emit('close')">
        <section class="modal-panel">
          <header>
            <strong>{{ title }}</strong>
            <button type="button" @click="$emit('close')"><X :size="18" /></button>
          </header>
          <slot />
        </section>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { X } from "lucide-vue-next";

defineProps<{ open: boolean; title: string }>();
defineEmits<{ close: [] }>();
</script>
