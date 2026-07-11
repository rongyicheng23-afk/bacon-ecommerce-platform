<script setup lang="ts">
import { nextTick, ref } from 'vue'

const messages = ref<Array<{ role: 'user' | 'agent'; text: string; time: string }>>([])
const inputText = ref('')
const chatBody = ref<HTMLElement | null>(null)

const faqList = [
  { q: '如何查询物流信息？', a: '您可以在"我的订单"中点击具体订单查看物流状态和快递单号。' },
  { q: '支持哪些支付方式？', a: '目前支持微信支付、支付宝和银行卡支付，更多方式陆续开放中。' },
  { q: '退换货政策是怎样的？', a: '签收后 7 天内可申请退换货，商品需保持原包装完整，详情请查看售后政策。' },
  { q: '如何修改收货地址？', a: '下单前可在"个人中心 → 收货地址"中修改，已发货订单暂不支持修改地址。' },
  { q: '优惠券如何使用？', a: '结算页面会自动匹配可用优惠券，您也可以手动选择需要使用的优惠券。' },
  { q: '客服工作时间？', a: '在线客服工作时间为每天 9:00 - 22:00，非工作时间可留言，我们会尽快回复。' },
]

const sendMessage = () => {
  const text = inputText.value.trim()
  if (!text) return

  const now = new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  messages.value.push({ role: 'user', text, time: now })
  inputText.value = ''

  // auto reply
  setTimeout(() => {
    const reply = getAutoReply(text)
    messages.value.push({ role: 'agent', text: reply, time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }) })
    scrollBottom()
  }, 800)

  scrollBottom()
}

const getAutoReply = (q: string): string => {
  const lower = q.toLowerCase()
  if (lower.includes('物流') || lower.includes('快递') || lower.includes('配送')) return faqList[0].a
  if (lower.includes('支付') || lower.includes('付款')) return faqList[1].a
  if (lower.includes('退') || lower.includes('换') || lower.includes('货')) return faqList[2].a
  if (lower.includes('地址') || lower.includes('收货')) return faqList[3].a
  if (lower.includes('优惠') || lower.includes('券') || lower.includes('折扣')) return faqList[4].a
  return '收到您的消息，客服会在工作时间内尽快回复。您也可以查看下方常见问题，或拨打客服热线 400-888-8888。'
}

const loadFaqReply = (faq: { q: string; a: string }) => {
  const now = new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  messages.value.push({ role: 'user', text: faq.q, time: now })
  setTimeout(() => {
    messages.value.push({ role: 'agent', text: faq.a, time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }) })
    scrollBottom()
  }, 400)
  scrollBottom()
}

const scrollBottom = () => {
  nextTick(() => {
    if (chatBody.value) chatBody.value.scrollTop = chatBody.value.scrollHeight
  })
}

const startChat = () => {
  if (messages.value.length > 0) return
  const now = new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  messages.value.push({ role: 'agent', text: '您好！我是 Bacon Mall 智能客服小B，有什么可以帮您的？您可以直接输入问题，也可以点击下方常见问题快速获取答案。', time: now })
}
</script>

<template>
  <div class="cs-page">
    <div class="cs-hero">
      <h1>🎧 客服中心</h1>
      <p>智能客服 7×24 小时在线 · 人工客服 9:00-22:00</p>
    </div>

    <div class="cs-layout">
      <!-- chat panel -->
      <div class="cs-chat">
        <div class="chat-header">
          <span class="chat-agent-avatar">🤖</span>
          <div>
            <strong>Bacon 小B助手</strong>
            <small>智能客服 · 在线</small>
          </div>
        </div>

        <div ref="chatBody" class="chat-body" @vue:mounted="startChat">
          <div
            v-for="(msg, i) in messages"
            :key="i"
            :class="['chat-bubble', msg.role]"
          >
            <span class="bubble-avatar">{{ msg.role === 'agent' ? '🤖' : '👤' }}</span>
            <div class="bubble-content">
              <p>{{ msg.text }}</p>
              <span class="bubble-time">{{ msg.time }}</span>
            </div>
          </div>
        </div>

        <div class="chat-input">
          <input
            v-model="inputText"
            type="text"
            placeholder="输入您的问题…"
            @keyup.enter="sendMessage"
          />
          <button @click="sendMessage">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
          </button>
        </div>
      </div>

      <!-- faq panel -->
      <div class="cs-faq">
        <h3>常见问题</h3>
        <div class="faq-list">
          <button
            v-for="(faq, i) in faqList"
            :key="i"
            class="faq-item"
            @click="loadFaqReply(faq)"
          >
            <span class="faq-q">{{ faq.q }}</span>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polyline points="9 18 15 12 9 6"/></svg>
          </button>
        </div>

        <div class="cs-contact">
          <h4>其他联系方式</h4>
          <p>📞 客服热线：400-888-8888</p>
          <p>📧 邮箱：support@baconmall.com</p>
          <p>🕐 工作时间：每天 9:00 - 22:00</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.cs-page {
  max-width: 1000px;
  margin: 0 auto;
}

.cs-hero {
  margin-bottom: 1.5rem;
}

.cs-hero h1 {
  margin: 0 0 0.25rem;
  color: #241B2F;
  font-size: 1.5rem;
}

.cs-hero p {
  margin: 0;
  color: #756D7E;
  font-size: 0.9rem;
}

.cs-layout {
  display: grid;
  grid-template-columns: 1fr 280px;
  gap: 1.5rem;
  align-items: start;
}

/* ---- chat panel ---- */
.cs-chat {
  border: 1px solid #E9E4EE;
  border-radius: 14px;
  background: #fff;
  box-shadow: 0 4px 16px rgba(15, 23, 42, 0.05);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.chat-header {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.9rem 1.15rem;
  border-bottom: 1px solid #E9E4EE;
  background: #fafbfc;
}

.chat-agent-avatar { font-size: 1.6rem; }

.chat-header strong {
  display: block;
  color: #241B2F;
  font-size: 0.9rem;
}

.chat-header small {
  color: #980B32;
  font-size: 0.74rem;
  font-weight: 700;
}

.chat-body {
  flex: 1;
  min-height: 340px;
  max-height: 440px;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  background: #fafbfd;
}

.chat-bubble {
  display: flex;
  gap: 0.5rem;
  max-width: 85%;
}

.chat-bubble.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.chat-bubble.agent {
  align-self: flex-start;
}

.bubble-avatar {
  font-size: 1.2rem;
  flex-shrink: 0;
  align-self: flex-end;
}

.bubble-content {
  padding: 0.65rem 0.9rem;
  border-radius: 14px;
  font-size: 0.86rem;
  line-height: 1.55;
}

.chat-bubble.agent .bubble-content {
  background: #fff;
  border: 1px solid #E9E4EE;
  border-bottom-left-radius: 4px;
  color: #241B2F;
}

.chat-bubble.user .bubble-content {
  background: #980B32;
  color: #fff;
  border-bottom-right-radius: 4px;
}

.bubble-content p {
  margin: 0;
}

.bubble-time {
  display: block;
  margin-top: 4px;
  font-size: 0.68rem;
  opacity: 0.6;
  text-align: right;
}

.chat-input {
  display: flex;
  padding: 0.65rem 1rem;
  border-top: 1px solid #E9E4EE;
  gap: 0.5rem;
  background: #fff;
}

.chat-input input {
  flex: 1;
  min-height: 40px;
  padding: 0 1rem;
  border: 1px solid #948B9D;
  border-radius: 999px;
  background: #fafafa;
  color: #241B2F;
  font-size: 0.88rem;
  outline: none;
}

.chat-input input:focus {
  border-color: #980B32;
  background: #fff;
}

.chat-input button {
  display: grid;
  width: 40px;
  height: 40px;
  place-items: center;
  border: 0;
  border-radius: 50%;
  background: #980B32;
  color: #fff;
  cursor: pointer;
  flex-shrink: 0;
}

.chat-input button svg {
  width: 18px;
  height: 18px;
}

/* ---- faq panel ---- */
.cs-faq {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.cs-faq h3 {
  margin: 0;
  color: #241B2F;
  font-size: 1rem;
  font-weight: 900;
}

.faq-list {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.faq-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0.9rem;
  border: 1px solid #E9E4EE;
  border-radius: 10px;
  background: #fff;
  color: #241B2F;
  cursor: pointer;
  text-align: left;
  transition: all 0.15s ease;
}

.faq-item:hover {
  border-color: #980B32;
  background: #F4EFF7;
}

.faq-q {
  font-size: 0.84rem;
  font-weight: 700;
  flex: 1;
}

.faq-item svg {
  width: 14px;
  height: 14px;
  color: #ccc;
  flex-shrink: 0;
}

.cs-contact {
  padding: 1rem;
  border-radius: 12px;
  background: #f8fafc;
  border: 1px solid #E9E4EE;
}

.cs-contact h4 {
  margin: 0 0 0.5rem;
  color: #241B2F;
  font-size: 0.85rem;
  font-weight: 900;
}

.cs-contact p {
  margin: 0.25rem 0;
  color: #756D7E;
  font-size: 0.8rem;
}

@media (max-width: 768px) {
  .cs-layout {
    grid-template-columns: 1fr;
  }
}
</style>
