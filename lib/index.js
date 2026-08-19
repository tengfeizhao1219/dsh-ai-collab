// dsh-ai-collab —— DSH（DeepSeek Harness）插件入口
// 注册 ai_collab_init 工具：从随包分发的 templates/ 渲染并写入协作约定文件。
// 形态：cordis 插件（bundle），被 cordis.patch.yml 挂载为插件行 `ai-collab`。
import { defineTool } from "@deepseek-ai/dsh-tools";
import fs from "node:fs/promises";
import path from "node:path";

export const name = "ai-collab";

export const inject = ["tools"];

/** 模板目录：lib/ 上一级 templates/（随包分发，files 字段已包含）。 */
const TEMPLATE_DIR = new URL("../templates/", import.meta.url);

const TPL_FILES = [
  "CONTEXT.md.tpl",
  "ROLE_CARDS.md.tpl",
  "TASK_BOARD.md.tpl",
  "RELAY.md.tpl",
  "COMMLOG.md.tpl",
  "COLLABORATION.md.tpl",
  "NAVIGATION.md.tpl",
  "SESSION_BOOT.md.tpl",
  "LEARNINGS.md.tpl",
  "ADR.md.tpl",
  "REVIEW.md.tpl",
];

const DOC_DIRS = [
  "01-需求规划", "02-产品设计", "03-技术方案",
  "04-开发实现", "05-测试验收", "06-上线复盘",
];

const MECH_VERSION = "1.0.0";

function sanitize(name) {
  return String(name || "").replace(/[^\w.\-]/g, "-");
}

async function render(tplName, vars) {
  const url = new URL(tplName, TEMPLATE_DIR);
  let text;
  try {
    text = await fs.readFile(url, "utf-8");
  } catch {
    throw new Error(`template missing: ${tplName}`);
  }
  for (const [k, v] of Object.entries(vars)) {
    text = text.split(`{{${k}}}`).join(String(v ?? ""));
  }
  return text;
}

function today() {
  const d = new Date();
  const p = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`;
}

/**
 * ai_collab_init —— 在目标目录生成 AI 多角色协作约定文件（五件套 + 导航 + 接棒提示词 + docs 骨架）。
 * 供模型在「用户要启动一个新项目 / 把现有项目切换为 AI 协作模式」时调用。
 */
export function apply(ctx) {
  ctx.tools.register(defineTool({
    name: "ai_collab_init",
    description:
      "Initialize an AI multi-role collaboration project: generate the convention files " +
      "(CONTEXT / ROLE_CARDS / TASK_BOARD / RELAY / COMMLOG / COLLABORATION / NAVIGATION / SESSION_BOOT) " +
      "plus a docs/ skeleton into a target directory, implementing the \"files-as-communication\" " +
      "mechanism (O orchestrator + specialist roles, gate checks, session handover). " +
      "Call this when the user starts a new software project or wants an existing project to run " +
      "under AI-collaboration rules. Generated files are written to `dir` (default: current workspace).",
    parameters: {
      projectName: { type: "string", required: true, description: "Project name (also used as the directory name when dir is omitted)." },
      description: { type: "string", description: "One-line project positioning, written into CONTEXT.md." },
      techStack: { type: "string", description: "Tech stack, written into CONTEXT.md (default: 待定)." },
      dir: { type: "string", description: "Target directory. Default: <current workspace>/<projectName>." },
      constraints: { type: "array", items: { type: "string" }, description: "Hard constraints (owner decisions) written into CONTEXT.md and enforced by the Q role." },
    },
    output: {
      schema: {
        type: "object",
        additionalProperties: false,
        properties: {
          dir: { type: "string" },
          files: { type: "array", items: { type: "string" } },
          skipped: { type: "array", items: { type: "string" } },
        },
      },
    },
    async execute(args) {
      const projectName = String(args.projectName || "").trim();
      if (!projectName) throw new Error("projectName is required");
      const base = args.dir && String(args.dir).trim()
        ? path.resolve(String(args.dir).trim())
        : path.resolve(process.cwd(), sanitize(projectName));
      const constraints = (args.constraints || []).map(String);
      while (constraints.length < 3) constraints.push("—");
      await fs.mkdir(base, { recursive: true });

      const vars = {
        PROJECT_NAME: projectName,
        PROJECT_DESC: (args.description || "（待 owner 补充一句话定位）").trim(),
        START_DATE: today(),
        MECH_VERSION,
        TECH_STACK: (args.techStack || "待定").trim(),
        REPO_URL: "待定",
        HARD_CONSTRAINT_1: constraints[0],
        HARD_CONSTRAINT_2: constraints[1],
        HARD_CONSTRAINT_3: constraints[2],
        ARCH_SKETCH: "（待 Phase 0 技术栈确认后补充架构草图）",
        OWNER_DECISIONS: "技术栈 / 凭证与外部资源（见 RELAY 待拍板项）",
        EXTRA_OWNER_DECISIONS: "（随项目推进补充）",
        GLOSSARY_ROWS: "（随文档产出补充）",
      };

      const written = [];
      const skipped = [];
      for (const tpl of TPL_FILES) {
        const dst = path.join(base, tpl.slice(0, -4)); // 去掉 .tpl
        if (await exists(dst)) { skipped.push(dst); continue; }
        const content = await render(tpl, vars);
        await fs.writeFile(dst, content, "utf-8");
        written.push(dst);
      }
      // docs/ 目录骨架（不覆盖已有内容）
      for (const d of DOC_DIRS) {
        const dir = path.join(base, "docs", d);
        await fs.mkdir(dir, { recursive: true });
        const keep = path.join(dir, ".gitkeep");
        if (!(await exists(keep))) await fs.writeFile(keep, "", "utf-8");
      }
      // 项目 README 入口
      const readme = path.join(base, "README.md");
      if (!(await exists(readme))) {
        await fs.writeFile(readme, [
          `# ${projectName}`,
          "",
          `> 由 ai-collab ${MECH_VERSION} 生成（${vars.START_DATE}）。这是一个 **AI 多角色协作项目**：沟通介质是文件，没有 IM、没有会议。`,
          "",
          vars.PROJECT_DESC,
          "",
          "## 快速开始（新会话接棒）",
          "",
          "把 `SESSION_BOOT.md` 中的接棒提示词发给你的 AI，它会按序读取约定文件完成上下文继承，然后即可派发任务。",
          "",
          "## 约定文件（第一读者是 AI）",
          "",
          "| 文件 | 作用 |",
          "|---|---|",
          "| `CONTEXT.md` | 项目速览（第一必读） |",
          "| `ROLE_CARDS.md` | 角色卡（O + 专业角色） |",
          "| `TASK_BOARD.md` | 任务看板（任务级状态） |",
          "| `RELAY.md` | 阶段流水线 + 里程碑 + 待拍板项 |",
          "| `COMMLOG.md` | 沟通交接记录（倒序） |",
          "| `COLLABORATION.md` | 协作总规 |",
          "| `NAVIGATION.md` | 文档导航与交叉引用索引 |",
          "",
        ].join("\n"), "utf-8");
        written.push(readme);
      }

      return {
        dir: base,
        files: written,
        skipped,
        note: "新会话粘贴 SESSION_BOOT.md 接棒提示词开始协作；运行 scripts/check.py 验证机制文件一致性；可选 git init + scripts/git_sync.sh 启动同步守护。",
      };
    },
    presentCall: (args) => ({
      card: "generic",
      title: `Initialize ai-collab project: ${args.projectName || ""}`,
      kind: "other",
      rawInput: args,
    }),
  }));
}

async function exists(p) {
  try { await fs.access(p); return true; } catch { return false; }
}
