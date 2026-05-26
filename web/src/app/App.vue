<template>
  <SceneBackdrop :tone="ui.pageTone" />
  <div class="app-frame">
    <AppShell>
      <RouterView v-slot="{ Component, route }">
        <Transition :css="false" mode="out-in" @before-enter="onBeforeEnter" @enter="onEnter" @leave="onLeave">
          <component :is="Component" :key="route.fullPath" />
        </Transition>
      </RouterView>
    </AppShell>
    <FloatingCopilot />
  </div>
</template>

<script setup lang="ts">
import gsap from "gsap";

import AppShell from "@/components/AppShell.vue";
import FloatingCopilot from "@/components/FloatingCopilot.vue";
import SceneBackdrop from "@/components/SceneBackdrop.vue";
import { useUiStore } from "@/stores/ui";

const ui = useUiStore();

function onBeforeEnter(el: Element) {
  gsap.killTweensOf(el);
  gsap.set(el, { autoAlpha: 0, y: 18, filter: "saturate(0.92)" });
}

function onEnter(el: Element, done: () => void) {
  gsap.killTweensOf(el);
  gsap.to(
    el,
    {
      autoAlpha: 1,
      y: 0,
      filter: "saturate(1)",
      duration: 0.36,
      ease: "power3.out",
      onComplete: () => {
        gsap.set(el, { clearProps: "opacity,visibility,transform,filter" });
        done();
      }
    }
  );
}

function onLeave(el: Element, done: () => void) {
  gsap.killTweensOf(el);
  gsap.to(el, {
    autoAlpha: 0,
    y: -8,
    duration: 0.18,
    ease: "power2.in",
    onComplete: done
  });
}
</script>
