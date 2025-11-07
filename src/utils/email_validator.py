"""邮箱格式验证工具"""

def validate_polyu_email(email: str) -> tuple[bool, str]:
    """
    验证邮箱格式是否符合PolyU要求（必须以@connect.polyu.hk结尾）
    
    Args:
        email: 待验证的邮箱地址
        
    Returns:
        (is_valid, error_message): 如果有效返回(True, '')，否则返回(False, 错误信息)
    """
    if not email or not isinstance(email, str):
        return False, '邮箱不能为空'
    
    email = email.strip().lower()
    
    # 检查邮箱格式
    if '@' not in email:
        return False, '邮箱格式不正确'
    
    # 检查是否以@connect.polyu.hk结尾
    required_suffix = '@connect.polyu.hk'
    if not email.endswith(required_suffix):
        return False, f'邮箱必须以{required_suffix}结尾'
    
    # 检查@符号前是否有内容
    local_part = email.split('@')[0]
    if not local_part:
        return False, '邮箱@符号前必须有内容'
    
    return True, ''

