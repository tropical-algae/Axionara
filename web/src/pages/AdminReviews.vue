<template>
  <section class="ops-layout page-grid">
    <header class="section-header span-all"><div><span class="eyebrow">REVIEW LEDGER</span><h1>审核记录</h1></div></header>
    <main class="ops-board span-all">
      <div class="asset-list">
        <article v-for="review in admin.reviews" :key="review.id" class="list-card">
          <StatusBadge :status="review.review_status" />
          <div><h3>{{ review.dataset_id }}</h3><p>{{ review.review_comment || review.publish_comment || "无审核备注" }}</p></div>
          <span>{{ dateTime(review.reviewed_at || review.published_at || review.create_date) }}</span>
        </article>
      </div>
    </main>
  </section>
</template>

<script setup lang="ts">
import { onMounted } from "vue";

import StatusBadge from "@/components/StatusBadge.vue";
import { useAdminStore } from "@/stores/admin";
import { dateTime } from "@/utils/format";

const admin = useAdminStore();
onMounted(() => admin.loadReviews());
</script>
