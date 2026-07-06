"""Presentation helpers for the terminal interface."""

from __future__ import annotations

import json
import os
import textwrap
from typing import Any

from cli.messages import colorize, info
from cli.tables import format_table
from core.constants import APP_NAME, APP_VERSION
from services.scanner_service import ETHICAL_NOTICE

try:  # pragma: no cover - exercised when Rich is installed in an interactive terminal.
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
except ImportError:  # pragma: no cover
    Console = None
    Panel = None
    Text = None


class TerminalRenderer:
    """Renders consistent CLI output."""

    def __init__(self, width: int = 88) -> None:
        self.width = max(60, width)
        self.rich_console = Console() if Console and os.isatty(1) else None

    def banner(self) -> str:
        return self.panel(
            "SENTINELSCAN ELITE CLI",
            [
                *self.logo().splitlines(),
                "SentinelScan Elite CLI",
                f"Versao: {APP_VERSION}",
                "Cyber Defense & Vulnerability Intelligence",
                "Feito por Joao Guilherme",
                "Author hex: 4a 6f 61 6f 20 47 75 69 6c 68 65 72 6d 65",
                "Use 'sentinelscan help' para ver navegacao, atalhos e comandos.",
            ],
        )

    def print_banner(self) -> None:
        print(self.banner())

    def logo(self) -> str:
        return (
            "  ____  _____ _   _ _____ ___ _   _ _____ _      ____   ____    _    _   _\n"
            " / ___|| ____| \\ | |_   _|_ _| \\ | | ____| |    / ___| / ___|  / \\  | \\ | |\n"
            " \\___ \\|  _| |  \\| | | |  | ||  \\| |  _| | |    \\___ \\| |     / _ \\ |  \\| |\n"
            "  ___) | |___| |\\  | | |  | || |\\  | |___| |___  ___) | |___ / ___ \\| |\\  |\n"
            " |____/|_____|_| \\_| |_| |___|_| \\_|_____|_____|____/ \\____/_/   \\_\\_| \\_|"
        )

    def print_json(self, payload: Any) -> None:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))

    def print_table(self, rows: list[dict[str, Any]], columns: list[str]) -> None:
        print(format_table(rows, columns))

    def print_status(self, status: dict[str, Any]) -> None:
        self.print_dashboard(status)

    def print_dashboard(self, status: dict[str, Any]) -> None:
        health = status.get("health", {})
        self.print_banner()
        self.print_panel(
            "Ethical Notice",
            [
                ETHICAL_NOTICE,
            ],
            style="red",
        )
        self.print_panel(
            "Status do sistema",
            [
                f"Root: {status['root_path']}",
                f"Modules: {status['modules']} | Plugins: {status['plugins']} | Projects: {status['projects']}",
                f"Inicializacao: {self.progress_bar(1, 1)}",
            ],
            style="cyan",
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
                    {"metric": "Usuario", "value": health.get("user")},
                    {"metric": "Sistema", "value": health.get("os")},
                    {"metric": "IP local", "value": health.get("local_ip")},
                    {"metric": "CPU", "value": health.get("cpu_count")},
                    {"metric": "RAM MB", "value": health.get("memory_total_mb")},
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
                    "Usar Nmap: python main.py scan nmap <alvo> --authorize.",
                    "Usar Nuclei: python main.py scan nuclei <alvo> --authorize.",
                    "Listar modulos: use 'modules list' ou a opcao 13 no menu interativo.",
                    "Relatorios ficam em reports/<projeto>/<ano>/<mes>/<dia>/<sessao>/<ferramenta>.",
                    "Formatos: markdown, txt, json, csv e html.",
                    "Sair corretamente: escolha 0 no menu interativo para ver o resumo final.",
                ],
            )
        )
        commands = [
            {"command": "python main.py status", "purpose": "Ver saude do sistema"},
            {"command": "python main.py interactive", "purpose": "Abrir menu guiado"},
            {"command": "python main.py modules list", "purpose": "Listar modulos"},
            {"command": "python main.py scan nmap 127.0.0.1 --authorize", "purpose": "Nmap autorizado"},
            {"command": "python main.py scan nuclei http://localhost --authorize", "purpose": "Nuclei autorizado"},
            {"command": "python main.py reports list", "purpose": "Listar relatorios"},
            {"command": "python main.py maintenance clean-temp", "purpose": "Simular limpeza segura"},
            {"command": "python main.py maintenance clean-temp --yes", "purpose": "Limpar cache descartavel"},
        ]
        self.print_table(commands, ["command", "purpose"])

    def print_modules(self, modules: list[dict[str, Any]]) -> None:
        if not modules:
            self.print_panel(
                "Modulos",
                ["Nenhum modulo carregado. Verifique a pasta modules/ e os logs tecnicos."],
                style="yellow",
            )
            return
        self.print_panel(
            "Modulos carregados",
            [f"Total: {len(modules)}", "Nmap e Nuclei aparecem aqui quando descobertos."],
            style="green",
        )
        self.print_table(modules, ["id", "name", "category", "version", "state", "description"])

    def print_history(self, records: list[dict[str, Any]]) -> None:
        rows = [
            {
                "timestamp": record.get("timestamp"),
                "function": record.get("function"),
                "result": record.get("result"),
                "error": record.get("error") or "",
            }
            for record in records
        ]
        self.print_panel("Historico", [f"Eventos recentes: {len(rows)}"], style="cyan")
        self.print_table(rows, ["timestamp", "function", "result", "error"])

    def print_scan_result(self, result: dict[str, Any]) -> None:
        data = result.get("data", {})
        reports = data.get("reports", [])
        self.print_panel(
            f"Resultado: {result.get('module_id')}",
            [
                f"Status: {result.get('status')}",
                f"Sucesso: {result.get('success')}",
                f"Ferramenta: {data.get('tool')}",
                f"Perfil: {data.get('profile')}",
                f"Relatorios: {len(reports)}",
            ],
            style="green" if result.get("success") else "red",
        )
        if reports:
            self.print_table(reports, ["format", "path", "generated_at"])

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

    def print_panel(self, title: str, lines: list[str] | str, style: str = "cyan") -> None:
        if self.rich_console and Panel and Text:
            content = "\n".join(lines if isinstance(lines, list) else [lines])
            self.rich_console.print(Panel(Text(content), title=title, border_style=style))
            return
        print(self.panel(title, lines))

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
