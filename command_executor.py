import subprocess
import shlex

class CommandExecutor:
    def __init__(self, default_timeout=5):
        """
        初始化命令执行器

        :param default_timeout: 默认超时时间（秒）
        """
        self.default_timeout = default_timeout

    def execute(self, command_str, timeout=None):
        """
        执行用户命令并返回标准化结果

        :param command_str: 输入的命令字符串
        :param timeout: 本次执行的超时时间（秒），None表示使用默认值
        :return: 包含执行结果的字典
        """
        # 设置超时时间（优先使用参数值）
        actual_timeout = timeout if timeout is not None else self.default_timeout

        try:
            # 安全分割命令参数（自动处理引号和转义）
            command_parts = self._split_command(command_str)
            if not command_parts:
                return self._format_result(
                    error="Empty command",
                    return_code=-1
                )

            # 执行核心逻辑
            process_result = subprocess.run(
                command_parts,
                stdin=subprocess.PIPE,        # 禁止交互输入
                stdout=subprocess.PIPE,       # 捕获标准输出
                stderr=subprocess.PIPE,       # 捕获错误输出
                timeout=actual_timeout,      # 超时控制
                text=True                    # 返回字符串而非字节
            )

            return self._format_result(
                stdout=process_result.stdout,
                stderr=process_result.stderr,
                return_code=process_result.returncode
            )

        except subprocess.TimeoutExpired:
            return self._format_result(
                error=f"Command timed out after {actual_timeout}s",
                return_code=-1
            )
        except Exception as e:
            return self._format_result(
                error=f"Execution failed: {str(e)}",
                return_code=-1
            )

    def _split_command(self, command_str):
        """安全分割命令字符串"""
        try:
            return shlex.split(command_str)
        except ValueError as e:
            raise RuntimeError(f"Invalid command format: {str(e)}")

    def _format_result(self, stdout="", stderr="", error="", return_code=0):
        """统一结果格式"""
        return {
            "success": return_code == 0,
            "stdout": stdout.strip(),
            "stderr": stderr.strip(),
            "error": error,
            "return_code": return_code
        }


# 使用示例
if __name__ == "__main__":
    executor = CommandExecutor(default_timeout=3)

    test_commands = [
        "ls -l",                # 正常命令
        "top",                  # 交互式命令
        "sleep 100",              # 触发超时
        "invalid_command",      # 不存在命令
    ]

    for cmd in test_commands:
        print(f"Executing: {cmd}")
        result = executor.execute(cmd)
        print(f"Success: {result['success']}")
        print(f"Return Code: {result['return_code']}")
        print(f"Stdout:\n{result['stdout']}")
        print(f"Stderr:\n{result['stderr']}")
        print(f"Error: {result['error']}")
        print("=" * 50)