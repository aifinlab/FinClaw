---
description: ⚠️ DEPRECATED - 上海财经大学 FastGPT 平台接口，接入「匡时财经教育大模型」和「博弈与社会课程智能体」。当用户需要使用上财校内 AI 助教或教育大模型时使用。
---

# fastgpt-skill (已废弃)

⚠️ **状态: DEPRECATED (2026-03-25)**

> 此 Skill 已废弃，不再维护。原因：需要上财校内网络或 VPN，适用范围受限。

## 废弃原因
- 需要上财校内网络或 VPN 访问
- 适用范围受限，无法公开使用
- 接口不稳定

## 替代方案
- 使用系统内置的 Claude/GPT 等大模型接口

---

上财 FastGPT 平台 OpenAPI 封装。

## 核心能力

- 匡时财经教育大模型问答
- 博弈与社会课程智能体
- 多 agent 配置支持

## 接口

- 上财 FastGPT：llm.sufe.edu.cn OpenAPI

## 使用

```bash
node "$SKILLS_ROOT/fastgpt-skill/index.js" --query "什么是纳什均衡"
```

## 注意

- 需要上财校内网络或 VPN
- agent 配置在 index.js 中预设
