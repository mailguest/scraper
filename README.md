# Scraper Project

## 项目简介

这是一个简单的内容爬虫项目，支持定时抓取外部网站的数据，并将抓取到的数据保存到本地。项目中包括不同网站的爬虫实现，如**华尔街见闻**、**新浪财经**、**财联社** 等，未来可能会再持续增加。

## 项目结构

```bash
├── /apis/                           # Flask API 逻辑
├── /config/                        # 配置文件
├── /scripts/                       # 脚本及业务类
├── /static/                        # 静态文件
├── /templates/                     # 模板文件
├── /tests/                         # 测试目录
├── /utils/                         # 工具类目录
├── run.py                          # 统一启动脚本
```

## 环境配置

- **Python 版本**: 3.10.15
- **依赖包**: 列在 `requirements.txt` 中

### 安装依赖

在本地开发环境中，可以通过以下命令安装所需的依赖：

```bash
pip install -r requirements.txt
```

## 启动步骤

### 1. 克隆项目

```bash
git clone <your-repository-url>
cd <your-repository-folder>
```

### 2. 使用 Docker 构建和运行

#### 构建 Docker 镜像

在项目根目录下执行以下命令，构建 Docker 镜像：

```bash
docker build -t scraper-app .
```

#### 运行 Docker 容器

使用以下命令启动 Docker 容器，并传递本地的 `data` 和 `logs` 目录：

```bash
docker run -d \
  --name scraper-app \
  -e DATA_DIR=./data \
  -e LOGS_DIR=./logs \
  -v ./data:/app/data \
  -v ./logs:/app/logs \
  -p 5001:5001 \
  mailguest/scraper-app

docker run -d --name scraper-app -e DATA_DIR=./data -e LOGS_DIR=./logs -v ./data:/app/data -v ./logs:/app/logs -p 5001:5001 mailguest/scraper-app
```

- **DATA_DIR**: 爬取的数据存储目录，外部路径传递。
- **LOGS_DIR**: 日志存储目录，外部路径传递。
- **5001 端口**: 容器内运行的 Flask API 端口，映射到主机的 5001 端口。

#### 使用 Docker Compose（可选）

你也可以使用 Docker Compose 来管理启动和环境变量。运行以下命令启动服务：

```bash
docker-compose up -d
```

### 3. 本地启动 (无 Docker)

如果你不想使用 Docker，可以在本地直接运行项目。确保已安装 Python 3.10.15，并执行以下命令：

#### 安装依赖

```bash
pip install -r requirements.txt
```

#### 运行项目

```bash
python run.py
```

## API 使用

项目启动后，API 默认在 `http://localhost:5001` 提供服务。

### 获取数据

```bash
GET /data
```

- **查询参数**:
  - `page`: 分页页码 (默认为 1)
  - `limit`: 每页条数 (默认为 10)
  - `date`: 可选，指定获取某天的数据，格式为 `YYYY-MM-DD`

示例请求：

```bash
curl "http://localhost:5001/data?page=1&limit=10&date=2024-10-22"
```

## 日志管理

- 日志文件按天切割，保存在 `logs/` 目录下。
- 每个爬虫类（如 `WallStreetCNScraper` 和 `SinaFinanceScraper`）都有各自的日志文件 (`wallstreet_scraper.log` 和 `sina_scraper.log`)。
- 项目自动删除超过 30 天的日志文件，确保日志不会无限增长。

## 数据存储

- 爬取的数据目前以mongodb存储
- ip代理以文件方式存储在data目录中

## 环境变量

- `DATA_DIR`: 爬取数据的存储目录（默认为 `./data`）。
- `LOGS_DIR`: 日志文件的存储目录（默认为 `./logs`）。
`

## 常见问题

### 1. 如何修改爬取的目标网站？

你可以在 `config/urls.json` 中配置需要爬取的目标网站。每个网站的 URL、请求方式、限制参数都可以在此文件中配置。

### 2. 如何查看日志？

日志文件存储在 `logs/` 目录下，可以直接查看日志文件，或者使用 `docker logs` 查看运行中的容器日志。

---

## 贡献

如果你对这个项目有建议或改进，欢迎提交 Pull Request 或 Issue。

```

### 关键更新：
1. **日志管理**：每个 `scraper` 类都添加了日志记录功能，日志文件按天切割并保存在 `logs/` 目录下。
2. **爬虫类更新**：`WallStreetCNScraper` 和 `SinaFinanceScraper` 已更新，增加了 `source` 和 `date` 字段，并使用工厂模式管理。
3. **API**：API 服务在 `http://localhost:5001` 运行，支持通过日期和分页获取数据。

如果有其他问题，欢迎告诉我！