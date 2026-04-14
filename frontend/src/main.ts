import { createApp } from 'vue'
// 1. 引入 Element Plus 组件库
import ElementPlus from 'element-plus'
// 2. 引入 Element Plus 官方样式（没这行界面就没颜色、没布局）
import 'element-plus/dist/index.css'
// 3. 引入你自己的全局样式
import './style.css'
import App from './App.vue'

const app = createApp(App)

// 4. 注册组件库
app.use(ElementPlus)

app.mount('#app')