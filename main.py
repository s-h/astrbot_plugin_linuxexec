from astrbot.api.event import filter, AstrMessageEvent

from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from .CommandExecutor import CommandExecutor

@register("linuxexec", "s-h", "执行linux非交互式系统命令", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.executor = CommandExecutor(default_timeout=5)
    
    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("linuxexec")
    async def linuxcmd(self, event: AstrMessageEvent):
        message_str = event.message_str # 用户发的纯文本消息字符串
        args = message_str.replace("linuxexec ", "")
        if not args:
            yield event.plain_result("请输入要执行的命令")
            return
        result = self.executor.execute(args)
        yield event.plain_result(f"""Success: {result['success']}
Return Code: {result['return_code']}
Stdout: {result['stdout']}
Stderr: {result['stderr']}
Error: {result['error']}""")

    async def terminate(self):
        '''可选择实现 terminate 函数，当插件被卸载/停用时会调用。'''
