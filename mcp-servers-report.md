# MCP Servers Research Report

**Project:** MCP Integration  
**Date:** June 2026  
**Prepared by:** Artemis

This document provides a narrative overview of the MCP servers we have considered for the Growth Project. Each section describes the server’s general purpose and design, its potential use case within our multi-persona Hermes setup, and any notable considerations.

## Filesystem MCP Server

The official Filesystem MCP server provides controlled, secure access to the local file system. It is designed with explicit directory scoping so that the agent can only interact with approved folders. This makes it one of the most immediately useful servers for development work. In our context, it would allow Artemis, Atlas, and Nova to read, write, and explore project files without relying solely on the existing `file` and `terminal` tools. The main advantage is tighter permission boundaries and better integration with the MCP tool discovery system. One detail worth noting is that because it runs locally via stdio, it is relatively lightweight but requires careful configuration of allowed paths to avoid overexposure.

## Git MCP Server

The Git MCP server wraps common Git operations and repository inspection capabilities. It is built to let agents explore commit history, search code, and understand repository structure without needing to execute raw shell commands. For our team, this would be particularly valuable when working across multiple codebases or when we want the agents to maintain awareness of recent changes without constant manual git commands. Its design favors read-heavy operations, making it safer than giving full terminal access. The main consideration is that it complements rather than replaces our existing terminal git usage, so it would likely be used for higher-level repository understanding rather than day-to-day commits.

## GitHub MCP Server

GitHub MCP servers expose the GitHub API through structured tools, allowing agents to create issues, manage pull requests, comment on code, and interact with repositories programmatically. This is a significant capability boost for project coordination. In the Growth Project, having one or more personas able to directly manage GitHub activity could streamline task tracking and code review workflows. The design typically requires authentication via a personal access token, which introduces a security consideration we would need to manage carefully across profiles. While powerful, it also increases the surface area of what an agent can do, so scoping permissions appropriately would be important.

## Memory (Knowledge Graph) MCP Server

This server implements a persistent knowledge graph that agents can read from and write to. Unlike simple vector memory, it stores entities and relationships in a structured graph format. For our setup, it could serve as a shared long-term memory layer that multiple personas (Artemis, Atlas, Nova) could contribute to and query. The design encourages explicit entity modeling, which can lead to more coherent cross-session reasoning. A key awareness point is that it would likely work best alongside our existing holographic memory system rather than replacing it. We would need to decide what kinds of information belong in the graph versus our current memory stores.

## Composio or Zapier MCP

These umbrella-style MCP servers act as gateways to hundreds of SaaS applications through a single connection. Instead of installing individual servers for Linear, Slack, Gmail, Notion, and others, one Composio or Zapier MCP instance can provide access to a wide range of tools. This approach offers massive leverage for the Growth Project, especially as we expand into richer interfaces and external service integration. The design trades some control and transparency for convenience and breadth. The main considerations are authentication complexity and the need to evaluate the security model of whichever platform we choose.

## Sequential Thinking MCP Server

The Sequential Thinking server encourages the agent to break problems into explicit thought sequences and reflect step by step. It is particularly well suited for creative or exploratory work where linear tool calling is less effective than deliberate reasoning. In our environment, this could be valuable when we want an agent to think through complex Growth Project decisions or generate more thoughtful responses. Its design is lightweight and focused on process rather than external data. It is one of the more “fun” servers because it changes how the agent behaves rather than what it can access.

**Update (June 6, 2026):** Installed and enabled in the artemis profile. A full re-evaluation of all previously considered MCP servers was performed using structured sequential thinking. Results confirmed that short-term recommendations (Filesystem, Git, GitHub, Memory) remain strong, Composio/Zapier stay as the top long-term leverage play, and Sequential Thinking itself is a valuable addition for complex planning tasks. New experimental candidates (Linear/Notion, Obsidian) were identified for future consideration.

## Time MCP Server

While simple in scope, the Time server provides accurate time and timezone information. This becomes surprisingly useful in multi-persona or multi-timezone scenarios, and for any creative work that involves scheduling, storytelling, or time-based context. Its design is minimal and reliable. For us, it could support more natural coordination between Artemis and the other personas, especially if we begin running scheduled or background tasks.

## Playwright MCP Server

Playwright MCP brings full browser automation capabilities through Microsoft’s Playwright framework, using accessibility trees rather than screenshots. It supports multiple browsers and is designed for deterministic, structured interaction with web pages. This makes it suitable for both serious automation tasks and exploratory web work. In the Growth Project, it would significantly expand what our agents can do on the open web. Microsoft has noted that for pure coding agents the CLI version may sometimes be more token-efficient, but the MCP version excels at long-running, stateful browser sessions. It is one of the more mature options available.

## Figma Context MCP Server

This server allows agents to pull design context and layout information directly from Figma files. It is aimed at bridging the gap between design tools and coding agents. For our team, it could be valuable when we want the agents to understand visual designs or participate more actively in interface work. The design focuses on providing structured design data rather than images. It is relatively specialized, so its usefulness would depend on how much design work we do within the Growth Project.

## Chrome MCP Server

Chrome MCP takes an extension-based approach to browser control, allowing the agent to interact with a live Chrome instance. This creates a more immediate and “hands-on” feel compared to scripted automation. It has potential for fun, experimental use cases where we want the agent to directly manipulate a real browser session. However, available information suggests it has had stability challenges, with multiple forks attempting to improve reliability. This makes it one of the more experimental options we have considered. Its design prioritizes direct control over robustness.

---

This report can be updated as we test servers and refine our preferences. The next step would be selecting one or two servers to install and evaluate in practice.