<template>
  <section class="home-hero page-grid">
    <div class="hero-copy">
      <span class="eyebrow">DATA REFINERY / AGENTIC INTELLIGENCE</span>
      <h1>把原始数据炼成可交易、可审查、可问答的资产</h1>
      <p>Axionara 将上传、解析、清洗、风险审查、发布、授权、规范化导出，全部压缩进一个可运营的数据要素控制面板</p>
      <p>基于 Agent 的知识问答，让你轻松掌握全部</p>
      <div class="hero-actions">
        <RouterLink class="primary-action" to="/catalog">进入数据市场</RouterLink>
        <RouterLink class="secondary-action" to="/register">创建角色身份</RouterLink>
      </div>
    </div>

    <div class="command-radar">
      <div class="radar-core">
        <span>AX</span>
      </div>
      <article v-for="node in nodes" :key="node.title">
        <component :is="node.icon" :size="20" />
        <strong>{{ node.title }}</strong>
        <span>{{ node.copy }}</span>
      </article>
    </div>

    <div class="system-strip">
      <MetricTile label="Pipeline" value="7 stages" caption="ingest / parse / clean / review / publish" />
      <MetricTile label="Markets" value="Public + Vault" caption="公开发现与授权使用分离" />
      <MetricTile label="AI Layer" value="RAG ready" caption="面向资产的上下文问答" />
    </div>
  </section>
</template>

<script setup lang="ts">
import { BrainCircuit, DatabaseZap, FileCheck2, ShieldCheck } from "lucide-vue-next";

import MetricTile from "@/components/MetricTile.vue";

const nodes = [
  { icon: DatabaseZap, title: "数据摄入", copy: "提供者上传原始文件" },
  { icon: BrainCircuit, title: "智能分析", copy: "结构、质量、标签、摘要" },
  { icon: ShieldCheck, title: "审核发布", copy: "管理员控制风险边界" },
  { icon: FileCheck2, title: "授权导出", copy: "使用者获取与转换" }
];
</script>
