from flask import Blueprint, request, jsonify
from src.models.note import Note
from src.models.user import User
from src.database import db

note_bp = Blueprint('note', __name__)

@note_bp.route('/', methods=['GET'])
def get_notes():
    """获取所有笔记"""
    user_id = request.args.get('user_id')
    if user_id:
        notes = Note.query.filter_by(user_id=user_id).all()
    else:
        notes = Note.query.all()
    return jsonify([note.to_dict() for note in notes])

@note_bp.route('/<int:note_id>', methods=['GET'])
def get_note(note_id):
    """获取特定笔记"""
    note = Note.query.get_or_404(note_id)
    return jsonify(note.to_dict())

@note_bp.route('/', methods=['POST'])
def create_note():
    """创建新笔记"""
    data = request.get_json()
    
    if not data or not data.get('title') or not data.get('content') or not data.get('user_id'):
        return jsonify({'error': '缺少必要字段'}), 400
    
    # 检查用户是否存在
    user = User.query.get(data['user_id'])
    if not user:
        return jsonify({'error': '用户不存在'}), 400
    
    # 创建新笔记
    note = Note(
        title=data['title'],
        content=data['content'],
        user_id=data['user_id']
    )
    
    db.session.add(note)
    db.session.commit()
    
    return jsonify(note.to_dict()), 201

@note_bp.route('/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    """更新笔记"""
    note = Note.query.get_or_404(note_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': '没有提供数据'}), 400
    
    if 'title' in data:
        note.title = data['title']
    if 'content' in data:
        note.content = data['content']
    
    db.session.commit()
    return jsonify(note.to_dict())

@note_bp.route('/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    """删除笔记"""
    note = Note.query.get_or_404(note_id)
    db.session.delete(note)
    db.session.commit()
    return jsonify({'message': '笔记已删除'}), 200
