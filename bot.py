import discord
from discord.ext import commands
import subprocess
import os
import tempfile
import asyncio

# Cấu hình bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} đã online!')

@bot.command(name='deobfuscate', aliases=['deob', 'd'])
async def deobfuscate(ctx):
    """Deobfuscate file Lua - Gửi kèm file .lua"""
    
    # Kiểm tra có file đính kèm không
    if not ctx.message.attachments:
        await ctx.send("❌ Vui lòng gửi file .lua kèm theo lệnh!")
        return
    
    attachment = ctx.message.attachments[0]
    
    # Kiểm tra file extension
    if not attachment.filename.endswith('.lua'):
        await ctx.send("❌ Chỉ chấp nhận file .lua!")
        return
    
    # Kiểm tra kích thước file (giới hạn 5MB)
    if attachment.size > 5 * 1024 * 1024:
        await ctx.send("❌ File quá lớn! Giới hạn 5MB")
        return
    
    await ctx.send("⏳ Đang xử lý file...")
    
    try:
        # Tạo thư mục tạm
        with tempfile.TemporaryDirectory() as tmpdir:
            # Đường dẫn file
            input_path = os.path.join(tmpdir, attachment.filename)
            output_path = os.path.join(tmpdir, f"deobfuscated_{attachment.filename}")
            
            # Tải file xuống
            await attachment.save(input_path)
            
            # Chạy deobfuscator
            cmd = [
                'python3', 
                'src/deobfuscator_console.py',
                input_path,
                output_path,
                'decompile'
            ]
            
            # Timeout 60s
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=60.0
                )
            except asyncio.TimeoutError:
                process.kill()
                await ctx.send("❌ Xử lý quá lâu! File có thể quá phức tạp.")
                return
            
            # Kiểm tra kết quả
            if process.returncode != 0:
                error_msg = stderr.decode('utf-8', errors='ignore')
                await ctx.send(f"❌ Lỗi khi deobfuscate:\n```{error_msg[:500]}```")
                return
            
            # Kiểm tra file output
            if not os.path.exists(output_path):
                await ctx.send("❌ Không tạo được file output!")
                return
            
            # Gửi file kết quả
            file_size = os.path.getsize(output_path)
            
            if file_size > 8 * 1024 * 1024:  # Discord limit 8MB
                await ctx.send("❌ File kết quả quá lớn (>8MB). Không thể gửi!")
                return
            
            await ctx.send(
                "✅ Deobfuscate thành công!",
                file=discord.File(output_path)
            )
            
    except Exception as e:
        await ctx.send(f"❌ Lỗi: {str(e)}")

@bot.command(name='help', aliases=['h'])
async def help_command(ctx):
    """Hướng dẫn sử dụng bot"""
    embed = discord.Embed(
        title="🤖 WeAreDevs Deobfuscator Bot",
        description="Bot deobfuscate Lua scripts",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="📝 Cách sử dụng",
        value="Gửi file .lua kèm lệnh `!deobfuscate`",
        inline=False
    )
    
    embed.add_field(
        name="🔧 Lệnh",
        value="`!deobfuscate` hoặc `!deob` hoặc `!d`",
        inline=False
    )
    
    embed.add_field(
        name="⚠️ Giới hạn",
        value="• File tối đa 5MB\n• Timeout 60 giây",
        inline=False
    )
    
    await ctx.send(embed=embed)

# Chạy bot
if __name__ == '__main__':
    TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    if not TOKEN:
        print("❌ Thiếu DISCORD_BOT_TOKEN trong environment variables!")
        exit(1)
    
    bot.run(TOKEN)
