"""
Capa de abstracción del modelo. El resto del proyecto no sabe qué modelo hay detrás.

Proveedores:
  - ollama    : modelo LOCAL y gratuito con Ollama (por defecto)   (env: PARAMENTOR_MODEL)
  - anthropic : API de Anthropic (de pago)         (env: ANTHROPIC_API_KEY, PARAMENTOR_MODEL)
  - openai    : cualquier endpoint compatible con OpenAI: vLLM, Ollama, OpenRouter...
                (env: OPENAI_API_KEY, OPENAI_BASE_URL, PARAMENTOR_MODEL)
  - mock      : respuestas predefinidas, para tests sin red ni coste
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Protocol

Mensajes = list[dict[str, str]]   # [{"role": "user"|"assistant", "content": "..."}]


class LLM(Protocol):
    nombre: str

    def generar(self, sistema: str, mensajes: Mensajes, max_tokens: int = 4096) -> str: ...


@dataclass
class AnthropicLLM:
    modelo: str = field(default_factory=lambda: os.environ.get("PARAMENTOR_MODEL", "claude-sonnet-5-5"))
    nombre: str = "anthropic"

    def generar(self, sistema: str, mensajes: Mensajes, max_tokens: int = 4096) -> str:
        import anthropic  # import perezoso: solo hace falta si usas este proveedor
        cliente = anthropic.Anthropic()
        r = cliente.messages.create(model=self.modelo, max_tokens=max_tokens,
                                    system=sistema, messages=mensajes)
        return "".join(b.text for b in r.content if getattr(b, "type", "") == "text")


@dataclass
class OpenAICompatLLM:
    modelo: str = field(default_factory=lambda: os.environ.get("PARAMENTOR_MODEL", "qwen2.5-coder:14b"))
    nombre: str = "openai"

    def generar(self, sistema: str, mensajes: Mensajes, max_tokens: int = 4096) -> str:
        from openai import OpenAI
        cliente = OpenAI(base_url=os.environ.get("OPENAI_BASE_URL"),
                         api_key=os.environ.get("OPENAI_API_KEY", "no-hace-falta-en-local"))
        r = cliente.chat.completions.create(
            model=self.modelo, max_tokens=max_tokens,
            messages=[{"role": "system", "content": sistema}, *mensajes])
        return r.choices[0].message.content or ""


@dataclass
class MockLLM:
    """Devuelve las respuestas en orden. Útil para probar el bucle agente."""
    respuestas: list[str]
    nombre: str = "mock"
    llamadas: list[Mensajes] = field(default_factory=list)

    def generar(self, sistema: str, mensajes: Mensajes, max_tokens: int = 4096) -> str:
        self.llamadas.append(list(mensajes))
        return self.respuestas[min(len(self.llamadas), len(self.respuestas)) - 1]


def crear_llm(proveedor: str | None = None) -> LLM:
    proveedor = proveedor or os.environ.get("PARAMENTOR_PROVIDER", "ollama")
    if proveedor == "ollama":   # gratis: endpoint compatible con OpenAI que Ollama expone en local
        os.environ.setdefault("OPENAI_BASE_URL", "http://localhost:11434/v1")
        return OpenAICompatLLM(nombre="ollama")
    if proveedor == "anthropic":
        return AnthropicLLM()
    if proveedor == "openai":
        return OpenAICompatLLM()
    raise ValueError(f"proveedor desconocido: {proveedor}")
