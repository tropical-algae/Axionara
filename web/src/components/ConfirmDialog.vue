<template>
  <Modal :open="open" :title="title" @close="handleClose">
    <div class="confirm-dialog" :class="`tone-${tone}`">
      <p v-if="description">{{ description }}</p>
      <slot />
      <div class="confirm-actions">
        <button type="button" :disabled="busy" @click="handleClose">{{ cancelLabel }}</button>
        <button class="primary-action" type="button" :disabled="busy" @click="$emit('confirm')">
          {{ busy ? busyLabel : confirmLabel }}
        </button>
      </div>
    </div>
  </Modal>
</template>

<script setup lang="ts">
import Modal from "@/components/Modal.vue";

const props = withDefaults(
  defineProps<{
    open: boolean;
    title: string;
    description?: string;
    confirmLabel?: string;
    cancelLabel?: string;
    busyLabel?: string;
    tone?: "default" | "danger";
    busy?: boolean;
  }>(),
  {
    description: "",
    confirmLabel: "确认",
    cancelLabel: "取消",
    busyLabel: "处理中...",
    tone: "default",
    busy: false
  }
);

const emit = defineEmits<{ close: []; confirm: [] }>();

function handleClose() {
  if (props.busy) return;
  emit("close");
}
</script>
