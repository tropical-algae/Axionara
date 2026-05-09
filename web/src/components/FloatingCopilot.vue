<template>
  <button ref="buttonRef" class="copilot-button" type="button" aria-label="打开问答" @click="open">
    <MessageCircle :size="25" />
  </button>

  <Teleport to="body">
    <div v-show="ui.copilotOpen" ref="overlayRef" class="copilot-overlay" @click.self="close">
      <aside ref="drawerRef" class="copilot-drawer">
        <header>
          <div>
            <span>AXIONARA COPILOT</span>
            <strong>{{ title }}</strong>
          </div>
          <button type="button" @click="close"><X :size="20" /></button>
        </header>

        <div class="messages">
          <article v-for="message in messages" :key="message.id" :class="message.role">
            <span>{{ message.role === "user" ? "YOU" : "AI" }}</span>
            <p>{{ message.text }}</p>
          </article>
        </div>

        <form class="chat-compose" @submit.prevent="send">
          <textarea v-model="draft" rows="3" placeholder="询问这个页面中的数据、可用字段、风险与导出建议..." />
          <button type="submit" :disabled="sending || !draft.trim()">
            <Send :size="17" />
            发送
          </button>
        </form>
      </aside>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import gsap from "gsap";
import { MessageCircle, Send, X } from "lucide-vue-next";
import { computed, nextTick, ref, watch } from "vue";

import { useCatalogStore } from "@/stores/catalog";
import { useMeStore } from "@/stores/me";
import { useUiStore } from "@/stores/ui";

const ui = useUiStore();
const catalog = useCatalogStore();
const me = useMeStore();
const overlayRef = ref<HTMLElement | null>(null);
const drawerRef = ref<HTMLElement | null>(null);
const buttonRef = ref<HTMLElement | null>(null);
const draft = ref("");
const sending = ref(false);
const messages = ref([
  { id: "seed", role: "assistant", text: "我会根据当前页面选择公开市场、公开数据详情或授权数据内容作为问答范围。" }
]);

const title = computed(() => {
  if (ui.chatContext === "catalog") return "数据市场问答";
  if (ui.chatContext === "catalog-detail") return "公开资产问答";
  if (ui.chatContext === "me-detail") return "授权内容问答";
  return "平台助手";
});

function open() {
  ui.openCopilot();
}

function close() {
  ui.closeCopilot();
}

async function send() {
  const question = draft.value.trim();
  if (!question) return;
  messages.value.push({ id: crypto.randomUUID(), role: "user", text: question });
  draft.value = "";
  sending.value = true;
  try {
    const response =
      ui.chatContext === "me-detail" && ui.chatDatasetId
        ? await me.ask(ui.chatDatasetId, question)
        : await catalog.ask(question, ui.chatContext === "catalog-detail" ? ui.chatDatasetId ?? undefined : undefined);
    messages.value.push({ id: crypto.randomUUID(), role: "assistant", text: response.answer || "没有获得可用回答。" });
  } catch (error) {
    messages.value.push({ id: crypto.randomUUID(), role: "assistant", text: error instanceof Error ? error.message : "问答服务暂不可用。" });
  } finally {
    sending.value = false;
  }
}

watch(
  () => ui.copilotOpen,
  async (openNow) => {
    await nextTick();
    if (!overlayRef.value || !drawerRef.value) return;
    if (openNow) {
      gsap.fromTo(overlayRef.value, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.28, ease: "power2.out" });
      gsap.fromTo(drawerRef.value, { xPercent: 105 }, { xPercent: 0, duration: 0.62, ease: "expo.out" });
    } else {
      gsap.set(overlayRef.value, { autoAlpha: 0 });
      gsap.set(drawerRef.value, { xPercent: 105 });
    }
  }
);

watch(
  () => ui.chatContext,
  () => {
    messages.value = [{ id: crypto.randomUUID(), role: "assistant", text: `当前范围已切换为：${title.value}。` }];
  }
);
</script>
