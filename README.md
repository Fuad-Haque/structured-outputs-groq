# structured-outputs-groq

<div align="center">

[![Typing SVG](https://readme-typing-svg.demolab.com?font=Sora&weight=700&size=22&duration=2800&pause=1000&color=6C63FF&center=true&vCenter=true&width=700&lines=Unstructured+Text+In.+Valid+JSON+Out.;Strict+Mode+%C2%B7+Zero+Repair+Logic;Groq+%C2%B7+OpenAI+SDK+%C2%B7+JSON+Schema;No+Malformed+JSON.+No+Retries.+No+Exceptions.)](https://git.io/typing-svg)

</div>

<div align="center">

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI_SDK-412991?style=for-the-badge&logo=openai&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-F55036?style=for-the-badge&logoColor=white)
![JSON](https://img.shields.io/badge/JSON_Schema-000000?style=for-the-badge&logo=json&logoColor=white)

</div>

---

## Overview

**structured-outputs-groq** is a schema-constrained JSON extraction pipeline. It takes 10 unstructured, real-world-shaped text inputs — product reviews of varying length, tone, and completeness — and returns a rigid, schema-valid JSON object for every single one. Same four fields, correct types, closed enum for sentiment, every time.

Free-text JSON generation from an LLM occasionally produces malformed or wrong-shaped output — missing fields, wrong types, extra keys — which silently corrupts anything downstream expecting a specific shape. This project uses OpenAI's **Structured Outputs** (`strict: true`) instead, which constrains decoding at the token level so an invalid shape is structurally impossible to emit.

It runs against **Groq's free-tier, OpenAI-compatible API** via the official `openai` Python SDK — meaning the exact same code runs against real OpenAI with a one-line `base_url` swap.

**Run it** → `python main.py` (see [Quick Start](#quick-start))

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Stack](#stack)
- [Extraction Schema](#extraction-schema)
- [Structured Outputs vs. Free-Text JSON](#structured-outputs-vs-free-text-json)
- [Environment Variables](#environment-variables)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Author](#author)

---

## Features

| Feature | Detail |
|---------|--------|
| Strict Schema Enforcement | `response_format={"type": "json_schema", "strict": true}` — invalid shape is structurally impossible to emit, not just discouraged |
| Fixed 4-Field Schema | Every output has exactly `product_name`, `rating`, `sentiment`, `key_features` — no more, no fewer |
| Closed Enum for Sentiment | `sentiment` is constrained to a fixed set of values via the schema itself — never a stray label |
| Zero Repair Logic | No retry loop, regex, or JSON-repair step — strict mode guarantees valid shape on the first response |
| Provider-Portable | Identical `openai` SDK code runs against Groq or real OpenAI — swap only `base_url` |
| Diverse Test Set | 10 real-world-shaped product reviews spanning varying length, tone, and completeness |
| Free-Tier Backend | Runs entirely on Groq's free tier using `openai/gpt-oss-20b`, confirmed to support `strict: true` |

---

## Architecture

```
10 Unstructured Text Inputs (product reviews)
        │
        ├── One JSON Schema defined once (4 fields, closed enum)
        │
        ├── openai SDK → base_url override → Groq (openai/gpt-oss-20b)
        │
        ├── response_format = {"type": "json_schema", "strict": true}
        │
        └── Strict-mode constrained decoding
                │
                └── Schema-valid JSON returned — parsed directly, no repair step
```

### Extraction Flow

```
Read input text
        │
        ├── Build request with fixed JSON Schema + strict:true
        ├── Send to Groq via OpenAI-compatible endpoint
        ├── Model constrained at token level to schema shape
        └── Parse response directly → print JSON block
```

---

## Stack

| Layer | Technology |
|-------|------------|
| Language | Python |
| LLM SDK | `openai` — official Python SDK, unmodified |
| LLM Backend | Groq — `openai/gpt-oss-20b` (free tier) |
| Compatibility Layer | OpenAI-compatible endpoint via `base_url` override |
| Schema Format | JSON Schema (strict mode) |
| Config | python-dotenv |

---

## Extraction Schema

Every input is run against the same schema, defined once and reused across all 10 calls.

```json
{
  "type": "object",
  "properties": {
    "product_name": { "type": "string" },
    "rating": { "type": "number" },
    "sentiment": {
      "type": "string",
      "enum": ["positive", "negative", "neutral", "mixed"]
    },
    "key_features": {
      "type": "array",
      "items": { "type": "string" }
    }
  },
  "required": ["product_name", "rating", "sentiment", "key_features"],
  "additionalProperties": false
}
```

### Request / Response Example

**Input (unstructured review)**
```
"Battery life is solid, camera's a bit disappointing tbh. Screen is
gorgeous though. Overall happy with the Pixel 9 — would recommend."
```

**Output (schema-valid JSON)**
```json
{
  "product_name": "Pixel 9",
  "rating": 4,
  "sentiment": "mixed",
  "key_features": ["battery life", "camera", "screen"]
}
```

---

## Structured Outputs vs. Free-Text JSON

| Approach | How It Works | Reliability |
|----------|--------------|-------------|
| **Free-text JSON prompting** | Model is asked to "return JSON" in the prompt; output is parsed with `json.loads()` | Occasionally malformed — missing fields, wrong types, extra keys, or a non-JSON preamble |
| **Structured Outputs (strict mode)** | Schema is passed directly via `response_format`; token-level constrained decoding makes an invalid shape impossible to emit | Schema-valid on every call — no retry or repair logic needed |

---

## Environment Variables

### `.env`

```env
GROQ_API_KEY=your-groq-api-key
```

A documented `.env.example` is included in the repo.

---

## Quick Start

```bash
git clone https://github.com/Fuad-Haque/structured-outputs-groq
cd structured-outputs-groq
cp .env.example .env
pip install -r requirements.txt
python main.py
```

Expect 10 printed JSON blocks — each with exactly `product_name`, `rating`, `sentiment`, and `key_features`. No more, no fewer.

---

## Project Structure

```
structured-outputs-groq/
├── main.py              # Schema definition, Groq client setup, extraction loop
├── .env.example
├── requirements.txt
└── README.md
```

---

## Author

Built by [Fuad Haque](https://fuadhaque.com)

[fuadhaque.dev@gmail.com](mailto:fuadhaque.dev@gmail.com) · [Book a Call](https://cal.com/fuad-haque) · [GitHub](https://github.com/Fuad-Haque)
