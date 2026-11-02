from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
)

from .database import Base


class Telemetry(Base):

    __tablename__ = "telemetry"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    agent_id = Column(
        String(100),
        nullable=False,
        index=True
    )

    timestamp = Column(
        DateTime,
        default=datetime.utcnow,
        index=True
    )

    cpu = Column(
        Float,
        default=0
    )

    memory = Column(
        Float,
        default=0
    )

    anomaly = Column(
        Boolean,
        default=False
    )

    anomaly_score = Column(
        Float,
        default=0
    )

    severity = Column(
        String(20),
        default="Normal"
    )

    risk_score = Column(
        Float,
        default=0
    )

    process_count = Column(
        Integer,
        default=0
    )

    network_connection_count = Column(
        Integer,
        default=0
    )

    processes_json = Column(
        Text,
        default="[]"
    )

    network_json = Column(
        Text,
        default="[]"
    )

    system_json = Column(
        Text,
        default="{}"
    )

    network_io_json = Column(
        Text,
        default="{}"
    )


class Incident(Base):

    __tablename__ = "incidents"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    agent_id = Column(
        String(100),
        nullable=False
    )

    timestamp = Column(
        DateTime,
        default=datetime.utcnow
    )

    alert = Column(
        String(255),
        nullable=False
    )

    severity = Column(
        String(20),
        nullable=False
    )

    anomaly_score = Column(
        Float,
        default=0
    )

    risk_score = Column(
        Float,
        default=0
    )

    cpu = Column(
        Float,
        default=0
    )

    memory = Column(
        Float,
        default=0
    )