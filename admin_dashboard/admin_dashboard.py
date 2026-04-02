from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import redis
import json
import re
import os
import csv
import io
from pydantic import BaseModel

# Configuração Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

app = FastAPI(title="Scoras AI Agent - Admin Dashboard", version="1.0.0")

# CORS para admin dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic
class ConversationSummary(BaseModel):
    user_id: str
    start_time: str
    last_activity: str
    message_count: int
    lead_type: Optional[str] = None
    qualified: bool = False
    name: Optional[str] = None
    nome: Optional[str] = None
    phone: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    whatsapp: Optional[str] = None
    interesse: Optional[str] = None

class ConversationDetail(BaseModel):
    user_id: str
    messages: List[Dict[str, Any]]
    qualification_data: Dict[str, Any]
    metadata: Dict[str, Any]

class RedisQuery(BaseModel):
    command: str
    args: List[str] = []

# Endpoints do Dashboard Admin

@app.get("/admin/conversations", response_model=List[ConversationSummary])
async def get_all_conversations(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    lead_type: Optional[str] = None,
    qualified: Optional[bool] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
):
    """Listar todas as conversas com filtros e paginação"""
    try:
        # Buscar todas as chaves de conversa
        conversation_keys = redis_client.keys("conversation:*")
        conversations = []
        
        for key in conversation_keys:
            user_id = key.replace("conversation:", "")
            
            # Buscar dados da conversa
            conversation_data = redis_client.get(key)
            if not conversation_data:
                continue
                
            try:
                conversation_obj = json.loads(conversation_data)
                if isinstance(conversation_obj, dict) and 'messages' in conversation_obj:
                    messages = conversation_obj['messages']
                else:
                    messages = conversation_obj if isinstance(conversation_obj, list) else []
            except json.JSONDecodeError:
                continue
            
            if not messages:
                continue
            
            # Buscar dados de qualificação
            qual_key = f"qualification:{user_id}"
            qual_data = redis_client.get(qual_key)
            qualification = json.loads(qual_data) if qual_data else {}
            
            # Extrair informações da conversa
            first_message = messages[0] if messages else {}
            last_message = messages[-1] if messages else {}
            
            start_time = first_message.get("timestamp", "")
            last_activity = last_message.get("timestamp", "")
            
            # Determinar tipo de lead
            lead_type_detected = None
            for msg in messages:
                bot_response = msg.get("bot_response", "")
                user_message = msg.get("user_message", "")
                if "academy" in bot_response.lower() or "scoras academy" in bot_response.lower():
                    lead_type_detected = "academy"
                    break
                elif "digital" in bot_response.lower() or "scoras digital" in bot_response.lower():
                    lead_type_detected = "digital"
                    break
                elif msg.get("lead_type"):
                    lead_type_detected = msg.get("lead_type").lower()
                    break
            
            conversation_summary = ConversationSummary(
                user_id=user_id,
                start_time=start_time,
                last_activity=last_activity,
                message_count=len(messages),
                lead_type=lead_type_detected or qualification.get("lead_type"),
                qualified=qualification.get("qualified", False),
                name=qualification.get("name") or qualification.get("nome"),
                nome=qualification.get("nome") or qualification.get("name"),
                phone=qualification.get("phone") or qualification.get("telefone"),
                telefone=qualification.get("telefone") or qualification.get("phone"),
                email=qualification.get("email"),
                whatsapp=qualification.get("whatsapp") or qualification.get("telefone") or qualification.get("phone"),
                interesse=qualification.get("interesse")
            )
            
            # Aplicar filtros
            if search and search.lower() not in user_id.lower():
                if not any(search.lower() in str(v).lower() for v in [
                    conversation_summary.name, 
                    conversation_summary.phone, 
                    conversation_summary.email
                ] if v):
                    continue
            
            if lead_type and conversation_summary.lead_type != lead_type:
                continue
            
            if qualified is not None and conversation_summary.qualified != qualified:
                continue
            
            # Filtro por data (simplificado)
            if date_from or date_to:
                # Implementar filtro de data baseado no start_time
                pass
            
            conversations.append(conversation_summary)
        
        # Ordenar por última atividade (mais recente primeiro)
        conversations.sort(key=lambda x: x.last_activity, reverse=True)
        
        # Paginação
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        return conversations[start_idx:end_idx]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar conversas: {str(e)}")

@app.get("/admin/conversation/{user_id}", response_model=ConversationDetail)
async def get_conversation_detail(user_id: str):
    """Obter detalhes completos de uma conversa específica"""
    try:
        # Buscar conversa
        conversation_key = f"conversation:{user_id}"
        conversation_data = redis_client.get(conversation_key)
        
        if not conversation_data:
            raise HTTPException(status_code=404, detail="Conversa não encontrada")
        
        conversation_obj = json.loads(conversation_data)
        if isinstance(conversation_obj, dict) and 'messages' in conversation_obj:
            messages = conversation_obj['messages']
        else:
            messages = conversation_obj if isinstance(conversation_obj, list) else []
        
        # Buscar dados de qualificação
        qual_key = f"qualification:{user_id}"
        qual_data = redis_client.get(qual_key)
        qualification = json.loads(qual_data) if qual_data else {}
        
        # Buscar metadados adicionais
        metadata = {
            "redis_keys": {
                "conversation": conversation_key,
                "qualification": qual_key
            },
            "total_messages": len(messages),
            "conversation_started": messages[0].get("timestamp") if messages else None,
            "last_activity": messages[-1].get("timestamp") if messages else None,
            "ttl": redis_client.ttl(conversation_key)
        }
        
        return ConversationDetail(
            user_id=user_id,
            messages=messages,
            qualification_data=qualification,
            metadata=metadata
        )
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Dados de conversa corrompidos")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar conversa: {str(e)}")

@app.post("/admin/redis/query")
async def execute_redis_query(query: RedisQuery):
    """Executar query customizada no Redis"""
    try:
        command = query.command.upper()
        
        # Lista de comandos permitidos (apenas leitura e comandos seguros)
        allowed_commands = [
            "GET", "KEYS", "EXISTS", "TTL", "TYPE", "LRANGE", "LLEN",
            "HGET", "HGETALL", "HKEYS", "HLEN", "SCARD", "SMEMBERS",
            "ZCARD", "ZRANGE", "ZREVRANGE", "SCAN", "INFO", "DBSIZE"
        ]
        
        if command not in allowed_commands:
            raise HTTPException(
                status_code=403, 
                detail=f"Comando '{command}' não permitido. Comandos permitidos: {', '.join(allowed_commands)}"
            )
        
        # Executar comando
        if command == "KEYS":
            result = redis_client.keys(query.args[0] if query.args else "*")
        elif command == "GET":
            result = redis_client.get(query.args[0]) if query.args else None
        elif command == "LRANGE":
            if len(query.args) >= 3:
                result = redis_client.lrange(query.args[0], int(query.args[1]), int(query.args[2]))
            else:
                result = redis_client.lrange(query.args[0], 0, -1) if query.args else []
        elif command == "HGETALL":
            result = redis_client.hgetall(query.args[0]) if query.args else {}
        elif command == "INFO":
            result = redis_client.info(query.args[0] if query.args else None)
        elif command == "DBSIZE":
            result = redis_client.dbsize()
        else:
            # Executar comando genérico
            result = getattr(redis_client, command.lower())(*query.args)
        
        return {
            "command": f"{command} {' '.join(query.args)}",
            "result": result,
            "type": type(result).__name__,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro na query Redis: {str(e)}")

@app.get("/admin/analytics/overview")
async def get_analytics_overview():
    """Dashboard principal com métricas gerais"""
    try:
        # Buscar todas as conversas
        conversation_keys = redis_client.keys("conversation:*")
        total_conversations = len(conversation_keys)
        
        # Contadores
        academy_leads = 0
        digital_leads = 0
        qualified_leads = 0
        total_messages = 0
        academy_conversations = 0
        digital_conversations = 0
        academy_qualified = 0
        digital_qualified = 0
        
        # Análise por período
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        this_week = today - timedelta(days=7)
        
        conversations_today = 0
        conversations_yesterday = 0
        conversations_this_week = 0
        
        for key in conversation_keys:
            user_id = key.replace("conversation:", "")
            
            # Dados da conversa
            conversation_data = redis_client.get(key)
            lead_type_from_conversation = None
            
            if conversation_data:
                try:
                    conversation_obj = json.loads(conversation_data)
                    if isinstance(conversation_obj, dict) and 'messages' in conversation_obj:
                        messages = conversation_obj['messages']
                    else:
                        messages = conversation_obj if isinstance(conversation_obj, list) else []
                    total_messages += len(messages)
                    
                    # Determinar tipo de lead das mensagens
                    for msg in messages:
                        bot_response = msg.get("bot_response", "")
                        user_message = msg.get("user_message", "")
                        if "academy" in bot_response.lower() or "scoras academy" in bot_response.lower():
                            lead_type_from_conversation = "academy"
                            break
                        elif "digital" in bot_response.lower() or "scoras digital" in bot_response.lower():
                            lead_type_from_conversation = "digital"
                            break
                        elif msg.get("lead_type"):
                            lead_type_from_conversation = msg.get("lead_type").lower()
                            break
                    
                    # Verificar data da primeira mensagem
                    if messages:
                        first_msg_time = messages[0].get("timestamp")
                        if first_msg_time:
                            try:
                                msg_date = datetime.fromisoformat(first_msg_time.replace("Z", "+00:00")).date()
                                if msg_date == today:
                                    conversations_today += 1
                                elif msg_date == yesterday:
                                    conversations_yesterday += 1
                                elif msg_date >= this_week:
                                    conversations_this_week += 1
                            except:
                                pass
                except:
                    continue
            
            # Dados de qualificação
            qual_key = f"qualification:{user_id}"
            qual_data = redis_client.get(qual_key)
            qualification = {}
            if qual_data:
                try:
                    qualification = json.loads(qual_data)
                    if qualification.get("qualified"):
                        qualified_leads += 1
                except:
                    continue
            
            # Determinar lead_type final (prioridade: qualification -> conversation)
            final_lead_type = qualification.get("lead_type") or lead_type_from_conversation
            
            # Normalizar para minúsculas para comparação
            if final_lead_type:
                final_lead_type = final_lead_type.lower()
            
            if final_lead_type == "academy":
                academy_leads += 1
                academy_conversations += 1
                if qualification.get("qualified"):
                    academy_qualified += 1
            elif final_lead_type == "digital":
                digital_leads += 1
                digital_conversations += 1
                if qualification.get("qualified"):
                    digital_qualified += 1
        
        # Redis info
        redis_info = redis_client.info()
        
        return {
            "overview": {
                "total_conversations": total_conversations,
                "total_messages": total_messages,
                "qualified_leads": qualified_leads,
                "qualification_rate": round((qualified_leads / total_conversations * 100) if total_conversations > 0 else 0, 2)
            },
            "lead_types": {
                "academy": academy_leads,
                "digital": digital_leads,
                "unknown": total_conversations - academy_leads - digital_leads
            },
            "conversations_breakdown": {
                "academy_conversations": academy_conversations,
                "digital_conversations": digital_conversations
            },
            "qualified_breakdown": {
                "academy_qualified": academy_qualified,
                "digital_qualified": digital_qualified
            },
            "activity": {
                "conversations_today": conversations_today,
                "conversations_yesterday": conversations_yesterday,
                "conversations_this_week": conversations_this_week
            },
            "redis_stats": {
                "total_keys": redis_info.get("db0", {}).get("keys", 0),
                "memory_used": redis_info.get("used_memory_human"),
                "connected_clients": redis_info.get("connected_clients"),
                "uptime_days": redis_info.get("uptime_in_days")
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar analytics: {str(e)}")

@app.delete("/admin/conversation/{user_id}")
async def delete_conversation(user_id: str):
    """Deletar uma conversa específica (LGPD compliance)"""
    try:
        deleted_keys = []
        
        # Deletar conversa
        conv_key = f"conversation:{user_id}"
        if redis_client.delete(conv_key):
            deleted_keys.append(conv_key)
        
        # Deletar qualificação
        qual_key = f"qualification:{user_id}"
        if redis_client.delete(qual_key):
            deleted_keys.append(qual_key)
        
        # Deletar outras chaves relacionadas
        other_keys = redis_client.keys(f"*:{user_id}")
        for key in other_keys:
            if redis_client.delete(key):
                deleted_keys.append(key)
        
        return {
            "deleted_keys": deleted_keys,
            "total_deleted": len(deleted_keys),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao deletar conversa: {str(e)}")

@app.get("/admin/leads")
async def get_leads(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    type: Optional[str] = None
):
    """Returns qualified leads with full contact info"""
    try:
        qualification_keys = redis_client.keys("qualification:*")
        leads = []

        for key in qualification_keys:
            user_id = key.replace("qualification:", "")
            qual_data = redis_client.get(key)
            if not qual_data:
                continue

            try:
                qualification = json.loads(qual_data)
            except json.JSONDecodeError:
                continue

            lead_type = (qualification.get("lead_type") or "unknown").lower()

            # Filter by type
            if type and lead_type != type.lower():
                continue

            # Get conversation message count
            conv_key = f"conversation:{user_id}"
            conv_data = redis_client.get(conv_key)
            message_count = 0
            created_at = qualification.get("last_interaction", "")
            if conv_data:
                try:
                    conv_obj = json.loads(conv_data)
                    if isinstance(conv_obj, dict) and 'messages' in conv_obj:
                        message_count = len(conv_obj['messages'])
                        created_at = conv_obj.get("created_at", created_at)
                except json.JSONDecodeError:
                    pass

            leads.append({
                "user_id": user_id,
                "nome": qualification.get("nome") or qualification.get("name"),
                "email": qualification.get("email"),
                "telefone": qualification.get("telefone") or qualification.get("phone"),
                "whatsapp": qualification.get("whatsapp") or qualification.get("telefone") or qualification.get("phone"),
                "interesse": qualification.get("interesse"),
                "lead_type": lead_type,
                "qualified": qualification.get("qualified", False),
                "created_at": created_at,
                "message_count": message_count,
                "last_interaction": qualification.get("last_interaction")
            })

        # Sort by last_interaction descending
        leads.sort(key=lambda x: x.get("last_interaction") or "", reverse=True)

        # Pagination
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page

        return {
            "total": len(leads),
            "page": page,
            "per_page": per_page,
            "leads": leads[start_idx:end_idx]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar leads: {str(e)}")


@app.get("/admin/search")
async def search_conversations(q: str = Query(..., min_length=1)):
    """Search across all conversations and qualifications"""
    try:
        q_lower = q.lower()
        results = []

        conversation_keys = redis_client.keys("conversation:*")

        for key in conversation_keys:
            user_id = key.replace("conversation:", "")
            matched = False

            # Check if user_id matches
            if q_lower in user_id.lower():
                matched = True

            # Check qualification data
            qual_key = f"qualification:{user_id}"
            qual_data = redis_client.get(qual_key)
            qualification = {}
            if qual_data:
                try:
                    qualification = json.loads(qual_data)
                except json.JSONDecodeError:
                    pass

                # Search in qualification fields
                for field in ['nome', 'name', 'email', 'telefone', 'phone', 'whatsapp', 'interesse']:
                    value = qualification.get(field)
                    if value and q_lower in str(value).lower():
                        matched = True
                        break

            if not matched:
                continue

            # Get conversation data
            conv_data = redis_client.get(key)
            message_count = 0
            start_time = ""
            last_activity = ""
            lead_type = qualification.get("lead_type", "unknown")

            if conv_data:
                try:
                    conv_obj = json.loads(conv_data)
                    if isinstance(conv_obj, dict) and 'messages' in conv_obj:
                        messages = conv_obj['messages']
                    else:
                        messages = conv_obj if isinstance(conv_obj, list) else []
                    message_count = len(messages)
                    if messages:
                        start_time = messages[0].get("timestamp", "")
                        last_activity = messages[-1].get("timestamp", "")
                        # Get lead_type from messages if not in qualification
                        if not lead_type or lead_type == "unknown":
                            for msg in messages:
                                if msg.get("lead_type"):
                                    lead_type = msg["lead_type"].lower()
                                    break
                except json.JSONDecodeError:
                    pass

            results.append({
                "user_id": user_id,
                "nome": qualification.get("nome") or qualification.get("name"),
                "email": qualification.get("email"),
                "telefone": qualification.get("telefone") or qualification.get("phone"),
                "whatsapp": qualification.get("whatsapp"),
                "lead_type": lead_type,
                "qualified": qualification.get("qualified", False),
                "message_count": message_count,
                "start_time": start_time,
                "last_activity": last_activity
            })

        return {
            "query": q,
            "total": len(results),
            "results": results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na busca: {str(e)}")


@app.get("/admin/export/csv")
async def export_csv(type: Optional[str] = None):
    """Export all qualified leads as CSV download"""
    try:
        qualification_keys = redis_client.keys("qualification:*")

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "user_id", "nome", "email", "telefone", "whatsapp",
            "interesse", "lead_type", "created_at", "message_count", "qualified"
        ])

        for key in qualification_keys:
            user_id = key.replace("qualification:", "")
            qual_data = redis_client.get(key)
            if not qual_data:
                continue

            try:
                qualification = json.loads(qual_data)
            except json.JSONDecodeError:
                continue

            lead_type = (qualification.get("lead_type") or "unknown").lower()

            # Filter by type if specified
            if type and lead_type != type.lower():
                continue

            # Get conversation message count
            conv_key = f"conversation:{user_id}"
            conv_data = redis_client.get(conv_key)
            message_count = 0
            created_at = qualification.get("last_interaction", "")
            if conv_data:
                try:
                    conv_obj = json.loads(conv_data)
                    if isinstance(conv_obj, dict) and 'messages' in conv_obj:
                        message_count = len(conv_obj['messages'])
                        created_at = conv_obj.get("created_at", created_at)
                except json.JSONDecodeError:
                    pass

            writer.writerow([
                user_id,
                qualification.get("nome") or qualification.get("name") or "",
                qualification.get("email") or "",
                qualification.get("telefone") or qualification.get("phone") or "",
                qualification.get("whatsapp") or qualification.get("telefone") or qualification.get("phone") or "",
                qualification.get("interesse") or "",
                lead_type,
                created_at,
                message_count,
                qualification.get("qualified", False)
            ])

        output.seek(0)
        filename = f"scoras_leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        if type:
            filename = f"scoras_leads_{type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao exportar CSV: {str(e)}")


@app.get("/admin/redis/info")
async def get_redis_info():
    """Informações detalhadas do Redis"""
    try:
        info = redis_client.info()
        return {
            "server": {
                "redis_version": info.get("redis_version"),
                "uptime_in_seconds": info.get("uptime_in_seconds"),
                "uptime_in_days": info.get("uptime_in_days"),
            },
            "memory": {
                "used_memory": info.get("used_memory"),
                "used_memory_human": info.get("used_memory_human"),
                "used_memory_peak": info.get("used_memory_peak"),
                "used_memory_peak_human": info.get("used_memory_peak_human"),
            },
            "clients": {
                "connected_clients": info.get("connected_clients"),
                "client_recent_max_input_buffer": info.get("client_recent_max_input_buffer"),
                "client_recent_max_output_buffer": info.get("client_recent_max_output_buffer"),
            },
            "stats": {
                "total_connections_received": info.get("total_connections_received"),
                "total_commands_processed": info.get("total_commands_processed"),
                "instantaneous_ops_per_sec": info.get("instantaneous_ops_per_sec"),
                "keyspace_hits": info.get("keyspace_hits"),
                "keyspace_misses": info.get("keyspace_misses"),
            },
            "keyspace": info.get("db0", {}),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter info Redis: {str(e)}")

# Servir arquivos estáticos (CSS, JS, etc.)
# Criar diretório se não existir
os.makedirs("admin_static", exist_ok=True)
app.mount("/admin/static", StaticFiles(directory="admin_static"), name="static")

# Endpoint para servir o dashboard principal
@app.get("/admin", response_class=HTMLResponse)
async def get_admin_dashboard():
    """Servir o dashboard administrativo"""
    try:
        with open("admin_dashboard.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return HTMLResponse("""
        <h1>Dashboard Admin não encontrado</h1>
        <p>Execute o script de setup para criar o dashboard.</p>
        """, status_code=404)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002) 