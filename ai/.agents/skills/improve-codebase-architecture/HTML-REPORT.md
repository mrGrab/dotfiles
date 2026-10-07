# HTML Report Format

Save the architecture review as one HTML file in the operating system's temporary directory. Load Tailwind and Mermaid from CDNs. Use Mermaid for diagrams that show relationships. Use HTML elements and inline SVG for diagrams such as mass diagrams and cross-sections. Use both types. Do not use Mermaid for every diagram, or the report may look generic.

## Scaffold

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Architecture review for {{repo name}}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script type="module">
      import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
      mermaid.initialize({
        startOnLoad: true,
        theme: "neutral",
        securityLevel: "loose",
      });
    </script>
    <style>
      /* Use custom styles for details that Tailwind cannot handle well,
         such as dashed seam lines and hand-drawn arrowheads. */
      .seam {
        stroke-dasharray: 4 4;
      }
      .leak {
        stroke: #dc2626;
      }
      .deep {
        background: linear-gradient(135deg, #0f172a, #1e293b);
      }
    </style>
  </head>
  <body class="bg-stone-50 text-slate-900 font-sans">
    <main class="max-w-5xl mx-auto px-6 py-12 space-y-12">
      <header>...</header>
      <section id="candidates" class="space-y-10">...</section>
      <section id="top-recommendation">...</section>
    </main>
  </body>
</html>
```

## Header

Show the repository name, date, and a short legend: a solid box means a module, a dashed line means a seam, a red arrow means leakage, and a thick dark box means a deep module. Do not add an introduction. Start with the candidates.

## Candidate card

Use diagrams to explain each candidate. Keep the text short and plain. Use the glossary terms from the `/codebase-design` skill.

Put each candidate in its own `<article>`:

- **Title**: Use a short name for the proposed deepening. Example: "Collapse the Order intake pipeline".
- **Badges**: Show recommendation strength (`Strong` in emerald, `Worth exploring` in amber, or `Speculative` in slate). Also show the dependency category: `in-process`, `local-substitutable`, `ports & adapters`, or `mock`.
- **Files**: List file paths in a monospaced font, such as `font-mono text-sm`.
- **Before and after diagrams**: Place them side by side. These are the main part of the candidate card. See the patterns below.
- **Problem**: State the problem in one sentence.
- **Solution**: State the change in one sentence.
- **Wins**: List benefits in bullets of six words or fewer. Examples: "Tests hit one interface", "Pricing logic stops leaking", "Delete 4 shallow wrappers".
- **ADR callout**, if needed: Add one line in an amber box.

Do not add explanatory paragraphs. If a diagram needs a paragraph to explain it, redraw the diagram.

## Diagram patterns

Choose a pattern that fits the candidate. Use different patterns across the report. The diagrams should not all look the same.

### Mermaid graph (the workhorse for dependencies / call flow)

Use a Mermaid `flowchart` or `graph` to show calls between modules and make problems clear. Put it in a card styled with Tailwind. Use `classDef` to show leakage edges in red and the deep module in a dark colour. A sequence diagram can show a change such as six calls becoming one.

```html
<div class="rounded-lg border border-slate-200 bg-white p-4">
  <pre class="mermaid">
    flowchart LR
      A[OrderHandler] --> B[OrderValidator]
      B --> C[OrderRepo]
      C -.leak.-> D[PricingClient]
      classDef leak stroke:#dc2626,stroke-width:2px;
      class C,D leak
  </pre>
</div>
```

### Hand-built boxes and arrows

Use bordered and labelled `<div>` elements for modules. Draw arrows with inline SVG `<line>` or `<path>` elements, positioned over a relative container. Use this pattern when the after diagram should show one thick-bordered deep module with faded internal details. Mermaid may not show this clearly.

### Cross-section

Stack horizontal bands (`h-12 border-l-4`) to show each layer a call passes through. Before: show six thin layers that do little work. After: show one thick band with the combined responsibility.

### Mass diagram

Show two rectangles for each module: one for its interface and one for its implementation. Before: make the interface rectangle almost as tall as the implementation rectangle to show a shallow module. After: make the interface rectangle short and the implementation rectangle tall to show a deep module.

### Call-graph collapse

Before: Show function calls as a tree of nested boxes. After: Show the same tree inside one box, with internal calls faded.

## Style guidance

- Use an editorial style, not a dashboard style. Leave plenty of space. You may use serif headings (`font-serif`) with stone and slate colours.
- Use colour sparingly: one accent colour, such as emerald or indigo; red for leakage; and amber for warnings.
- Keep diagrams about 320 pixels tall. This lets readers compare them side by side without scrolling.
- Use `text-xs uppercase tracking-wider` for module labels. This makes them look like diagram labels, not user interface text.
- Use only the Tailwind CDN script and the Mermaid ESM import. Keep the rest of the report static. Add no application code or interaction beyond Mermaid rendering.

## Top recommendation section

Use one larger card. Include the candidate name, one sentence explaining why it is the top choice, and a link to its card.

## Tone

Use concise, plain English. Use the architecture terms from the `/codebase-design` skill. Keep the wording consistent, even when shorter alternatives seem easier.

**Use exactly:** module, interface, implementation, depth, deep, shallow, seam, adapter, leverage, locality.

**Do not substitute:** Use "module", not component, service, or unit. Use "interface", not API or signature. Use "seam", not boundary. Do not use layer or wrapper when you mean module.

**Phrasings that fit the style:**

- "Order intake module is shallow: interface nearly matches the implementation."
- "Pricing leaks across the seam."
- "Deepen: one interface, one place to test."
- "Two adapters justify the seam: HTTP in prod, in-memory in tests."

**Wins bullets** should state the gain using glossary terms. Examples: _"locality: bugs stay in one module"_, _"leverage: one interface, many call sites"_, _"interface shrinks; implementation absorbs the wrappers"_. Do not write _"easier to maintain"_ or _"cleaner code"_. These phrases are not in the glossary and do not explain the benefit.

Do not hedge or add filler such as "it's worth noting that". Turn short statements into bullets where useful. Remove bullets that add no value. If a term is not in the `/codebase-design` glossary, use a glossary term instead of inventing one.
