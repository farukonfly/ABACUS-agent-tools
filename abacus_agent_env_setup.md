# abacus-agent 环境搭建笔记

本文档记录了 `abacus-agent` 环境的创建及相关依赖的安装步骤。

## 1. 创建并激活 Conda 环境

使用 Python 3.11 创建名为 `abacus-agent` 的新环境，并激活：

```bash
conda create -n abacus-agent python=3.11 -y
source activate abacus-agent  # 或使用 conda activate abacus-agent
```

## 2. 安装基础依赖环境

通过 conda 安装 `abacus` 和 `mpich`，并通过 pip 安装 `mcp`：

```bash
conda install abacus mpich -c conda-forge -y
pip install mcp
```

## 3. 以可编辑模式安装本地代码库

为了实现“链接到代码，代码变了也跟着变”的效果，需要使用 `pip install` 的 `-e` (或 `--editable`) 参数。这种安装方式会在当前环境和代码目录之间建立符号链接。

```bash
cd /home/farukon/Repository/deer-flow/packages/ABACUS-agent-tools
pip install -e .
```

## 4. 启动
安装完成后，可以通过以下命令启动 `abacus-agent`：

```bash
abacusagent --model fastmcp --host 0.0.0.0 --port 50001
```
