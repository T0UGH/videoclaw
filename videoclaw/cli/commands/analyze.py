"""analyze 命令"""
from __future__ import annotations

import json
import click
from pathlib import Path
from typing import Optional

from videoclaw.state import StateManager


DEFAULT_PROJECTS_DIR = Path.home() / "videoclaw-projects"


def parse_script(script_text: str) -> dict:
    """解析脚本，提取角色、场景、道具和故事板帧"""
    # 简单的脚本解析 - 后续可以接入 LLM
    # 这里先用占位数据

    # 检测关键字来确定角色
    characters = []
    scenes = []
    props = []

    # 简单的关键词匹配
    if "宇航员" in script_text or "航天员" in script_text:
        characters.append({
            "name": "宇航员",
            "description": "身穿白色宇航服的宇航员，头戴头盔",
            "actions": ["行走", "观察", "惊讶"]
        })

    if "变形金刚" in script_text or "机器人" in script_text:
        characters.append({
            "name": "变形金刚",
            "description": "高科技机器人，能变形为车辆形态",
            "actions": ["变形", "站立", "互动"]
        })

    if "火星" in script_text:
        scenes.append({
            "name": "火星表面",
            "description": "红色的火星荒原，有岩石和沙丘",
            "time": "白天"
        })

    if "基地" in script_text or "遗迹" in script_text:
        props.append({
            "name": "外星遗迹",
            "description": "古老的外星建筑遗迹"
        })

    # 如果没有识别到任何角色，添加默认
    if not characters:
        characters.append({
            "name": "主角",
            "description": "故事主角",
            "actions": ["行走", "观察"]
        })

    if not scenes:
        scenes.append({
            "name": "场景",
            "description": "故事发生地点",
            "time": "白天"
        })

    # 生成故事板帧
    frames = []
    if len(characters) >= 2:
        # 有两个角色时的故事板
        frames = [
            {
                "frame_id": 1,
                "description": f"{characters[0]['name']}独自在{scenes[0]['name']}探索",
                "action": "探索",
                "camera": "远景"
            },
            {
                "frame_id": 2,
                "description": f"{characters[0]['name']}发现了{characters[1]['name']}",
                "action": "发现",
                "camera": "中景"
            },
            {
                "frame_id": 3,
                "description": f"{characters[0]['name']}和{characters[1]['name']}相互警惕对视",
                "action": "对视",
                "camera": "特写"
            },
            {
                "frame_id": 4,
                "description": f"{characters[0]['name']}慢慢走近{characters[1]['name']}",
                "action": "接近",
                "camera": "中景"
            },
            {
                "frame_id": 5,
                "description": f"{characters[1]['name']}变形展示能力",
                "action": "变形",
                "camera": "全景"
            },
            {
                "frame_id": 6,
                "description": f"{characters[0]['name']}和{characters[1]['name']}建立友谊",
                "action": "友好",
                "camera": "中景"
            }
        ]
    else:
        frames = [
            {
                "frame_id": 1,
                "description": f"{characters[0]['name']}在{scenes[0]['name']}",
                "action": "站立",
                "camera": "全景"
            },
            {
                "frame_id": 2,
                "description": f"{characters[0]['name']}观察周围环境",
                "action": "观察",
                "camera": "中景"
            },
            {
                "frame_id": 3,
                "description": f"{characters[0]['name']}发现有趣的事物",
                "action": "发现",
                "camera": "特写"
            }
        ]

    return {
        "script": script_text,
        "characters": characters,
        "scenes": scenes,
        "props": props,
        "frames": frames
    }


@click.command()
@click.argument("script_text", required=False)
@click.option("--script", "-s", "script_option", help="脚本内容")
@click.option("--project", "-p", required=True, help="项目名称")
def analyze(script_text: Optional[str], script_option: Optional[str], project: str):
    """分析脚本，提取角色、场景、帧"""
    # 确定脚本内容
    script = script_text or script_option
    if not script:
        click.echo("错误: 请提供脚本内容", err=True)
        click.echo("用法: videoclaw analyze <脚本内容> --project <项目名>")
        click.echo("   或: videoclaw analyze --script '<脚本内容>' --project <项目名>")
        return

    project_path = DEFAULT_PROJECTS_DIR / project

    if not project_path.exists():
        click.echo(f"错误: 项目 {project} 不存在", err=True)
        return

    state = StateManager(project_path)
    state.set_status("analyzing")
    state.update_step("analyze", "in_progress")

    click.echo(f"分析脚本: {script}")

    # 解析脚本
    result = parse_script(script)
    click.echo(f"识别到 {len(result['characters'])} 个角色")
    click.echo(f"识别到 {len(result['scenes'])} 个场景")
    click.echo(f"生成 {len(result['frames'])} 个故事板帧")

    # 保存分析结果
    state.update_step("analyze", "completed", result)
    state.set_status("analyzed")

    click.echo("脚本分析完成!")
