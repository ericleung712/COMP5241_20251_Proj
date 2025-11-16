import openai
import json
from typing import Dict, List, Any
import os

class AIService:
    """AI服务类 - 处理各种AI功能"""
    
    def __init__(self):
        # 设置DeepSeek API密钥和端点
        self.api_key = os.getenv('DEEPSEEK_API_KEY', 'sk-ca7c5b2dbdb84e5b8c2d7281ebc355e2')
        # 配置OpenAI客户端以使用DeepSeek API
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com/v1"
        )
        self.model = "deepseek-chat"
    
    def generate_activity(self, activity_type: str, course_content: str, 
                         web_resources: str = "", additional_prompt: str = "", time_limit: int = None) -> Dict[str, Any]:
        """根据课程内容生成学习活动"""
        
        time_limit_str = f"\nTime Limit: {time_limit} minutes" if time_limit else ""
        
        prompts = {
            'poll': f"""
            基于以下课程内容，生成一个投票活动：
            课程内容：{course_content}
            网络资源：{web_resources}
            额外要求：{additional_prompt}{time_limit_str}
            
            请生成包含以下内容的JSON格式：
            {{
                "title": "活动标题",
                "description": "活动描述",
                "question": "投票问题",
                "options": ["选项1", "选项2", "选项3", "选项4"],
                "correct_answer": "正确答案（如果有）",
                "explanation": "解释说明"
            }}
            """,
            
            'quiz': f"""
            基于以下课程内容，生成一个测验活动：
            课程内容：{course_content}
            网络资源：{web_resources}
            额外要求：{additional_prompt}{time_limit_str}
            
            请生成包含以下内容的JSON格式：
            {{
                "title": "测验标题",
                "description": "测验描述",
                "questions": [
                    {{
                        "question": "问题内容",
                        "type": "multiple_choice",
                        "options": ["选项A", "选项B", "选项C", "选项D"],
                        "correct_answer": 0,
                        "explanation": "解释"
                    }}
                ],
                "time_limit": 300
            }}
            """,
            
            'word_cloud': f"""
            基于以下课程内容，生成一个词云活动：
            课程内容：{course_content}
            网络资源：{web_resources}
            额外要求：{additional_prompt}{time_limit_str}
            
            请生成包含以下内容的JSON格式：
            {{
                "title": "词云活动标题",
                "description": "活动描述",
                "prompt": "请学生输入与主题相关的关键词",
                "max_words": 10,
                "min_word_length": 2
            }}
            """,
            
            'short_answer': f"""
            基于以下课程内容，生成一个简答题活动：
            课程内容：{course_content}
            网络资源：{web_resources}
            额外要求：{additional_prompt}{time_limit_str}
            
            请生成包含以下内容的JSON格式：
            {{
                "title": "简答题标题",
                "description": "活动描述",
                "questions": [
                    {{
                        "question": "问题内容",
                        "type": "short_answer",
                        "max_length": 500,
                        "sample_answer": "参考答案"
                    }}
                ],
                "time_limit": 600
            }}
            """,
            
            'mini_game': f"""
            基于以下课程内容，生成一个迷你游戏活动：
            课程内容：{course_content}
            网络资源：{web_resources}
            额外要求：{additional_prompt}{time_limit_str}
            
            请生成包含以下内容的JSON格式：
            {{
                "title": "游戏标题",
                "description": "游戏描述",
                "game_type": "matching",
                "rules": "游戏规则",
                "content": {{
                    "items": ["项目1", "项目2", "项目3"],
                    "matches": ["匹配1", "匹配2", "匹配3"]
                }}
            }}
            """
        }
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个教育技术专家，专门设计互动学习活动。请只返回纯JSON格式，不要包含任何其他文字或markdown标记。"},
                    {"role": "user", "content": prompts.get(activity_type, prompts['quiz'])}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            content = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if content.startswith('```json'):
                content = content.replace('```json', '').replace('```', '').strip()
            elif content.startswith('```'):
                content = content.replace('```', '').strip()
            
            # Try to parse JSON
            try:
                parsed_data = json.loads(content)
                return parsed_data
            except json.JSONDecodeError as e:
                # Try to extract JSON from the content
                import re
                json_match = re.search(r'\{[\s\S]*\}', content)
                if json_match:
                    try:
                        parsed_data = json.loads(json_match.group(0))
                        return parsed_data
                    except:
                        pass
                
                # If still cannot parse, return structured format
                return {
                    "title": f"AI生成的{activity_type}活动",
                    "description": content,
                    "raw_content": content,
                    "parse_error": str(e)
                }
                
        except Exception as e:
            return {
                "error": f"AI生成失败: {str(e)}",
                "title": f"AI生成的{activity_type}活动",
                "description": "AI服务暂时不可用，请手动创建活动。"
            }
    
    def analyze_responses(self, responses: List[Dict[str, Any]], activity_type: str) -> Dict[str, Any]:
        """分析学生回答"""
        
        if not responses:
            return {"error": "没有回答数据"}
        
        # 构建分析提示
        responses_text = "\n".join([
            f"学生{idx+1}: {resp.get('content', '')}" 
            for idx, resp in enumerate(responses)
        ])
        
        prompt = f"""
        请分析以下学生的回答，活动类型：{activity_type}
        
        学生回答：
        {responses_text}
        
        请提供以下分析（JSON格式）：
        {{
            "summary": "回答总结",
            "common_themes": ["主题1", "主题2", "主题3"],
            "similarity_groups": [
                {{
                    "group_id": 1,
                    "students": ["学生1", "学生2"],
                    "similarity_reason": "相似原因"
                }}
            ],
            "insights": ["洞察1", "洞察2"],
            "recommendations": ["建议1", "建议2"]
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个教育数据分析专家，专门分析学生学习数据。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.5
            )
            
            content = response.choices[0].message.content
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {
                    "summary": content,
                    "raw_analysis": content
                }
                
        except Exception as e:
            return {
                "error": f"AI分析失败: {str(e)}",
                "summary": "AI分析服务暂时不可用"
            }
    
    def generate_feedback(self, student_response: str, correct_answer: str = "", 
                         activity_type: str = "general") -> str:
        """生成个性化反馈"""
        
        prompt = f"""
        请为学生的回答生成建设性反馈：
        
        学生回答：{student_response}
        正确答案：{correct_answer}
        活动类型：{activity_type}
        
        请提供：
        1. 积极评价
        2. 改进建议
        3. 鼓励性话语
        
        保持友好和建设性的语调。
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个耐心的老师，善于给出建设性反馈。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"AI反馈生成失败: {str(e)}"
    
    def group_similar_answers(self, responses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """自动分组相似答案"""
        
        if len(responses) < 2:
            return [{"group_id": 1, "responses": responses}]
        
        # 使用AI进行相似度分析
        analysis = self.analyze_responses(responses, "grouping")
        
        if "similarity_groups" in analysis:
            return analysis["similarity_groups"]
        
        # 简单的基于关键词的分组（备用方案）
        groups = []
        used_responses = set()
        
        for i, resp in enumerate(responses):
            if i in used_responses:
                continue
                
            group = {"group_id": len(groups) + 1, "responses": [resp]}
            used_responses.add(i)
            
            # 简单的关键词匹配
            resp_words = set(resp.get('content', '').lower().split())
            
            for j, other_resp in enumerate(responses[i+1:], i+1):
                if j in used_responses:
                    continue
                    
                other_words = set(other_resp.get('content', '').lower().split())
                similarity = len(resp_words & other_words) / len(resp_words | other_words)
                
                if similarity > 0.3:  # 30%相似度阈值
                    group["responses"].append(other_resp)
                    used_responses.add(j)
            
            groups.append(group)
        
        return groups
    
    def answer_question(self, question: str, course_context: Dict[str, Any]) -> str:
        """基于课程上下文回答用户问题"""
        
        # 构建上下文信息
        course_info = course_context.get('course_info', {})
        documents = course_context.get('documents', [])
        activities = course_context.get('activities', [])
        
        # 构建上下文文本
        context_text = f"""
课程信息：
- 课程名称：{course_info.get('course_name', '未知')}
- 课程代码：{course_info.get('course_code', '未知')}
- 课程描述：{course_info.get('description', '无描述')}
"""
        
        # 添加文档信息
        if documents:
            context_text += "\n课程资料：\n"
            for doc in documents:
                context_text += f"- {doc.get('title', doc.get('filename', '未知'))}"
                if doc.get('description'):
                    context_text += f": {doc.get('description')}"
                if doc.get('content'):
                    # 限制文档内容长度
                    content = doc.get('content', '')[:2000]  # 最多2000字符
                    context_text += f"\n  内容摘要：{content}\n"
                context_text += "\n"
        
        # 添加活动信息
        if activities:
            context_text += "\n课程活动：\n"
            for activity in activities:
                context_text += f"- {activity.get('title', '未知活动')}"
                if activity.get('description'):
                    context_text += f": {activity.get('description')}"
                if activity.get('config'):
                    config = activity.get('config', {})
                    if isinstance(config, dict):
                        if config.get('question'):
                            context_text += f"\n  问题：{config.get('question')}"
                        if config.get('options'):
                            context_text += f"\n  选项：{', '.join(config.get('options', []))}"
                context_text += "\n"
        
        prompt = f"""
你是一个智能课程助手，专门帮助学生和教师解答关于课程的问题。

课程上下文信息：
{context_text}

用户问题：{question}

请基于以上课程信息回答用户的问题。要求：
1. 回答要准确、清晰、有帮助
2. 如果问题涉及课程资料，请引用具体的资料内容
3. 如果问题涉及活动，请说明活动的相关信息
4. 如果信息不足，请诚实说明，不要编造信息
5. 使用友好的语气，就像一位耐心的老师或助教

请直接回答问题，不需要额外的格式说明。
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个智能课程助手，专门帮助学生和教师解答关于课程的问题。你能够基于课程资料和活动信息提供准确、有帮助的回答。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"抱歉，AI服务暂时不可用：{str(e)}"
    
    def answer_general_question(self, question: str, user_courses: List[Dict[str, Any]] = None) -> str:
        """回答通用问题，对于课程相关问题引导用户到课程AI助手"""
        
        # 构建用户课程信息
        courses_info = ""
        if user_courses and len(user_courses) > 0:
            courses_info = "\n用户可用的课程：\n"
            for course in user_courses:
                courses_info += f"- {course.get('course_name', '未知')} ({course.get('course_code', '未知')})\n"
        
        prompt = f"""
你是一个智能通用助手，可以帮助用户解答各种问题。

{courses_info if courses_info else ""}

用户问题：{question}

请根据以下规则回答问题：
1. 对于一般性问题（如平台使用、功能说明、学习建议等），直接回答
2. 对于特定课程的问题（如"COMP5241的作业要求"、"某门课的考试时间"等），请引导用户使用该课程的AI助手
3. 如果问题涉及具体课程内容、资料、活动等，请引导用户到相应课程的AI助手
4. 使用友好、耐心的语气
5. 如果引导到课程AI助手，请说明："这个问题涉及具体课程内容，建议您使用该课程的AI助手，它能够基于课程资料和活动信息提供更准确的回答。您可以在课程详情页面找到'询问AI助手'按钮。"

请直接回答问题，不需要额外的格式说明。
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个智能通用助手，可以帮助用户解答各种问题。对于课程相关问题，你会引导用户使用课程特定的AI助手。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"抱歉，AI服务暂时不可用：{str(e)}"
