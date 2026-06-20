## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
  **Automaticky zajišťuje git post-commit hook** — není třeba spouštět ručně.
  Manuálně (po klonování repo nebo při potížích):
  ```
  graphify update backend/rates/ && graphify update frontend/src/
  graphify merge-graphs backend/rates/graphify-out/graph.json frontend/src/graphify-out/graph.json --out graphify-out/graph.json
  ```
