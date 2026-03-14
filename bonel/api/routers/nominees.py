"""
Bonel Project - 候选人/论文提交路由
处理论文提交、文件上传、数据持久化到 Supabase

⚠️ 依赖检查：
本模块使用 Form Data 解析，需要安装 python-multipart：
    pip install python-multipart

如果未安装，FastAPI 会在解析 Form Data 时抛出错误：
    RuntimeError: Form data requires "python-multipart" to be installed.
"""

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Query
from fastapi.responses import JSONResponse
from typing import Optional
from datetime import datetime
from uuid import uuid4
import logging

from bonel.auth.dependencies import get_current_user, get_supabase_service_client
from bonel.models import CurrentUser, NomineeStatus

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Nominees"])


@router.post("/nominees")
async def submit_nominee(
    # 文本字段 - 使用 Form(...) 表示必填，Form(default) 表示有默认值
    title: str = Form(..., description="论文标题，必填"),
    author: str = Form(default="佚名研究员", description="作者名称，默认为佚名研究员"),
    contact: str = Form(..., description="联系方式，必填，敏感信息"),
    abstract: str = Form(..., description="论文摘要，必填"),
    link: Optional[str] = Form(default=None, description="外部证据链接，选填"),
    
    # 文件字段 - 使用 File(None) 表示可选
    file: Optional[UploadFile] = File(None, description="PDF 文件，选填"),
    
    # 鉴权依赖 - 确保只有登录用户才能提交
    user: CurrentUser = Depends(get_current_user)
):
    """
    提交抽象论文 (Submit Paper)
    
    接收前端通过 multipart/form-data 格式提交的数据，包含：
    - 论文元数据（标题、作者、摘要等）
    - 可选的 PDF 附件
    
    业务流程：
    1. 验证用户登录状态
    2. 如有 PDF 文件，上传到 Supabase Storage
    3. 生成学术感 ID，将数据写入 PostgreSQL
    4. 返回提交成功响应
    
    Args:
        title: 论文标题
        author: 作者名称
        contact: 联系方式
        abstract: 论文摘要
        link: 外部证据链接
        file: PDF 文件
        user: 当前登录用户（自动注入）
    
    Returns:
        {"success": True, "message": "灾难档案已成功递交", "id": nominee_id}
    """
    
    # ==================== 1. 文件上传处理 ====================
    file_url: Optional[str] = None
    
    if file is not None:
        # 验证文件类型 - 只允许 PDF
        content_type = file.content_type or ""
        filename = file.filename or ""
        
        if not (content_type == "application/pdf" or filename.lower().endswith(".pdf")):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只允许上传 PDF 格式的文件"
            )
        
        try:
            # 读取文件字节流
            # ⚠️ 注意：UploadFile 是异步的，必须使用 await file.read()
            file_bytes = await file.read()
            
            if len(file_bytes) == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="上传的文件为空"
                )
            
            # 生成唯一文件名，防止重名覆盖
            # 格式：uuid前8位_原文件名.pdf
            # 例如：a1b2c3d4e5f67890_我的论文.pdf
            unique_id = uuid4().hex[:8]
            safe_filename = filename.replace(" ", "_") if filename else "document.pdf"
            file_name = f"{unique_id}_{safe_filename}"
            
            # 获取 Supabase 服务客户端（具有 Storage 写入权限）
            supabase = get_supabase_service_client()
            
            # 上传文件到 Supabase Storage 的 papers 存储桶
            # 参数说明：
            #   - "papers": 存储桶名称
            #   - file_name: 目标文件名
            #   - file_bytes: 文件字节流
            #   - {"content-type": "application/pdf"}: 元数据，设置正确的 MIME 类型
            upload_response = supabase.storage.from_("papers").upload(
                file_name,
                file_bytes,
                {"content-type": "application/pdf"}
            )
            
            logger.info(f"✅ 文件上传成功: {file_name}")
            
            # 获取文件的公开下载链接 (Public URL)
            # 注意：papers 存储桶必须设置为公开 (public) 才能获取公开 URL
            # 如果存储桶是私有的，需要使用 createSignedUrl() 生成临时签名 URL
            file_url = supabase.storage.from_("papers").get_public_url(file_name)
            
            logger.info(f"📎 文件公开链接: {file_url}")
            
        except HTTPException:
            # 重新抛出已知的 HTTP 异常
            raise
        except Exception as e:
            # 捕获 Supabase 或其他异常
            logger.error(f"❌ 文件上传失败: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"文件上传失败: {str(e)}"
            )
        finally:
            # 关闭文件句柄，释放资源
            # 这是一个好习惯，防止内存泄漏
            await file.close()
    
    # ==================== 2. 生成学术感唯一 ID ====================
    # 格式：BNL-2603-<UUID前8位>
    # BNL: Bonel 项目缩写
    # 2603: 2026年3月，表示项目时间线
    # UUID前8位：确保唯一性
    uuid_part = uuid4().hex[:8].upper()
    nominee_id = f"BNL-2603-{uuid_part}"
    
    # ==================== 3. 写入 PostgreSQL 数据库 ====================
    try:
        # 获取 Supabase 服务客户端
        supabase = get_supabase_service_client()
        
        # 准备插入数据
        # 对应 public.nominees 表结构
        insert_data = {
            "id": nominee_id,
            "title": title,
            "author": author,
            "contact": contact,
            "abstract": abstract,
            "evidence_link": link,  # 对应数据库的 evidence_link 字段
            "file_url": file_url,   # 上一步获取的 PDF URL
            "total_votes": 0,       # 初始票数为 0
            "status": NomineeStatus.PENDING.value,  # 待审核状态
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            # 可选：记录提交者信息，便于后续追溯
            "submitted_by": user.id
        }
        
        # 执行 INSERT 操作
        # 使用 .execute() 执行查询
        result = supabase.from_("nominees").insert(insert_data).execute()
        
        logger.info(f"✅ 论文数据已写入数据库: {nominee_id}")
        logger.info(f"👤 提交者: {user.id} ({user.email or 'N/A'})")
        
    except Exception as e:
        # 数据库操作失败
        # 注意：这里文件已经上传成功，但数据库写入失败
        # 在生产环境中，应该考虑：
        # 1. 删除已上传的文件（保持数据一致性）
        # 2. 将失败任务放入队列，稍后重试
        logger.error(f"❌ 数据库写入失败: {e}")
        logger.error(f"📝 失败数据: id={nominee_id}, title={title}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"数据保存失败: {str(e)}"
        )
    
    # ==================== 4. 返回成功响应 ====================
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "success": True,
            "message": "灾难档案已成功递交",
            "id": nominee_id
        }
    )


@router.get("/nominees")
async def get_nominees_list(
    sort: str = Query("hot", pattern="^(hot|new)$", description="排序方式: hot(热度)/new(最新)"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    search: str = Query("", description="搜索关键词"),
    user: CurrentUser = Depends(get_current_user)
):
    """
    获取候选人/论文列表
    
    支持排序和分页：
    - hot: 按 total_votes 降序排列（热度榜单）
    - new: 按 created_at 降序排列（最新入库）
    
    只返回已通过审核 (status='approved') 的论文
    
    Args:
        sort: 排序方式 ('hot' 或 'new')
        page: 页码，从1开始
        page_size: 每页数量
        search: 搜索关键词（可选）
        user: 当前登录用户
    
    Returns:
        包含论文列表和用户状态的 JSON
    """
    try:
        supabase = get_supabase_service_client()
        
        # 构建基础查询 - 只查询已审核通过的
        query = supabase.from_("nominees").select("*").eq("status", NomineeStatus.APPROVED.value)
        
        # 搜索过滤
        if search:
            # 在标题、作者、ID 中搜索
            query = query.or_(f"title.ilike.%{search}%,author.ilike.%{search}%,id.ilike.%{search}%")
        
        # 排序
        if sort == "hot":
            query = query.order("total_votes", desc=True)
        else:  # new
            query = query.order("created_at", desc=True)
        
        # 分页
        offset = (page - 1) * page_size
        query = query.range(offset, offset + page_size - 1)
        
        # 执行查询
        result = query.execute()
        nominees = result.data or []
        
        # 获取总数（用于分页）
        count_result = supabase.from_("nominees") \
            .select("id", count="exact") \
            .eq("status", NomineeStatus.APPROVED.value)
        if search:
            count_result = count_result.or_(f"title.ilike.%{search}%,author.ilike.%{search}%,id.ilike.%{search}%")
        count_data = count_result.execute()
        total = count_data.count if hasattr(count_data, 'count') else len(nominees)
        
        # 获取用户投票状态
        user_status = {
            "isLoggedIn": user.is_authenticated,
            "votesLeft": 0,
            "hasSharedToday": False
        }
        
        if user.is_authenticated:
            # 查询用户已投票数
            try:
                profile_result = supabase.from_("profiles") \
                    .select("daily_votes_left, has_shared_today") \
                    .eq("id", user.id) \
                    .single() \
                    .execute()
                if profile_result.data:
                    user_status["votesLeft"] = profile_result.data.get("daily_votes_left", 5)
                    user_status["hasSharedToday"] = profile_result.data.get("has_shared_today", False)
            except Exception as e:
                logger.warning(f"获取用户状态失败: {e}")
                user_status["votesLeft"] = 5
        
        # 转换数据格式，匹配前端期望
        papers = []
        for nominee in nominees:
            # 查询当前用户对该论文的投票数
            user_votes = 0
            if user.is_authenticated:
                try:
                    vote_result = supabase.from_("vote_logs") \
                        .select("vote_count") \
                        .eq("user_id", user.id) \
                        .eq("nominee_id", nominee["id"]) \
                        .single() \
                        .execute()
                    if vote_result.data:
                        user_votes = vote_result.data.get("vote_count", 0)
                except:
                    pass  # 没有投票记录就是0
            
            papers.append({
                "id": nominee["id"],
                "title": nominee["title"],
                "author": nominee["author"],
                "abstract": nominee.get("abstract", ""),
                "totalVotes": nominee.get("total_votes", 0),
                "userVotes": user_votes,
                "date": nominee.get("created_at", datetime.now().isoformat())
            })
        
        return {
            "userStatus": user_status,
            "papers": papers,
            "total": total,
            "page": page,
            "pageSize": page_size
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取论文列表失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取列表失败: {str(e)}"
        )


@router.get("/nominees/{nominee_id}")
async def get_nominee_detail(
    nominee_id: str,
    user: CurrentUser = Depends(get_current_user)
):
    """
    获取候选人/论文详情
    
    用于后续的"灾难展览页"展示单个论文详情
    
    Args:
        nominee_id: 候选人唯一 ID (如 BNL-2603-A1B2C3D4)
        user: 当前登录用户
    
    Returns:
        论文详情，包含标题、作者、摘要、文件链接等
    """
    try:
        supabase = get_supabase_service_client()
        
        # 查询单个候选人
        result = supabase.from_("nominees").select("*").eq("id", nominee_id).single().execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"未找到 ID 为 {nominee_id} 的论文"
            )
        
        nominee = result.data
        
        # 检查权限：只有管理员或提交者本人可以查看待审核的论文
        if nominee.get("status") == NomineeStatus.PENDING.value:
            if not (user.is_admin_or_above() or nominee.get("submitted_by") == user.id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="该论文正在审核中，暂时无法查看"
                )
        
        return {
            "success": True,
            "data": nominee
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 查询论文详情失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询失败: {str(e)}"
        )
