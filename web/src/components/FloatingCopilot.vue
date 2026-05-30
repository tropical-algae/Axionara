<template>
  <button ref="buttonRef" class="copilot-button" type="button" aria-label="打开问答" @click="open">
    <MessageCircle :size="25" />
  </button>

  <Teleport to="body">
    <div v-if="renderCopilot" ref="overlayRef" class="copilot-overlay" @click.self="close">
      <aside ref="drawerRef" class="copilot-drawer">
        <header>
          <div class="copilot-heading">
            <img class="copilot-logo" src="/axionara.svg" alt="" aria-hidden="true" />
            <div>
              <span>AXIONARA COPILOT</span>
              <strong>{{ title }}</strong>
            </div>
          </div>
          <button type="button" @click="close"><X :size="20" /></button>
        </header>

        <div class="messages">
          <article v-for="message in messages" :key="message.id" :class="[message.role, { streaming: message.streaming }]">
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
import { computed, nextTick, onBeforeUnmount, ref, watch } from "vue";

import { catalogApi, meApi } from "@/api/services";
import { useCatalogStore } from "@/stores/catalog";
import { useUiStore } from "@/stores/ui";

const ui = useUiStore();
const catalog = useCatalogStore();
const overlayRef = ref<HTMLElement | null>(null);
const drawerRef = ref<HTMLElement | null>(null);
const buttonRef = ref<HTMLElement | null>(null);
const renderCopilot = ref(ui.copilotOpen);
let copilotTimeline: gsap.core.Timeline | null = null;
type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  text: string;
  streaming?: boolean;
};

const draft = ref("");
const sending = ref(false);
const messages = ref<ChatMessage[]>([
  { id: "seed", role: "assistant", text: "我会根据当前页面选择公开市场、公开数据详情或授权数据内容作为问答范围。" }
]);
let activeStreamController: AbortController | null = null;

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

function findMessage(id: string) {
  return messages.value.find((message) => message.id === id);
}

function appendAssistantDelta(messageId: string, delta: string) {
  const message = findMessage(messageId);
  if (message) message.text += delta;
}

function finishAssistantMessage(messageId: string) {
  const message = findMessage(messageId);
  if (!message) return;
  message.streaming = false;
  if (!message.text.trim()) message.text = "没有获得可用回答。";
}

function abortActiveStream() {
  activeStreamController?.abort();
  activeStreamController = null;
}

async function send() {
  const question = draft.value.trim();
  if (!question || sending.value) return;
  abortActiveStream();

  const assistantMessageId = crypto.randomUUID();
  const controller = new AbortController();
  activeStreamController = controller;
  messages.value.push(
    { id: crypto.randomUUID(), role: "user", text: question },
    { id: assistantMessageId, role: "assistant", text: "", streaming: true }
  );
  draft.value = "";
  sending.value = true;

  try {
    if (ui.chatContext === "me-detail" && ui.chatDatasetId) {
      await meApi.askStream(ui.chatDatasetId, question, (delta) => appendAssistantDelta(assistantMessageId, delta), undefined, controller.signal);
    } else if (ui.chatContext === "catalog-detail" && ui.chatDatasetId) {
      await catalogApi.askDatasetStream(ui.chatDatasetId, question, (delta) => appendAssistantDelta(assistantMessageId, delta), undefined, controller.signal);
    } else {
      await catalogApi.askStream(question, undefined, catalog.query.tag_slug, (delta) => appendAssistantDelta(assistantMessageId, delta), undefined, controller.signal);
    }
    finishAssistantMessage(assistantMessageId);
  } catch (error) {
    if (controller.signal.aborted) return;
    const assistantMessage = findMessage(assistantMessageId);
    if (assistantMessage) {
      assistantMessage.streaming = false;
      assistantMessage.text = error instanceof Error ? error.message : "问答服务暂不可用。";
    }
  } finally {
    if (activeStreamController === controller) activeStreamController = null;
    sending.value = false;
  }
}


watch(
  () => ui.copilotOpen,
  async (openNow) => {
    copilotTimeline?.kill();
    if (openNow) {
      renderCopilot.value = true;
      await nextTick();
      if (!overlayRef.value || !drawerRef.value) return;
      gsap.set(overlayRef.value, { autoAlpha: 0 });
      gsap.set(drawerRef.value, { xPercent: 100, force3D: true });
      copilotTimeline = gsap
        .timeline()
        .to(overlayRef.value, { autoAlpha: 1, duration: 0.16, ease: "power1.out" }, 0)
        .to(drawerRef.value, { xPercent: 0, duration: 0.34, ease: "power3.out", force3D: true }, 0);
      return;
    }

    if (!overlayRef.value || !drawerRef.value) {
      renderCopilot.value = false;
      return;
    }
    copilotTimeline = gsap
      .timeline({
        onComplete: () => {
          renderCopilot.value = false;
        }
      })
      .to(drawerRef.value, { xPercent: 100, duration: 0.24, ease: "power2.in", force3D: true }, 0)
      .to(overlayRef.value, { autoAlpha: 0, duration: 0.2, ease: "power1.out" }, 0);
  }
);

watch(
  () => ui.chatContext,
  () => {
    abortActiveStream();
    messages.value = [{ id: crypto.randomUUID(), role: "assistant", text: `当前范围已切换为：${title.value}。` }];
  }
);

onBeforeUnmount(() => {
  abortActiveStream();
  copilotTimeline?.kill();
});
</script>
