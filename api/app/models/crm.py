from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database.db import Base


class Client(Base):
    __tablename__ = "t_crm_client"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(50), nullable=True, index=True)
    birth_date = Column(Date, nullable=True)
    birth_time = Column(String(10), nullable=True)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    sessions = relationship(
        "Session", back_populates="client", cascade="all, delete-orphan"
    )
    calculations = relationship(
        "Calculation", back_populates="client", cascade="all, delete-orphan"
    )
    notes_rel = relationship(
        "Note", back_populates="client", cascade="all, delete-orphan"
    )


class Session(Base):
    __tablename__ = "t_crm_session"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(
        Integer, ForeignKey("t_crm_client.id", ondelete="CASCADE"), nullable=False
    )
    date = Column(Date, nullable=False, index=True)
    notes = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    client = relationship("Client", back_populates="sessions")


class Calculation(Base):
    __tablename__ = "t_crm_calculation"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(
        Integer, ForeignKey("t_crm_client.id", ondelete="CASCADE"), nullable=False
    )
    calculation_type = Column(
        String(50), nullable=False, index=True
    )  # "tongshu", "qimen", "bazi", etc.
    reference_id = Column(
        String(255), nullable=False
    )  # ID of the calculation in the respective system
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    client = relationship("Client", back_populates="calculations")


class Note(Base):
    __tablename__ = "t_crm_note"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(
        Integer, ForeignKey("t_crm_client.id", ondelete="CASCADE"), nullable=False
    )
    note_text = Column(Text, nullable=False)
    calculation_id = Column(
        String(255), nullable=True
    )  # Optional link to a specific calculation

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    client = relationship("Client", back_populates="notes_rel")
