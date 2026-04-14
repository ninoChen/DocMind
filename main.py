import os                                                                                                                                                                        
import json                                                                                                                                                                      
import asyncio                                                                                                                                                                   
import shutil
import requests                                                                                                                                                                  
import threading
from typing import List                                                                                                                                                          
from fastapi import FastAPI, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware                                                                                                                               
from fastapi.responses import StreamingResponse
from openai import OpenAI
from dotenv import load_dotenv
                                                                                                                                                                                 
# --- Phoenix / OpenTelemetry 追踪（后台线程，不阻塞启动） ---
from openinference.instrumentation.langchain import LangChainInstrumentor                                                                                                        
from opentelemetry import trace as otel_trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter                                                                                               
from opentelemetry.sdk import trace as sdk_trace
from opentelemetry.sdk.trace.export import BatchSpanProcessor                                                                                                                    
from opentelemetry.sdk.resources import Resource

from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
                                                                                                                                                                                   
load_dotenv()
                                                                                                                                                                                 
import time                                                                                                                                                                      
   
def _init_telemetry():                                                                                                                                                           
      try:        
          resource = Resource(attributes={"service.name": "my-ai-knowledge-base"})
          tracer_provider = sdk_trace.TracerProvider(resource=resource)                                                                                                            
          otel_trace.set_tracer_provider(tracer_provider)
                                                                                                                                                                                   
          otlp_exporter = OTLPSpanExporter(
              endpoint="http://127.0.0.1:6006/v1/traces",
              timeout=5,
          )                                                                                                                                                                        
          tracer_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
          LangChainInstrumentor().instrument()                                                                                                                                     
                  
          tracer = tracer_provider.get_tracer(__name__)
          with tracer.start_as_current_span("phoenix-test") as span:
              span.set_attribute("init", True)
                                                                                                                                                                                   
          import time
          time.sleep(2)                                                                                                                                                            
                  
          print("[Telemetry] Phoenix connect OK - please refresh Phoenix page to see test trace")
      except Exception as e:
          import traceback                                                                                                                                                         
          print(f"[Telemetry] Phoenix connect FAILED: {e}")
          traceback.print_exc() 

threading.Thread(target=_init_telemetry, daemon=True).start()                                                                                                                    
 
# --- FastAPI 逻辑 ---                                                                                                                                                           
app = FastAPI(title="AI 知识库 + Phoenix 2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],                                                                                                                                                         
    allow_headers=["*"],
)                                                                                                                                                                                
                
class ZhipuEmbeddings:
    def __init__(self):
        self.api_key = os.getenv("ZHIPU_API_KEY")
        self.url = "https://open.bigmodel.cn/api/paas/v4/embeddings"
                                                                                                                                                                                 
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}                                                                                
        payload = {"model": "embedding-3", "input": [t.replace("\n", " ") for t in texts]}
        res = requests.post(self.url, json=payload, headers=headers)                                                                                                             
        return [item["embedding"] for item in res.json()["data"]]
                                                                                                                                                                                 
    def embed_query(self, text: str) -> List[float]:                                                                                                                             
        return self.embed_documents([text])[0]
                                                                                                                                                                                 
                
class SmartVectorStore:
    def __init__(self, db_dir="./chroma_db_router"):
        self.embeddings = ZhipuEmbeddings()
        self.db_dir = db_dir
        self.db = None
                                                                                                                                                                                 
    def _ensure_db(self):
        if self.db is None:                                                                                                                                                      
            self._load_db()
    def _load_db(self):
        if os.path.exists(self.db_dir) and os.listdir(self.db_dir):
            from langchain_community.vectorstores import Chroma
            self.db = Chroma(persist_directory=self.db_dir, embedding_function=self.embeddings)                                                                                  
 
    def add_document(self, pdf_path: str, category: str):                                                                                                                        
        from langchain_community.document_loaders import PyPDFLoader
        from langchain_text_splitters import RecursiveCharacterTextSplitter                                                                                                      
        from langchain_community.vectorstores import Chroma
                                                                                                                                                                                 
        self._ensure_db()
        loader = PyPDFLoader(pdf_path)
        pages = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        chunks = text_splitter.split_documents(pages)                                                                                                                            
        for chunk in chunks:
            chunk.metadata["category"] = category                                                                                                                                
                
        if self.db is None:
            self.db = Chroma.from_documents(chunks, self.embeddings, persist_directory=self.db_dir)
        else:                                                                                                                                                                    
            self.db.add_documents(chunks)
                                                                                                                                                                                 
                                                                                                                                                                                 
client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com/v1")
store = SmartVectorStore()                                                                                                                                                       
                
@app.get("/")
def root():
    from fastapi.responses import JSONResponse
    return JSONResponse({"message": "AI 知识库服务已启动", "docs": "/docs"})
@app.post("/upload")
def upload_document(file: UploadFile = File(...), category: str = Form(...)):
    temp_path = f"temp_{file.filename}"                                                                                                                                          
    try:
        with open(temp_path, "wb") as buffer:                                                                                                                                    
            shutil.copyfileobj(file.file, buffer)
        print(f">>> 开始向量化: {file.filename}")                                                                                                                                
        store.add_document(temp_path, category)
        print(f">>> 向量化完成")                                                                                                                                                 
                
        return {"status": "success", "msg": "上传成功"}
    except Exception as e:
        print(f">>> ❌ 报错: {e}")
        return {"status": "error", "msg": str(e)}                                                                                                                                
    finally:
        if os.path.exists(temp_path):                                                                                                                                            
            os.remove(temp_path)

# --- Redis 配置 ---
REDIS_URL = os.getenv("REDIS_URL")

def get_redis_history(session_id: str):
    """
    初始化 Redis 聊天记录
    ttl: 过期时间（秒），例如 3600 秒（1小时）不活动则自动删除
    """
    return RedisChatMessageHistory(
        session_id=session_id, 
        url=REDIS_URL, 
        ttl=3600  
    )

@app.post("/chat")
async def chat(message: str = Form(...), session_id: str = Form("user_123")):
    async def event_generator():
        try:
            # 1. 从 Redis 加载历史记忆
            history_obj = get_redis_history(session_id)
            # 获取最近的历史记录（Redis 存储的是对象，我们需要转换格式）
            history_messages = history_obj.messages[-6:] 

            # 2. 意图识别 (保持之前的逻辑)
            intent_prompt = f"分析问题意图，仅输出一个标签: PERSONNEL, TECHNICAL, CHAT。问题: {message}"
            res = client.chat.completions.create(
                model="deepseek-chat", 
                messages=[{"role": "user", "content": intent_prompt}], 
                temperature=0
            )
            intent = res.choices[0].message.content.strip().upper()
            
            # 3. 检索增强 (RAG)
            context = ""
            if intent in ["PERSONNEL", "TECHNICAL"] and store.db:
                # 实际生产中，这里可以结合历史记忆来优化 message (Query Rewriting)
                docs = store.db.similarity_search(message, k=3, filter={"category": intent})
                context = "\n".join([d.page_content for d in docs])

            # 4. 构造 OpenAI 格式的消息列表
            messages_for_llm = [
                {"role": "system", "content": "你是一个严谨的企业办公助手。请结合背景信息和历史对话回答。"}
            ]
            
            # 将 Redis 中的历史消息加入列表
            for msg in history_messages:
                role = "user" if isinstance(msg, HumanMessage) else "assistant"
                messages_for_llm.append({"role": role, "content": msg.content})
            
            # 放入当前问题（含 RAG 背景）
            current_input = f"背景：{context}\n问题：{message}" if context else message
            messages_for_llm.append({"role": "user", "content": current_input})

            # 5. 调用模型并流式返回
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages_for_llm,
                stream=True
            )

            full_answer = ""
            for chunk in response:
                delta = chunk.choices[0].delta.content
                if delta:
                    full_answer += delta
                    yield f"data: {json.dumps({'content': delta}, ensure_ascii=False)}\n\n"
                    await asyncio.sleep(0.01)

            # 6. 【核心】将本次对话存入 Redis
            history_obj.add_user_message(message)
            history_obj.add_ai_message(full_answer)

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
                                                                                                                                                                                 
                
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)