"""Presentation helpers for the terminal interface."""

from __future__ import annotations

import json
import textwrap
from typing import Any

from cli.messages import colorize, info
from cli.tables import format_table
from core.constants import APP_NAME, APP_VERSION


class TerminalRenderer:
    """Renders consistent CLI output."""

    def __init__(self, width: int = 88) -> None:
        self.width = max(60, width)

    def banner(self) -> str:
        return self.panel(
            f"{APP_NAME} v{APP_VERSION}",
            [
                "Plataforma modular para auditorias autorizadas, inventario e relatorios.",
                "Use 'sentinelscan help' para ver navegacao, atalhos e comandos.",
            ],
        )

    def print_banner(self) -> None:
        print(self.banner())

    def print_json(self, payload: Any) -> None:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))

    def print_table(self, rows: list[dict[str, Any]], columns: list[str]) -> None:
        print(format_table(rows, columns))

    def print_status(self, status: dict[str, Any]) -> None:
        health = status.get("health", {})
        self.print_banner()
        print(
            self.panel(
                "Status do sistema",
                [
                    f"Root: {status['root_path']}",
                    f"Modules: {status['modules']} | Plugins: {status['plugins']} | Projects: {status['projects']}",
                    f"Inicializacao: {self.progress_bar(1, 1)}",
                ],
            )
        )
        metrics = [
            {"metric": "Aplicacao", "value": status["application"]},
            {"metric": "Versao", "value": status["version"]},
            {"metric": "Root", "value": status["root_path"]},
            {"metric": "Modulos", "value": status["modules"]},
            {"metric": "Plugins", "value": status["plugins"]},
            {"metric": "Projetos", "value": status["projects"]},
        ]
        health = status.get("health", {})
        if health:
            metrics.extend(
                [
                    {"metric": "Uptime", "value": f"{health.get('uptime_seconds')}s"},
                    {"metric": "Python", "value": health.get("python_version")},
                ]
            )
        self.print_table(metrics, ["metric", "value"])

    def print_help(self) -> None:
        print(
            self.panel(
                "Ajuda da CLI",
                [
                    "Navegar: digite o numero da opcao no menu interativo e pressione Enter.",
                    "Voltar ou sair: use 0 no menu interativo.",
                    "Cancelar entrada: pressione Ctrl+C para interromper a acao atual com seguranca.",
                    "Abrir modulos: use 'python main.py modules list' e depois 'modules run <id>'.",
                    "Gerar relatorios: use 'reports generate' ou execute modulo com '--report'.",
                    "Formatos: markdown, txt, json, csv e html.",
                    "Sair corretamente: escolha 0 no menu interativo para ver o resumo final.",
                ],
            )
        )
        commands = [
            {"command": "python main.py status", "purpose": "Ver saude do sistema"},
            {"command": "python main.py interactive", "purpose": "Abrir menu guiado"},
            {"command": "python main.py modules list", "purpose": "Listar modulos"},
            {"command": "python main.py reports list", "purpose": "Listar relatorios"},
            {"command": "python main.py maintenance clean-temp", "purpose": "Simular limpeza segura"},
            {"command": "python main.py maintenance clean-temp --yes", "purpose": "Limpar cache descartavel"},
        ]
        self.print_table(commands, ["command", "purpose"])

    def print_final_session_report(self, summary: dict[str, Any]) -> None:
        print(
            self.panel(
                "Relatorio final da sessao",
                [
                    f"Tempo total: {summary.get('duration_seconds', 0)}s",
                    f"Modulos usados: {summary.get('modules_used', 0)}",
                    f"Relatorios criados: {summary.get('reports_created', 0)}",
                    f"Erros encontrados: {summary.get('errors_found', 0)}",
                ],
            )
        )
        modules = summary.get("module_ids") or []
        if modules:
            self.print_table(
                [{"module": module_id} for module_id in modules],
                ["module"],
            )

    def print_clean_result(self, result: dict[str, Any]) -> None:
        status = "simulacao" if result.get("dry_run") else "concluida"
        print(
            self.panel(
                f"Limpeza segura ({status})",
                [
                    f"Arquivos analisados: {result.get('scanned_paths', 0)}",
                    f"Arquivos removidos: {result.get('removed_files', 0)}",
                    f"Diretorios removidos: {result.get('removed_dirs', 0)}",
                    f"Espaco liberado: {result.get('freed_bytes', 0)} bytes",
                    "Relatorios, logs, projetos, sessoes e dados persistentes foram preservados.",
                ],
            )
        )

    def panel(self, title: str, lines: list[str] | str) -> str:
        content = [lines] if isinstance(lines, str) else lines
        inner_width = self.width - 4
        top = "+" + "-" * (self.width - 2) + "+"
        title_line = f"| {colorize(title, 'bold')[:inner_width].ljust(inner_width)} |"
        rendered = [top, title_line, top]
        for line in content:
            wrapped = textwrap.wrap(str(line), width=inner_width) or [""]
            for item in wrapped:
                rendered.append(f"| {item.ljust(inner_width)} |")
        rendered.append(top)
        return "\n".join(rendered)

    def progress_bar(self, current: int, total: int, width: int = 28) -> str:
        if total <= 0:
            total = 1
        ratio = max(0.0, min(float(current) / float(total), 1.0))
        filled = int(round(width * ratio))
        bar = "#" * filled + "-" * (width - filled)
        return f"[{bar}] {int(ratio * 100)}%"

    def print_info(self, message: str) -> None:
        print(info(message))
