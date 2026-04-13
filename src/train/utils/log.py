import time

from datetime import datetime

def loginfo(message,status="info"):
	"""
	Logs the message to the console with a timestamp.
	:param message: 提示信息内容
    :param status: 状态类型 info/success/warn/error/start/end
	"""
	now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	
	status_map = {
		"info": "[INFO]",
		"success": "[SUCCESS]",
		"warn": "[WARN]",
		"error": "[ERROR]",
		"start": "[START]",
		"end": "[END]"
	}
	
	tag = status_map.get(status, "[INFO]")
	print(f"{now} {tag} {message}")