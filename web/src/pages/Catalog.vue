<template>
  <section class="catalog-layout page-grid">
    <aside class="market-filters">
      <span class="eyebrow">MARKET FILTERS</span>
      <h2>展开筛选</h2>
      <input v-model="keyword" class="search-input" placeholder="搜索标题、摘要、标签..." @keyup.enter="apply" />

      <div class="filter-block">
        <strong>分类</strong>
        <button :class="{ active: !query.category }" @click="setFilter('category', undefined)">全部</button>
        <button v-for="category in catalog.categories" :key="category" :class="{ active: query.category === category }" @click="setFilter('category', category)">
          {{ category }}
        </button>
      </div>

      <div class="filter-block">
        <strong>标签</strong>
        <button :class="{ active: !query.tag_slug }" @click="setFilter('tag_slug', undefined)">全部</button>
        <button v-for="tag in catalog.tags" :key="tag.slug" :class="{ active: query.tag_slug === tag.slug }" @click="setFilter('tag_slug', tag.slug)">
          {{ tag.name }}
        </button>
      </div>

      <div class="filter-block">
        <strong>格式</strong>
        <button :class="{ active: !query.source_format }" @click="setFilter('source_format', undefined)">全部</button>
        <button v-for="format in formats" :key="format" :class="{ active: query.source_format === format }" @click="setFilter('source_format', format)">
          {{ format.toUpperCase() }}
        </button>
      </div>
    </aside>

    <main class="market-main">
      <header class="section-header">
        <div>
          <span class="eyebrow">PUBLIC DATA EXCHANGE</span>
          <h1>数据市场</h1>
        </div>
        <button class="icon-text" type="button" @click="ui.openCopilot('catalog')"><Bot :size="16" />市场问答</button>
      </header>

      <LoadingState v-if="catalog.loading" />
      <EmptyState v-else-if="!catalog.datasets.length" title="暂无公开资产" description="调整筛选条件，或等待管理员发布新的数据集。" />
      <div v-else class="asset-grid">
        <DataCard v-for="item in catalog.datasets" :key="item.dataset.id" :item="item" :to="`/catalog/${item.dataset.id}`" />
      </div>
    </main>

    <aside class="market-intel">
      <MetricTile label="Assets" :value="catalog.datasets.length" caption="当前筛选结果" intense />
      <MetricTile label="Tags" :value="catalog.tags.length" caption="公开主题维度" />
      <div class="intel-panel">
        <strong>市场观察</strong>
        <p>筛选已完全展开，分类、标签和格式直接暴露在页面中，便于快速扫视公开数据结构。</p>
      </div>
      <div class="tag-cloud">
        <span v-for="tag in catalog.tags.slice(0, 18)" :key="tag.slug">{{ tag.name }}</span>
      </div>
    </aside>
  </section>
</template>

<script setup lang="ts">
import { Bot } from "lucide-vue-next";
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from "vue";

import DataCard from "@/components/DataCard.vue";
import EmptyState from "@/components/EmptyState.vue";
import LoadingState from "@/components/LoadingState.vue";
import MetricTile from "@/components/MetricTile.vue";
import type { CatalogQuery } from "@/api/types";
import { useCatalogStore } from "@/stores/catalog";
import { useUiStore } from "@/stores/ui";

const catalog = useCatalogStore();
const ui = useUiStore();
const query = reactive<CatalogQuery>({});
const keyword = ref("");
const formats = computed(() => catalog.formats.length ? catalog.formats : ["csv", "json", "pdf", "xlsx"]);
let searchTimer: number | undefined;

function apply() {
  query.keyword = keyword.value || undefined;
  catalog.loadDatasets(query);
}

function setFilter(key: keyof CatalogQuery, value?: string) {
  query[key] = value;
  apply();
}

onMounted(async () => {
  ui.setContext("catalog");
  await Promise.all([catalog.loadTags().catch(() => undefined), catalog.loadDatasets()]);
});

watch(keyword, () => {
  window.clearTimeout(searchTimer);
  searchTimer = window.setTimeout(apply, 260);
});

onBeforeUnmount(() => {
  window.clearTimeout(searchTimer);
});
</script>
