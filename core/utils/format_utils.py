import json
import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class FormattedOutput:
    text: str
    color: Optional[str] = None
    style: Optional[str] = None


class FormatUtils:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"

    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"

    @staticmethod
    def colorize(text: str, color: str) -> str:
        return f"{color}{text}{FormatUtils.RESET}"

    @staticmethod
    def bold(text: str) -> str:
        return f"{FormatUtils.BOLD}{text}{FormatUtils.RESET}"

    @staticmethod
    def dim(text: str) -> str:
        return f"{FormatUtils.DIM}{text}{FormatUtils.RESET}"

    @staticmethod
    def success(text: str) -> str:
        return FormatUtils.colorize(f"✓ {text}", FormatUtils.GREEN)

    @staticmethod
    def error(text: str) -> str:
        return FormatUtils.colorize(f"✗ {text}", FormatUtils.RED)

    @staticmethod
    def warning(text: str) -> str:
        return FormatUtils.colorize(f"⚠ {text}", FormatUtils.YELLOW)

    @staticmethod
    def info(text: str) -> str:
        return FormatUtils.colorize(f"ℹ {text}", FormatUtils.CYAN)

    @staticmethod
    def header(text: str) -> str:
        return FormatUtils.colorize(FormatUtils.bold(text), FormatUtils.CYAN)

    @staticmethod
    def subheader(text: str) -> str:
        return FormatUtils.colorize(text, FormatUtils.BLUE)

    @staticmethod
    def highlight(text: str) -> str:
        return FormatUtils.colorize(text, FormatUtils.YELLOW)

    @staticmethod
    def prompt(text: str) -> str:
        return FormatUtils.colorize(text, FormatUtils.GREEN)

    @staticmethod
    def timestamp() -> str:
        return datetime.datetime.now().strftime("%H:%M:%S")

    @staticmethod
    def format_table(
        headers: List[str],
        rows: List[List[str]],
        col_widths: Optional[List[int]] = None,
    ) -> str:
        if not col_widths:
            col_widths = [
                max(len(str(row[i])) for row in [headers] + rows)
                for i in range(len(headers))
            ]

        separator = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"
        header_row = (
            "|"
            + "|".join(f" {headers[i]:<{col_widths[i]}} " for i in range(len(headers)))
            + "|"
        )

        lines = [separator, header_row, separator]
        for row in rows:
            row_str = (
                "|"
                + "|".join(f" {str(row[i]):<{col_widths[i]}} " for i in range(len(row)))
                + "|"
            )
            lines.append(row_str)
        lines.append(separator)

        return "\n".join(lines)

    @staticmethod
    def format_list(items: List[str], numbered: bool = True) -> str:
        if numbered:
            return "\n".join(f"  {i + 1}. {item}" for i, item in enumerate(items))
        return "\n".join(f"  • {item}" for item in items)

    @staticmethod
    def truncate(text: str, max_length: int, ellipsis: str = "...") -> str:
        if len(text) <= max_length:
            return text
        return text[: max_length - len(ellipsis)] + ellipsis

    @staticmethod
    def pad_center(text: str, width: int) -> str:
        padding = (width - len(text)) // 2
        return " " * padding + text + " " * (width - len(text) - padding)

    @staticmethod
    def box_text(text: str, width: int, title: Optional[str] = None) -> str:
        lines = text.split("\n")
        border = "═" * (width - 2)

        result = f"╔{border}╗\n"
        if title:
            title_padding = (width - len(title) - 2) // 2
            result += f"║ {' ' * title_padding}{title}{' ' * (width - len(title) - title_padding - 2)}║\n"
            result += f"╟{border}╢\n"

        for line in lines:
            if len(line) < width - 2:
                line += " " * (width - 2 - len(line))
            result += f"║ {line[: width - 2]} ║\n"

        result += f"╚{border}╝"
        return result

    @staticmethod
    def json_dumps(data: Any, indent: int = 2) -> str:
        return json.dumps(data, indent=indent, sort_keys=True)

    @staticmethod
    def json_loads(text: str) -> Any:
        return json.loads(text)

    @staticmethod
    def format_bytes(size: int) -> str:
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} PB"

    @staticmethod
    def format_duration(seconds: float) -> str:
        if seconds < 1:
            return f"{seconds * 1000:.0f}ms"
        elif seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}h {minutes}m"

    @staticmethod
    def format_hex(data: bytes, width: int = 16) -> str:
        lines = []
        for i in range(0, len(data), width):
            chunk = data[i : i + width]
            hex_part = " ".join(f"{b:02x}" for b in chunk)
            ascii_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
            lines.append(f"{i:08x}  {hex_part:<{width * 3}}  {ascii_part}")
        return "\n".join(lines)


class TableFormatter:
    def __init__(self, columns: List[Dict[str, Any]]):
        self.columns = columns
        self.rows = []

    def add_row(self, values: List[Any]):
        self.rows.append(values)

    def render(self) -> str:
        col_widths = []
        for i, col in enumerate(self.columns):
            width = col.get("width", 0)
            if width == 0:
                width = len(col.get("name", ""))
                for row in self.rows:
                    width = max(width, len(str(row[i])))
            col_widths.append(width)

        separator = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"

        lines = [separator]

        header = (
            "|"
            + "|".join(
                f" {self.columns[i]['name']:<{col_widths[i]}} "
                for i in range(len(self.columns))
            )
            + "|"
        )
        lines.append(header)
        lines.append(separator)

        for row in self.rows:
            row_str = (
                "|"
                + "|".join(f" {str(row[i]):<{col_widths[i]}} " for i in range(len(row)))
                + "|"
            )
            lines.append(row_str)

        lines.append(separator)
        return "\n".join(lines)
