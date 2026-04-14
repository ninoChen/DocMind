<template>
  <el-container class="app-wrapper">
    <el-aside width="280px" class="aside-panel">
      <div class="panel-header">
        <h3>🚀 AI 知识库</h3>
      </div>
      
      <div class="panel-content">
        <p class="section-title">1. 选择路由分类</p>
        <el-select v-model="category" class="w-full mb-4">
          <el-option label="技术文档 (TECHNICAL)" value="TECHNICAL" />
          <el-option label="人事制度 (PERSONNEL)" value="PERSONNEL" />
        </el-select>

        <p class="section-title">2. 上传参考文档</p>
        <el-upload
          drag
          action="http://127.0.0.1:8000/upload"
          :data="{ category: category }"
          accept=".pdf"
          :on-success="onUploadSuccess"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">拖拽 PDF 到此处或 <em>点击上传</em></div>
        </el-upload>
      </div>
    </el-aside>

    <el-main class="chat-container">
      <div class="chat-body" ref="scrollBox">
        <div v-for="(item, index) in chatList" :key="index" :class="['msg-row', item.role]">
          <div class="msg-avatar shadow-sm">
            {{ item.role === 'user' ? 'ME' : 'AI' }}
          </div>
          <div class="msg-content shadow-sm">{{ item.content }}</div>
        </div>
      </div>

      <div class="chat-footer">
        <el-input
          v-model="inputMsg"
          placeholder="请输入你的问题..."
          size="large"
          @keyup.enter="handleSend"
          :disabled="isTalking"
        >
          <template #append>
            <el-button @click="handleSend" type="primary" :loading="isTalking">
              发送
            </el-button>
          </template>
        </el-input>
      </div>
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { ref, nextTick, reactive } from 'vue'
import { UploadFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// --- 状态定义 ---
const category = ref('TECHNICAL')
const inputMsg = ref('')
const isTalking = ref(false) // 对话状态锁
const scrollBox = ref<HTMLElement | null>(null)
// 使用 reactive 增强消息列表的响应式灵敏度
const chatList = reactive<{ role: 'user' | 'assistant'; content: string }[]>([])

// --- 自动滚动函数 ---
const autoScroll = async () => {
  await nextTick()
  if (scrollBox.value) {
    scrollBox.value.scrollTop = scrollBox.value.scrollHeight
  }
}

// --- 事件处理 ---
const onUploadSuccess = () => {
  ElMessage.success('文档已成功入库并生成向量索引')
}

const handleSend = async () => {
  if (!inputMsg.value.trim() || isTalking.value) return

  const userText = inputMsg.value
  isTalking.value = true
  
  // 1. 用户消息入场
  chatList.push({ role: 'user', content: userText })
  inputMsg.value = ''
  await autoScroll()

  // 2. AI 消息占位（使用 reactive 对象确保属性变更能被 Vue 捕获）
  const aiResponse = reactive({ role: 'assistant' as const, content: '' })
  chatList.push(aiResponse)

  // 3. 构建请求
  const formData = new FormData()
  formData.append('message', userText)

  try {
    const res = await fetch('http://127.0.0.1:8000/chat', {
      method: 'POST',
      body: formData
    })

    if (!res.body) throw new Error('ReadableStream 异常')
    
    const reader = res.body.getReader()
    const decoder = new TextDecoder()

    // 4. 读取流数据
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      
      const chunk = decoder.decode(value)
      const lines = chunk.split('\n')
      
      for (const line of lines) {
        if (line.trim().startsWith('data: ')) {
          try {
            const jsonStr = line.substring(6).trim()
            if (!jsonStr) continue
            
            const data = JSON.parse(jsonStr)
            if (data.content) {
              // 逐字追加内容
              aiResponse.content += data.content
              // 每一帧都尝试滚动，确保 UI 同步渲染
              autoScroll()
            }
          } catch (e) {
            console.warn("JSON 数据帧解析失败:", e)
          }
        }
      }
    }
  } catch (err) {
    aiResponse.content = "❌ 连接后端失败，请检查 8000 端口服务是否已启动。"
    console.error(err)
  } finally {
    isTalking.value = false
    autoScroll()
  }
}
</script>

<style scoped>
/* 容器布局 */
.app-wrapper { height: 100vh; background-color: #f0f2f5; overflow: hidden; }

/* 侧边栏样式 */
.aside-panel { background: #fff; border-right: 1px solid #e4e7ed; display: flex; flex-direction: column; }
.panel-header { padding: 25px 20px; border-bottom: 1px solid #f0f0f0; }
.panel-header h3 { margin: 0; color: #409eff; font-size: 20px; }
.panel-content { padding: 20px; }
.section-title { font-size: 13px; color: #909399; margin-bottom: 12px; font-weight: bold; }

/* 聊天主区域 */
.chat-container { display: flex; flex-direction: column; padding: 0; background: #fdfdfd; }
.chat-body { flex: 1; overflow-y: auto; padding: 40px 60px; scroll-behavior: smooth; }

/* 消息行样式 */
.msg-row { display: flex; margin-bottom: 30px; align-items: flex-start; }
.msg-row.user { flex-direction: row-reverse; }

/* 头像 */
.msg-avatar { 
  width: 40px; height: 40px; border-radius: 8px; 
  display: flex; align-items: center; justify-content: center; 
  font-weight: bold; font-size: 12px; margin: 0 15px;
  flex-shrink: 0;
}
.user .msg-avatar { background: #409eff; color: #fff; }
.assistant .msg-avatar { background: #e9e9eb; color: #606266; }

/* 气泡内容 */
.msg-content { 
  max-width: 75%; padding: 14px 18px; border-radius: 12px; 
  font-size: 15px; line-height: 1.7; white-space: pre-wrap;
  word-break: break-all;
}
.user .msg-content { background: #409eff; color: #fff; border-top-right-radius: 2px; }
.assistant .msg-content { background: #fff; color: #303133; border-top-left-radius: 2px; border: 1px solid #ebeef5; }

/* 底部输入框 */
.chat-footer { padding: 30px 60px; background: #fff; border-top: 1px solid #f0f0f0; }
.w-full { width: 100%; }
.mb-4 { margin-bottom: 16px; }

/* 阴影效果 */
.shadow-sm { box-shadow: 0 2px 12px 0 rgba(0,0,0,0.05); }
</style>