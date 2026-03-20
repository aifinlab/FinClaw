请在机器上执行以下命令，自动安装 FinClaw 命令行工具并配置金融 Skills：

```bash
curl -fsSL https://raw.githubusercontent.com/aifinlab/FinClaw/main/install.sh | bash
```

安装完成后请重启 Agent，重启后即可使用 FinClaw 金融 Skills 能力。

如果只需要安装 CLI：

```bash
curl -fsSL https://raw.githubusercontent.com/aifinlab/FinClaw/main/install.sh | bash -s -- --cli-only
```

安装后可通过 `finclaw search 股票` 搜索、`finclaw install akshare-stock` 安装 Skills 到当前 workspace。
