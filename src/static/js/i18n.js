// 多语言支持系统
let currentLanguage = 'zh'; // 默认中文

// 语言切换功能
function toggleLanguage() {
    currentLanguage = currentLanguage === 'zh' ? 'en' : 'zh';
    updateLanguage();
    updateLanguageToggleButton();
}

function updateLanguage() {
    const elements = document.querySelectorAll('[data-zh][data-en]');
    elements.forEach(element => {
        element.textContent = element.getAttribute(`data-${currentLanguage}`);
    });
    
    // 更新placeholder
    const inputs = document.querySelectorAll('[data-zh-placeholder][data-en-placeholder]');
    inputs.forEach(input => {
        input.placeholder = input.getAttribute(`data-${currentLanguage}-placeholder`);
    });
    
    // 更新页面标题
    const titleElement = document.querySelector('title');
    if (titleElement) {
        document.title = titleElement.getAttribute(`data-${currentLanguage}`) || document.title;
    }
    
    // 更新HTML lang属性
    document.documentElement.lang = currentLanguage === 'zh' ? 'zh-CN' : 'en';
}

function updateLanguageToggleButton() {
    const button = document.getElementById('languageToggle');
    if (button) {
        button.textContent = currentLanguage === 'zh' ? '🌐 EN' : '🌐 中文';
    }
}

// 多语言消息
const messages = {
    'zh': {
        'login_success': '登录成功！',
        'login_failed': '登录失败，请检查用户名和密码',
        'register_success': '注册成功！',
        'register_failed': '注册失败，请重试',
        'network_error': '网络错误，请重试',
        'username_required': '请输入用户名',
        'password_required': '请输入密码',
        'email_required': '请输入邮箱',
        'fullname_required': '请输入姓名',
        'studentid_required': '请输入学生ID',
        'loading': '加载中...',
        'no_data': '暂无数据',
        'success': '成功',
        'error': '错误',
        'warning': '警告',
        'info': '信息',
        'confirm': '确认',
        'cancel': '取消',
        'save': '保存',
        'edit': '编辑',
        'delete': '删除',
        'create': '创建',
        'update': '更新',
        'submit': '提交',
        'back': '返回',
        'next': '下一步',
        'previous': '上一步',
        'close': '关闭',
        'open': '打开',
        'search': '搜索',
        'filter': '筛选',
        'sort': '排序',
        'refresh': '刷新',
        'export': '导出',
        'import': '导入',
        'download': '下载',
        'upload': '上传',
        'view': '查看',
        'details': '详情',
        'settings': '设置',
        'profile': '个人资料',
        'logout': '登出',
        'login': '登录',
        'register': '注册',
        'teacher': '教师',
        'student': '学生',
        'admin': '管理员',
        'course': '课程',
        'activity': '活动',
        'response': '响应',
        'analytics': '分析',
        'dashboard': '仪表板',
        'leaderboard': '排行榜',
        'reports': '报告',
        'statistics': '统计',
        'progress': '进度',
        'score': '分数',
        'feedback': '反馈',
        'poll': '投票',
        'quiz': '测验',
        'word_cloud': '词云',
        'short_answer': '简答题',
        'mini_game': '迷你游戏',
        'active': '进行中',
        'completed': '已完成',
        'draft': '草稿',
        'archived': '已归档'
    },
    'en': {
        'login_success': 'Login successful!',
        'login_failed': 'Login failed, please check username and password',
        'register_success': 'Registration successful!',
        'register_failed': 'Registration failed, please try again',
        'network_error': 'Network error, please try again',
        'username_required': 'Please enter username',
        'password_required': 'Please enter password',
        'email_required': 'Please enter email',
        'fullname_required': 'Please enter full name',
        'studentid_required': 'Please enter student ID',
        'loading': 'Loading...',
        'no_data': 'No data available',
        'success': 'Success',
        'error': 'Error',
        'warning': 'Warning',
        'info': 'Info',
        'confirm': 'Confirm',
        'cancel': 'Cancel',
        'save': 'Save',
        'edit': 'Edit',
        'delete': 'Delete',
        'create': 'Create',
        'update': 'Update',
        'submit': 'Submit',
        'back': 'Back',
        'next': 'Next',
        'previous': 'Previous',
        'close': 'Close',
        'open': 'Open',
        'search': 'Search',
        'filter': 'Filter',
        'sort': 'Sort',
        'refresh': 'Refresh',
        'export': 'Export',
        'import': 'Import',
        'download': 'Download',
        'upload': 'Upload',
        'view': 'View',
        'details': 'Details',
        'settings': 'Settings',
        'profile': 'Profile',
        'logout': 'Logout',
        'login': 'Login',
        'register': 'Register',
        'teacher': 'Teacher',
        'student': 'Student',
        'admin': 'Administrator',
        'course': 'Course',
        'activity': 'Activity',
        'response': 'Response',
        'analytics': 'Analytics',
        'dashboard': 'Dashboard',
        'leaderboard': 'Leaderboard',
        'reports': 'Reports',
        'statistics': 'Statistics',
        'progress': 'Progress',
        'score': 'Score',
        'feedback': 'Feedback',
        'poll': 'Poll',
        'quiz': 'Quiz',
        'word_cloud': 'Word Cloud',
        'short_answer': 'Short Answer',
        'mini_game': 'Mini Game',
        'active': 'Active',
        'completed': 'Completed',
        'draft': 'Draft',
        'archived': 'Archived'
    }
};

// 获取多语言文本
function getText(key) {
    return messages[currentLanguage][key] || key;
}

// 显示多语言消息
function showMessage(key, type = 'success') {
    const messageDiv = document.createElement('div');
    messageDiv.className = type;
    messageDiv.textContent = getText(key);
    
    const container = document.querySelector('.container') || document.body;
    container.insertBefore(messageDiv, container.firstChild);
    
    setTimeout(() => {
        messageDiv.remove();
    }, 3000);
}

// 页面加载时初始化语言
document.addEventListener('DOMContentLoaded', function() {
    updateLanguage();
    updateLanguageToggleButton();
});
