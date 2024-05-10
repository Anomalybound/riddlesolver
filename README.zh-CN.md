# RiddleSolver 🎩🔍

[English](README.md) | [简体中文](README.zh-CN.md)

[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-0.1.9-blue.svg)](https://github.com/AnomalyBound/riddlesolver)
[![Last Commit](https://img.shields.io/github/last-commit/AnomalyBound/riddlesolver)](https://github.com/AnomalyBound/riddlesolver/commits)

[![Code Size](https://img.shields.io/github/languages/code-size/AnomalyBound/riddlesolver)](https://github.com/AnomalyBound/riddlesolver)
[![Downloads](https://img.shields.io/pypi/dm/riddlesolver)](https://pypi.org/project/riddlesolver/)

女士们,先生们,男孩和女孩们,欢迎来到有史以来最不可思议、最令人兴奋、最搞笑的 Git commit 总结器的世界!🤯🎪 隆重推出...RiddleSolver!🎭

RiddleSolver 就像一个神奇的精灵🧞‍,它可以满足你理解 Git commits 这些神秘谜题的愿望。只需挥动虚拟魔杖🪄,RiddleSolver 就能变出清晰、简洁、标准化的 Git commit 信息摘要,让你惊叹不已!🎆

## ✨ 特性

- 🔮 揭开 Git commits 的神秘面纱,以令人惊叹的洞察力揭示其真正目的
- 🎯 只关注某个特定分支的唯一提交,消除处理重叠提交的麻烦
- 🌿 在本地仓库和远程 GitHub 仓库上施展魔法(无需克隆!)
- 📅 可以指定自定义日期范围,让你专注于最重要的提交
- 🧙‍♂️ 支持按特定作者或分支筛选提交,让你完全掌控分析过程
- 🔧 使用直观的 config 命令,轻松设置各项配置
- 🔑 通过神奇的 grant-auth 命令,便捷地进行 GitHub 身份验证
- 📦 作为一个多功能开发工具包,提供结构良好的 API,可无缝集成到你的项目中
- 🎨 附赠一个 Streamlit 应用程序,为提交分析提供令人愉悦和直观的用户界面

## 🧪 安装

要释放 RiddleSolver 的强大力量,只需在终端中念出以下咒语:

```bash
pip install riddlesolver
```

瞧!精灵现在听候你的差遣了!🧞️✨

## 📖 使用指南

### 召唤精灵

要召唤 RiddleSolver 精灵,解开 Git commits 的谜题,请使用以下命令:

```bash
riddlesolver <repo> [options]
```

将 `<repo>` 替换为本地仓库路径、远程仓库的 URL 或 GitHub 仓库的 owner/repo 格式。

### 选项 🎛️

- `-s`, `--start-date`: 指定提交的起始日期(YYYY-MM-DD)
- `-e`, `--end-date`: 指定提交的结束日期(YYYY-MM-DD) 
- `-d`, `--days`: 指定要包含在摘要中的天数(例如,`-d 2` 表示最近 2 天)
- `-w`, `--weeks`: 指定要包含在摘要中的周数(例如,`-w 1` 表示最近一周)
- `-m`, `--months`: 指定要包含在摘要中的月数(例如,`-m 3` 表示最近 3 个月)
- `-b`, `--branch`: 指定精灵关注的分支名称
- `-a`, `--author`: 指定要按作者的电子邮件或姓名筛选提交
- `-o`, `--output`: 指定将精灵的智慧保存为 markdown 文件的路径
- `-c`, `--command`: 执行命令(`config` 或 `grant-auth`)

⚠️ **重要提示**: 将 RiddleSolver 与 GitHub 远程仓库一起使用时,你有两个选择:

1. 使用 `grant-auth` 命令授予必要的权限,并利用 GitHub API 获取提交。

2. 如果选择不进行身份验证,RiddleSolver 仍然可以在不使用 GitHub API 的情况下获取提交。

### 配置精灵

要定制精灵的行为,并授予其访问 OpenAI API 的权限,请使用神奇的 `config` 子命令:

```bash
riddlesolver config <section> <key> <value>
```

例如,要设置 OpenAI API 密钥:

```bash
riddlesolver config openai api_key YOUR_API_KEY
```

精灵会将其秘密存储在位于 `~/.riddlesolver/config.ini` 的神圣卷轴中。

### 示例 🌟

召唤精灵,解开本地仓库的谜题:

```bash
riddlesolver /path/to/local/repo
```

召唤精灵,在特定日期范围内破解远程仓库的提交之谜:

```bash
riddlesolver https://github.com/owner/repo -s 2023-01-01 -e 2023-01-31
```

召唤精灵,揭示特定分支的奥秘:

```bash
riddlesolver /path/to/local/repo -b feature-branch
```

召唤精灵,探寻特定作者的提交轨迹:

```bash
riddlesolver owner/repo -a john@example.com
```  

召唤精灵,将其智慧凝结成 markdown 文件:

```bash
riddlesolver /path/to/local/repo -o summary.md
```

授予精灵 GitHub 身份验证的神力:

```bash
riddlesolver --command grant-auth 
```

**🛠️ 开发者工具包**
---------------------------

RiddleSolver 不仅是一个命令行工具,它还为开发者提供了结构良好的 API,方便将其功能集成到自己的项目中。你可以使用 RiddleSolver 作为开发工具包来获取提交、生成摘要,并将摘要保存到文件。

### **API 函数**

1.  `fetch_commits(repo_path, start_date, end_date, branch=None, author=None, access_token=None, repo_type=None)`: 在指定的日期范围内从仓库获取提交,可选择按分支和作者筛选。如果提供了 `access_token` 并将 `repo_type` 设置为 `"github"`,它将使用 GitHub API 获取提交。否则,它将在不使用 API 的情况下获取提交。返回提交对象的列表。
    
2.  `generate_summary(commit_batches, config)`: 使用 OpenAI API 生成提交批次的摘要。返回生成的摘要字符串。
    
3.  `save_summary_to_file(summary, output_file)`: 将提交摘要保存到指定输出路径的文件中。
    
### **使用示例**

以下是如何在你自己的项目中使用 RiddleSolver 作为开发工具包的示例:

```python
from riddlesolver import fetch_commits, generate_summary, save_summary_to_file
from riddlesolver.config import load_config_from_file  
from datetime import datetime

repo_path = "https://github.com/username/repo.git"
start_date = datetime(2023, 1, 1)
end_date = datetime(2023, 12, 31)
branch = "main"
author = "john@example.com"
access_token = "YOUR_ACCESS_TOKEN"
repo_type = "github"
output_file = "summary.md"

config = load_config_from_file()
batched_commits = fetch_commits(repo_path, start_date, end_date, branch, author, access_token, repo_type)
summary = generate_summary(batched_commits, config)
save_summary_to_file(summary, output_file)
```

## 🔧 配置

精灵的秘密藏在位于 `~/.riddlesolver` 的神圣卷轴里,让我们一探究竟:

```ini
[openai]
api_key = your_openai_api_key
model = gpt-3.5-turbo 
base_url = https://api.openai.com/v1

[general]
cache_dir = ~/.cache/repo_cache
cache_duration = 7

[github]
access_token = your_github_access_token
```

- `api_key`: 将 `INPUT YOUR API KEY` 替换为你的 OpenAI API 密钥(精灵施展魔法必不可少!)
- `model`: 指定精灵使用的 OpenAI 模型(默认为 `gpt-3.5-turbo`)  
- `base_url`: 指定 OpenAI API 的基本 URL(默认为 `https://api.openai.com/v1`)
- `cache_dir`: 指定精灵存储缓存仓库的目录(默认为 `~/.cache/repo_cache`) 
- `cache_duration`: 指定精灵保留缓存仓库的天数(默认为 `7`)
- `access_token`: 提供你的 GitHub 访问令牌,授予精灵访问仓库的权限(如果不需要,请留空)

## 🤝 贡献 

如果你想为增强精灵的魔力贡献一份力量,让它变得更加非凡,欢迎在 [GitHub 仓库](https://github.com/AnomalyBound/riddlesolver)上提出 issue 或提交 pull request。精灵感谢所有的帮助与支持!

## 📜 许可证

RiddleSolver 基于 [MIT 许可证](https://opensource.org/licenses/MIT)发布,赋予你使用、修改和分发精灵的自由,任你发挥!

## 🙏 致谢

精灵要向强大的 OpenAI 表示感谢,是它赋予了语言理解和生成的神奇力量。没有他们的 API,精灵就只是一个普通的提交总结工具。

现在,做好惊叹的准备吧!RiddleSolver 将为你揭开 Git commits 的奥秘,为你的开发之旅带来全新的清晰与透彻!🎉✨