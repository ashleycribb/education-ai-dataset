---
title: AI in Education Dashboard
---

# AI in Education Dashboard

Welcome to the live dashboard for the xAPI Profile for AI in Education. This dashboard demonstrates how to analyze and visualize the data captured by our profile, providing both quantitative and qualitative insights into AI-learner interactions.

```js
import * as Plot from "https://cdn.jsdelivr.net/npm/@observablehq/plot@0.6/+esm";
import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";
```

```js
// Load the sample data
const statements = await d3.json("./sample-data.json");
```

```js
// Filter for statements where the AI Assistant is the actor
const aiStatements = statements.filter(d => d.actor.name === "AI Teacher's Assistant");
```

## Quantitative Analysis: AI Assistance Verbs

This chart shows the frequency of the different types of assistance provided by the AI Teacher's Assistant in our sample dataset.

```js
// Create a bar chart of the AI assistance verbs
const verbFrequencyPlot = Plot.plot({
  marks: [
    Plot.barY(aiStatements, Plot.groupX({y: "count"}, {x: (d) => d.verb.display["en-US"]})),
    Plot.ruleY([0])
  ],
  x: {
    label: "AI Assistance Verb",
  },
  y: {
    label: "Frequency",
    grid: true,
  },
  width: 600,
});

display(verbFrequencyPlot);
```

## Qualitative Analysis: AI Interaction Log

This table provides a detailed log of the interactions between the AI Teacher's Assistant and the learners. It shows the learner's prompt that triggered the assistance and the exact content of the AI's response, providing rich, qualitative data for analysis.

```js
// Create a filterable table of the AI interactions
const interactionLog = aiStatements.map(d => ({
  "Verb": d.verb.display["en-US"],
  "Learner Prompt": d.context?.extensions["https://w3id.org/xapi/ai/extensions/prompt"],
  "AI Assistance Content": d.context?.extensions["https://w3id.org/xapi/ai/extensions/assistance-content"],
}));

display(interactionLog);
```
