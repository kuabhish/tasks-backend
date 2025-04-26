from uuid import uuid4
from app import db

class Dependency(db.Model):
    __tablename__ = 'dependencies'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    task_id = db.Column(db.String(36), db.ForeignKey('tasks.id'), nullable=False)
    depends_on_task_id = db.Column(db.String(36), db.ForeignKey('tasks.id'), nullable=True)
    depends_on_subtask_id = db.Column(db.String(36), db.ForeignKey('subtasks.id'), nullable=True)

    __table_args__ = (
        db.CheckConstraint(
            '(depends_on_task_id IS NOT NULL AND depends_on_subtask_id IS NULL) OR '
            '(depends_on_task_id IS NULL AND depends_on_subtask_id IS NOT NULL)',
            name='check_depends_on_task_or_subtask'
        ),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'taskId': self.task_id,
            'dependsOnTaskId': self.depends_on_task_id,
            'dependsOnSubtaskId': self.depends_on_subtask_id
        }