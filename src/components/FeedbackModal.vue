<script setup lang="ts">
import { ref } from 'vue'

const visible = defineModel<boolean>({ required: true })

const type = ref('suggestion')
const content = ref('')
const contact = ref('')
const submitted = ref(false)

const feedbackTypes = [
  { value: 'suggestion', label: '功能建议' },
  { value: 'bug', label: '问题反馈' },
  { value: 'experience', label: '体验评价' },
  { value: 'other', label: '其他' },
]

const close = () => {
  visible.value = false
}

const submit = () => {
  if (!content.value.trim()) return
  // store locally as mock
  const feedbacks = JSON.parse(localStorage.getItem('feedbacks') || '[]')
  feedbacks.push({
    type: type.value,
    content: content.value.trim(),
    contact: contact.value.trim(),
    time: new Date().toISOString(),
  })
  localStorage.setItem('feedbacks', JSON.stringify(feedbacks))
  submitted.value = true
  content.value = ''
  contact.value = ''
}

const reset = () => {
  submitted.value = false
  content.value = ''
  contact.value = ''
}

defineExpose({ open: () => { visible.value = true; submitted.value = false } })
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="visible" class="feedback-overlay" @click.self="close">
        <div class="feedback-modal">
          <div class="modal-header">
            <h2>帮助与反馈</h2>
            <button type="button" class="modal-close" @click="close">✕</button>
          </div>

          <template v-if="!submitted">
            <div class="modal-body">
              <div class="field">
                <label>反馈类型</label>
                <div class="type-options">
                  <button
                    v-for="t in feedbackTypes"
                    :key="t.value"
                    type="button"
                    :class="['type-btn', { active: type === t.value }]"
                    @click="type = t.value"
                  >{{ t.label }}</button>
                </div>
              </div>

              <div class="field">
                <label for="fb-content">详细描述</label>
                <textarea
                  id="fb-content"
                  v-model="content"
                  rows="5"
                  placeholder="请描述您的建议或遇到的问题…"
                ></textarea>
              </div>

              <div class="field">
                <label for="fb-contact">联系方式（选填）</label>
                <input
                  id="fb-contact"
                  v-model="contact"
                  type="text"
                  placeholder="手机号 / 邮箱"
                />
              </div>
            </div>

            <div class="modal-footer">
              <button type="button" class="btn-cancel" @click="close">取消</button>
              <button type="button" class="btn-submit" @click="submit">提交反馈</button>
            </div>
          </template>

          <template v-else>
            <div class="modal-body success-state">
              <span class="success-icon">✅</span>
              <h3>感谢您的反馈</h3>
              <p>我们会尽快处理，如有需要会通过您留的联系方式回复。</p>
              <button type="button" class="btn-submit" @click="reset">继续反馈</button>
            </div>
          </template>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.feedback-overlay {
  position: fixed;
  inset: 0;
  z-index: 200;
  display: grid;
  place-items: center;
  background: rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(4px);
}

.feedback-modal {
  width: min(480px, calc(100vw - 40px));
  max-height: calc(100vh - 80px);
  overflow-y: auto;
  border-radius: 18px;
  background: #fff;
  box-shadow: 0 24px 60px rgba(15, 23, 42, 0.25);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #f1f2f4;
}

.modal-header h2 {
  margin: 0;
  color: #0f172a;
  font-size: 1.15rem;
  font-weight: 900;
}

.modal-close {
  display: grid;
  width: 32px;
  height: 32px;
  place-items: center;
  border: 0;
  border-radius: 50%;
  background: #f7f8fa;
  color: #999;
  cursor: pointer;
  font-size: 0.85rem;
}

.modal-close:hover {
  background: #fff1f2;
  color: #ff2f68;
}

.modal-body {
  padding: 1.25rem 1.5rem;
}

.field {
  margin-bottom: 1rem;
}

.field label {
  display: block;
  margin-bottom: 0.5rem;
  color: #333;
  font-size: 0.88rem;
  font-weight: 800;
}

.type-options {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.type-btn {
  min-height: 34px;
  padding: 0 0.85rem;
  border: 1px solid #e5e7eb;
  border-radius: 999px;
  background: #fff;
  color: #64748b;
  cursor: pointer;
  font-size: 0.84rem;
  font-weight: 700;
  transition: all 0.15s ease;
}

.type-btn.active {
  border-color: #ff2f68;
  background: #fff2f5;
  color: #ff2f68;
}

.type-btn:hover:not(.active) {
  border-color: #ccc;
}

.field textarea,
.field input[type='text'] {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  background: #fafafa;
  color: #0f172a;
  font: inherit;
  font-size: 0.9rem;
  outline: none;
  resize: vertical;
  box-sizing: border-box;
}

.field textarea:focus,
.field input:focus {
  border-color: #ff2f68;
  background: #fff;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid #f1f2f4;
}

.btn-cancel {
  min-height: 38px;
  padding: 0 1.25rem;
  border: 1px solid #e5e7eb;
  border-radius: 999px;
  background: #fff;
  color: #64748b;
  cursor: pointer;
  font-size: 0.88rem;
  font-weight: 700;
}

.btn-submit {
  min-height: 38px;
  padding: 0 1.5rem;
  border: 0;
  border-radius: 999px;
  background: #ff2f68;
  color: #fff;
  cursor: pointer;
  font-size: 0.88rem;
  font-weight: 800;
}

.btn-submit:hover {
  background: #e8254a;
}

.success-state {
  text-align: center;
  padding: 2.5rem 1.5rem;
}

.success-icon {
  font-size: 2.5rem;
}

.success-state h3 {
  margin: 0.75rem 0 0.5rem;
  color: #0f172a;
  font-size: 1.1rem;
}

.success-state p {
  margin: 0 0 1.5rem;
  color: #777;
  font-size: 0.9rem;
  line-height: 1.6;
}

/* modal transition */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.25s ease;
}

.modal-enter-active .feedback-modal,
.modal-leave-active .feedback-modal {
  transition: transform 0.25s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .feedback-modal {
  transform: scale(0.94) translateY(20px);
}

.modal-leave-to .feedback-modal {
  transform: scale(0.94) translateY(20px);
}
</style>
