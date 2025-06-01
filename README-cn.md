# SQLite 到 Drift ORM 转换工具

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Drift](https://img.shields.io/badge/Drift-ORM-green)

[简体中文](README-cn.md)
[English](README.md)

## 项目简介

这是一个将 SQLite 数据库文件自动转换为 Flutter [Drift ORM](https://drift.simonbinder.eu/) 所需 Dart 文件的 Python 脚本工具。它简化了在 Flutter 应用中集成 SQLite 数据库的过程，自动生成完整的数据库模型代码。

## 主要功能

- 🔄 自动转换 SQLite 表结构为 Drift Table 类
- 🧩 支持常见数据类型（INTEGER, TEXT, BLOB, REAL, NUMERIC）
- 🔑 处理主键约束（单主键、联合主键、自增主键）
- ⚙️ 转换字段约束（非空、唯一、默认值）
- ✨ 自动生成数据库连接配置代码
- 🧹 自动格式化生成的 Dart 代码

## 快速使用

```bash
# 基本用法（输出文件默认为输入文件名+.dart）
python sqlite2drift.py -i my_database.sqlite

# 指定输出文件
python sqlite2drift.py -i my_database.sqlite -o lib/database/app_db.dart
```

## 未来计划

我们计划拓展此工具以支持更多数据库类型：

- ✅ 当前支持：SQLite
- 📅 计划中：PostgreSQL

欢迎贡献代码或提出功能建议！
