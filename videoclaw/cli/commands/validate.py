"""validate 命令 - 验证 JSON 格式"""
import json
import click
from pathlib import Path


@click.command()
@click.option("--project", "-p", required=True, help="项目名称")
@click.option("--strict", is_flag=True, help="严格模式：检查必需字段")
def validate(project: str, strict: bool):
    """验证项目 state.json 格式"""
    config_dir = Path.home() / "videoclaw-projects" / project / ".videoclaw"
    state_file = config_dir / "state.json"

    if not state_file.exists():
        click.echo(f"错误: 项目 {project} 不存在", err=True)
        click.echo(f"未找到: {state_file}", err=True)
        raise click.Abort()

    try:
        with open(state_file) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        click.echo(f"错误: JSON 格式无效", err=True)
        click.echo(str(e), err=True)
        raise click.Abort()

    # 基础验证
    if "steps" not in data:
        click.echo("错误: 缺少 steps 字段", err=True)
        raise click.Abort()

    # 检查 analyze 步骤
    analyze_step = data.get("steps", {}).get("analyze", {})
    analyze_output = analyze_step.get("output", {})

    if not analyze_output:
        click.echo("警告: analyze 步骤尚未完成或无输出", err=True)

    if "script" not in analyze_output:
        click.echo("警告: 缺少 script 字段", err=True)

    # 严格模式验证
    if strict:
        required_fields = ["script", "characters", "scenes", "frames"]
        for field in required_fields:
            if field not in analyze_output:
                click.echo(f"错误: 严格模式下必须包含 {field} 字段", err=True)
                raise click.Abort()

    click.echo(f"✓ 项目 {project} 的 state.json 格式有效")

    # 显示关键信息
    if analyze_output:
        if "script" in analyze_output:
            script = analyze_output["script"]
            click.echo(f"脚本: {script[:50]}...")
        if "characters" in analyze_output:
            click.echo(f"角色数: {len(analyze_output.get('characters', []))}")
        if "scenes" in analyze_output:
            click.echo(f"场景数: {len(analyze_output.get('scenes', []))}")
        if "frames" in analyze_output:
            click.echo(f"帧数: {len(analyze_output.get('frames', []))}")
