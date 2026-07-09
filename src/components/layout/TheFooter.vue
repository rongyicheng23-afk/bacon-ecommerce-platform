<template>
  <footer class="footer">
    <div class="footer-content">
      <section class="footer-section">
        <h3>Bacon Mall</h3>
        <p>面向专业实习2的网页端电商平台，后续接入 FastAPI、SQLite 和 Hadoop 离线推荐流程。</p>
      </section>

      <section class="footer-section">
        <h3>核心能力</h3>
        <p>商品浏览、搜索筛选、购物车、订单管理、用户行为日志和个性化推荐。</p>
      </section>

      <section class="footer-section">
        <h3>快速入口</h3>
        <router-link to="/">首页</router-link>
        <router-link to="/products">全部商品</router-link>
        <router-link to="/cart">购物车</router-link>
        <router-link to="/orders">我的订单</router-link>
      </section>
    </div>

    <div class="footer-bottom">
      <p>&copy; 2026 Bacon Mall. Professional Internship Project.</p>
    </div>
  </footer>
</template>

<style scoped>
.footer {
  margin-top: 4rem;
  padding: 3rem 0 1rem;
  background-color: #fff;
  border-top: 1px solid #eceff3;
}

.footer-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
}

.footer-section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.footer-section h3 {
  margin: 0;
  color: #111827;
  font-size: 1.1rem;
}

.footer-section p,
.footer-section a {
  color: #666;
  font-size: 0.92rem;
  line-height: 1.6;
}

.footer-section a {
  text-decoration: none;
}

.footer-section a:hover {
  color: var(--primary-color);
}

.footer-bottom {
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #eceff3;
  color: #999;
  text-align: center;
}

.footer-bottom p {
  margin: 0;
  font-size: 0.86rem;
}
</style>
