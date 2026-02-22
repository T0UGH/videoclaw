"""Publish 命令"""
from __future__ import annotations

import asyncio
import click
from pathlib import Path

from videoclaw.publisher.factory import get_publisher


@click.group()
def publish():
    """社交媒体发布命令"""
    pass


@publish.command()
@click.argument("platform")
@click.option("--account", default="default", help="账号名称")
def login(platform: str, account: str):
    """登录社交媒体账号

    示例:
        videoclaw publish login douyin
        videoclaw publish login kuaishou --account my_account
    """
    if platform not in ["douyin", "kuaishou"]:
        click.echo(f"不支持的平台: {platform}", err=True)
        return

    click.echo(f"正在打开 {platform} 登录页面，请扫码登录...")
    click.echo("登录成功后会自动保存 cookie")

    publisher = get_publisher(platform)

    async def run():
        success = await publisher.login(account)
        if success:
            click.echo(f"登录成功！Cookie 已保存到: {publisher.get_cookie_path(account)}")
        else:
            click.echo("登录失败", err=True)

    asyncio.run(run())


@publish.command()
@click.argument("platform")
@click.option("--video", "-v", required=True, help="视频文件路径")
@click.option("--title", "-t", required=True, help="视频标题")
@click.option("--tags", help="话题标签，逗号分隔")
@click.option("--cover", help="封面图片路径")
@click.option("--account", default="default", help="账号名称")
def upload(
    platform: str,
    video: str,
    title: str,
    tags: str,
    cover: str,
    account: str,
):
    """发布视频到社交媒体

    示例:
        videoclaw publish upload douyin -v video.mp4 -t "我的视频" --tags "tag1,tag2"
    """
    if platform not in ["douyin", "kuaishou"]:
        click.echo(f"不支持的平台: {platform}", err=True)
        return

    video_path = Path(video)
    if not video_path.exists():
        click.echo(f"视频文件不存在: {video}", err=True)
        return

    cover_path = Path(cover) if cover else None
    if cover_path and not cover_path.exists():
        click.echo(f"封面文件不存在: {cover}", err=True)
        return

    tags_list = [t.strip() for t in tags.split(",")] if tags else []

    publisher = get_publisher(platform)

    click.echo(f"正在发布视频到 {platform}...")

    async def run():
        result = await publisher.publish(
            video_path=video_path,
            title=title,
            tags=tags_list,
            cover_path=cover_path,
            account=account,
        )

        if result.success:
            click.echo(f"发布成功！")
            if result.video_url:
                click.echo(f"视频链接: {result.video_url}")
        else:
            click.echo(f"发布失败: {result.error}", err=True)

    asyncio.run(run())


@publish.command()
def status():
    """查看已登录账号状态"""
    click.echo("已登录的账号:")
    for platform in ["douyin", "kuaishou"]:
        cookie_dir = Path.home() / ".videoclaw" / "cookies" / platform
        if cookie_dir.exists():
            for cookie_file in cookie_dir.glob("*.json"):
                click.echo(f"  {platform}: {cookie_file.stem}")
