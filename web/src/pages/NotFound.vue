<template>
  <section class="not-found page-grid">
    <div>
      <span class="eyebrow">404 / ROUTE LOST</span>
      <h1>这条数据路径没有接入控制面。</h1>
      <p>返回市场或首页，重新进入一条有效的数据流。</p>
      <div class="hero-actions">
        <RouterLink class="primary-action" to="/catalog">数据市场</RouterLink>
        <RouterLink class="secondary-action" to="/">首页</RouterLink>
      </div>
    </div>
  </section>
</template>
