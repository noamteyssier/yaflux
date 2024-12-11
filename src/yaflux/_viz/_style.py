from dataclasses import dataclass


@dataclass
class NodeStyle:
    shape: str
    style: str
    prefix: str = ""


class GraphConfig:
    def __init__(
        self,
        step_color: str = "#008000",
        result_color: str = "#000080",
        flag_color: str = "#800000",
        fontname: str = "Helvetica",
        fontsize: int = 11,
        rankdir: str = "LR",
    ):
        self.fontname = fontname
        self.fontsize = fontsize
        self.rankdir = rankdir
        self.step_colors = self._build_color_set(step_color)
        self.result_colors = self._build_color_set(result_color)
        self.flag_colors = self._build_color_set(flag_color)

        # Define node styles
        self.node_styles = {
            "step": NodeStyle(shape="box", style="filled"),
            "result": NodeStyle(shape="box", style="filled,rounded"),
            "flag": NodeStyle(shape="cds", style="filled", prefix="flag"),
        }

    @staticmethod
    def _build_color_set(hex_color: str) -> dict[str, str]:
        return {
            "complete_line": f"{hex_color}FF",
            "complete_fill": f"{hex_color}80",
            "incomplete_line": f"{hex_color}10",
            "incomplete_fill": f"{hex_color}10",
        }
