# 🎓 智能课堂互动平台 (Smart Classroom Platform)

一个基于Flask的现代化智能课堂互动平台，集成了AI功能，支持教师创建各种学习活动，学生参与互动，以及实时数据分析。

## 🌟 核心功能

### 👨‍🏫 教师功能
- **课程管理**: 创建和管理课程，导入学生名单
- **活动创建**: 支持多种学习活动类型（投票、测验、词云、简答题、迷你游戏）
- **AI集成**: 基于教学内容自动生成学习活动
- **实时监控**: 查看学生参与情况和活动进度
- **数据分析**: 获取详细的学习分析报告

### 👨‍🎓 学生功能
- **课程注册**: 注册感兴趣的课程
- **活动参与**: 参与各种互动学习活动
- **实时反馈**: 获得即时的学习反馈
- **进度跟踪**: 查看个人学习进度和成绩

### 🤖 AI功能
- **智能活动生成**: 基于课程内容自动生成学习活动
- **答案分析**: 自动分析学生回答，识别相似答案
- **个性化反馈**: 为每个学生生成个性化学习反馈
- **学习洞察**: 提供学习数据洞察和建议

### 📊 管理功能
- **用户管理**: 管理教师、学生和管理员账户
- **系统监控**: 监控系统使用情况和性能
- **数据备份**: 系统数据备份和恢复
- **排行榜**: 课程排行榜和学习激励

## 🏗️ 技术架构

### 后端技术栈
- **Flask**: Python Web框架
- **SQLAlchemy**: ORM数据库操作
- **SQLite**: 轻量级数据库
- **OpenAI API**: AI功能集成
- **Werkzeug**: 密码安全处理

### 前端技术栈
- **HTML5**: 语义化标记
- **CSS3**: 现代化响应式设计
- **JavaScript**: 原生JS实现交互
- **Chart.js**: 数据可视化

### 项目结构
```
smart-classroom-platform/
├── src/
│   ├── models/              # 数据模型
│   │   ├── user.py         # 用户模型
│   │   ├── course.py       # 课程模型
│   │   ├── activity.py     # 活动模型
│   │   ├── response.py     # 响应模型
│   │   └── analytics.py    # 分析模型
│   ├── routes/              # API路由
│   │   ├── auth.py         # 认证路由
│   │   ├── course.py       # 课程路由
│   │   ├── activity.py     # 活动路由
│   │   ├── response.py     # 响应路由
│   │   ├── analytics.py   # 分析路由
│   │   └── admin.py        # 管理路由
│   ├── ai/                  # AI功能
│   │   └── ai_service.py   # AI服务
│   ├── static/              # 静态文件
│   │   ├── index.html      # 主页
│   │   ├── teacher.html    # 教师界面
│   │   ├── student.html    # 学生界面
│   │   └── admin.html      # 管理员界面
│   └── database.py         # 数据库配置
├── database/                # 数据库文件
├── main.py                 # 应用入口
├── wsgi.py                 # WSGI配置
├── requirements.txt        # 依赖管理
├── Procfile               # Heroku部署
└── README.md              # 项目文档
```

## 🚀 快速开始

### 1. 环境准备
```bash
# 克隆项目
git clone <repository-url>
cd smart-classroom-platform

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 环境配置
```bash
# 复制环境变量文件
cp .env.example .env

# 编辑.env文件，设置OpenAI API密钥
OPENAI_API_KEY=your-openai-api-key-here
```

### 3. 运行应用
```bash
python main.py
```

应用将在 `http://localhost:5000` 启动。

## 🔧 API接口

### 认证接口
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/logout` - 用户登出
- `GET /api/auth/profile` - 获取用户信息
- `PUT /api/auth/profile` - 更新用户信息

### 课程接口
- `GET /api/courses/` - 获取课程列表
- `POST /api/courses/` - 创建课程
- `GET /api/courses/<id>` - 获取课程详情
- `PUT /api/courses/<id>` - 更新课程
- `POST /api/courses/<id>/enroll` - 注册课程
- `POST /api/courses/<id>/import-students` - 导入学生

### 活动接口
- `GET /api/activities/` - 获取活动列表
- `POST /api/activities/` - 创建活动
- `GET /api/activities/<id>` - 获取活动详情
- `PUT /api/activities/<id>` - 更新活动
- `POST /api/activities/<id>/start` - 开始活动
- `POST /api/activities/<id>/stop` - 结束活动
- `POST /api/activities/ai/generate` - AI生成活动

### 响应接口
- `POST /api/responses/` - 提交响应
- `GET /api/responses/activity/<id>` - 获取活动响应
- `POST /api/responses/<id>/feedback` - 添加反馈
- `POST /api/responses/ai/analyze/<id>` - AI分析响应

### 分析接口
- `GET /api/analytics/dashboard` - 获取仪表板数据
- `GET /api/analytics/leaderboard/<id>` - 获取排行榜
- `GET /api/analytics/activity/<id>/analytics` - 获取活动分析

### 管理接口
- `GET /api/admin/users` - 获取所有用户
- `GET /api/admin/stats` - 获取系统统计
- `POST /api/admin/backup` - 创建备份

## 🎨 界面功能

### 教师界面
- **课程管理**: 创建、编辑、删除课程
- **学生管理**: 导入学生名单，查看学生信息
- **活动创建**: 手动创建或AI生成学习活动
- **实时监控**: 查看活动进行情况和学生参与度
- **数据分析**: 查看详细的学习分析报告

### 学生界面
- **课程浏览**: 查看可注册的课程
- **活动参与**: 参与各种学习活动
- **成绩查看**: 查看个人成绩和反馈
- **进度跟踪**: 查看学习进度和参与统计

### 管理员界面
- **用户管理**: 管理所有用户账户
- **系统监控**: 监控系统使用情况
- **数据管理**: 系统数据备份和恢复
- **统计分析**: 查看系统整体统计信息

## 🤖 AI功能详解

### 活动生成
- 基于课程内容自动生成适合的学习活动
- 支持多种活动类型：投票、测验、词云、简答题、迷你游戏
- 教师可以审查和优化AI生成的内容

### 答案分析
- 自动分析学生回答的相似性
- 识别回答中的共同主题和模式
- 提供学习洞察和改进建议

### 个性化反馈
- 为每个学生生成个性化的学习反馈
- 基于回答质量提供建设性建议
- 鼓励性话语和学习指导

## 📱 响应式设计

- **移动优先**: 优先考虑移动设备体验
- **自适应布局**: 适配不同屏幕尺寸
- **触摸友好**: 优化触摸操作体验
- **快速加载**: 优化页面加载速度

## 🚀 部署指南

### Heroku部署
1. 创建Heroku应用
2. 设置环境变量
3. 推送代码到Heroku
4. 启动应用

### Vercel部署
1. 连接GitHub仓库
2. 配置构建设置
3. 设置环境变量
4. 部署应用

### Docker部署
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "wsgi:app"]
```

## 🔒 安全特性

- **密码加密**: 使用Werkzeug进行密码哈希
- **会话管理**: 安全的用户会话处理
- **权限控制**: 基于角色的访问控制
- **数据验证**: 前后端双重数据验证

## 📈 性能优化

- **数据库索引**: 优化数据库查询性能
- **缓存机制**: 实现数据缓存减少数据库负载
- **异步处理**: 使用异步任务处理耗时操作
- **CDN加速**: 静态资源CDN加速

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📄 许可证

MIT License

## 📞 联系方式

- 项目维护者: [Your Name]
- 邮箱: [your-email@example.com]
- 项目地址: [GitHub Repository URL]

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者和教育工作者！

---

**智能课堂互动平台** - 让学习更智能，让教学更高效！ 🎓✨