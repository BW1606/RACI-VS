from datetime import datetime
from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

ROLES = ("R", "A", "C", "I", "V", "S")

R_SUBCATEGORIES = (
    "Ausführende Tätigkeit",
    "Gewährleistung",
    "Koordination",
    "Veranlassung",
    "Mitwirkung",
)


class Organisation(Base):
    __tablename__ = "organisations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    functions: Mapped[list["Function"]] = relationship("Function", back_populates="organisation")
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="organisation")


class Function(Base):
    __tablename__ = "functions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    organisation_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("organisations.id"), nullable=True)
    parent_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("functions.id"), nullable=True)
    description: Mapped[str] = mapped_column(Text, default="")
    aim: Mapped[str] = mapped_column(Text, default="")
    emergency_rep_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("functions.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    organisation: Mapped["Organisation | None"] = relationship("Organisation", back_populates="functions")
    parent: Mapped["Function | None"] = relationship(
        "Function", foreign_keys=[parent_id], remote_side="Function.id", back_populates="children"
    )
    children: Mapped[list["Function"]] = relationship(
        "Function", foreign_keys=[parent_id], back_populates="parent"
    )
    emergency_rep: Mapped["Function | None"] = relationship(
        "Function", foreign_keys=[emergency_rep_id], remote_side="Function.id"
    )
    task_roles: Mapped[list["FunctionTaskRole"]] = relationship(
        "FunctionTaskRole", back_populates="function", cascade="all, delete-orphan"
    )


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    organisation_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("organisations.id"), nullable=True)
    description: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    organisation: Mapped["Organisation | None"] = relationship("Organisation", back_populates="tasks")
    function_roles: Mapped[list["FunctionTaskRole"]] = relationship(
        "FunctionTaskRole", back_populates="task", cascade="all, delete-orphan"
    )


class FunctionTaskRole(Base):
    __tablename__ = "function_task_roles"
    __table_args__ = (UniqueConstraint("function_id", "task_id", name="uq_function_task"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    function_id: Mapped[int] = mapped_column(Integer, ForeignKey("functions.id"), nullable=False)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("tasks.id"), nullable=False)
    role: Mapped[str] = mapped_column(Enum(*ROLES, name="role_enum"), nullable=False)
    r_subcategory: Mapped[str | None] = mapped_column(String(50), nullable=True)

    function: Mapped["Function"] = relationship("Function", back_populates="task_roles")
    task: Mapped["Task"] = relationship("Task", back_populates="function_roles")
