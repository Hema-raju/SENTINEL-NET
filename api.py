from datetime import datetime
from flask import Blueprint, jsonify, request

from database import get_connection
from anomaly_detector import analyze_database_metrics
from risk_engine import calculate_risk
from alert_manager import create_alert, get_alert_message, should_create_alert


api = Blueprint("api", __name__)
AGENT_TIMEOUT_SECONDS = 15

# ============================================================
# BASIC API STATUS
# ============================================================

@api.route("/api/status", methods=["GET"])
def api_status():

    connection = get_connection()

    try:
        cursor = connection.cursor()

        # ----------------------------------------------------
        # Latest agent
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                agent_id,
                agent_name,
                hostname,
                operating_system,
                operating_system_version,
                operating_system_release,
                machine,
                processor,
                logical_cpu_count,
                physical_cpu_count,
                boot_time,
                first_seen,
                last_seen
            FROM agents
            ORDER BY id DESC
            LIMIT 1
            """
        )

        agent_row = cursor.fetchone()

        # ----------------------------------------------------
        # Latest system metric
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                agent_id,
                timestamp,
                cpu_usage,
                memory_usage,
                memory_total,
                memory_available,
                memory_used
            FROM system_metrics
            ORDER BY id DESC
            LIMIT 1
            """
        )

        metric_row = cursor.fetchone()

        # ----------------------------------------------------
        # Historical metrics for dashboard chart
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                timestamp,
                cpu_usage,
                memory_usage
            FROM system_metrics
            ORDER BY id DESC
            LIMIT 50
            """
        )

        history_rows = cursor.fetchall()

        history_rows = list(reversed(history_rows))

        # ----------------------------------------------------
        # Latest alert
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                agent_id,
                timestamp,
                cpu_usage,
                memory_usage,
                anomaly_detected,
                anomaly_score,
                risk_score,
                severity,
                message,
                reasons
            FROM alerts
            ORDER BY id DESC
            LIMIT 1
            """
        )

        alert_row = cursor.fetchone()

    finally:
        connection.close()


    # ========================================================
    # DEFAULT VALUES
    # ========================================================

    agent_data = {}
    metrics_data = {}
    system_info = {}
    history = []
    latest_alert = None


    # ========================================================
    # AGENT INFORMATION
    # ========================================================

    if agent_row:

      agent_status = "Offline"
    seconds_since_last_seen = None

    if agent_row["last_seen"]:
        try:
            last_seen_time = datetime.strptime(
                agent_row["last_seen"],
                "%Y-%m-%d %H:%M:%S"
            )

            seconds_since_last_seen = (
                datetime.now() - last_seen_time
            ).total_seconds()

            if seconds_since_last_seen <= AGENT_TIMEOUT_SECONDS:
                agent_status = "Online"

        except (ValueError, TypeError):
            agent_status = "Offline"

    agent_data = {
        "agent_id": agent_row["agent_id"],
        "agent_name": agent_row["agent_name"],
        "hostname": agent_row["hostname"],
        "last_seen": agent_row["last_seen"],
        "status": agent_status,
        "seconds_since_last_seen": (
            round(seconds_since_last_seen, 1)
            if seconds_since_last_seen is not None
            else None
        )
    }

    system_info = {
            "hostname": agent_row["hostname"],
            "operating_system": agent_row["operating_system"],
            "operating_system_version": agent_row["operating_system_version"],
            "operating_system_release": agent_row["operating_system_release"],
            "machine": agent_row["machine"],
            "processor": agent_row["processor"],
            "logical_cpu_count": agent_row["logical_cpu_count"],
            "physical_cpu_count": agent_row["physical_cpu_count"],
            "boot_time": agent_row["boot_time"]
        }


    # ========================================================
    # CURRENT METRICS
    # ========================================================

    if metric_row:

        metrics_data = {
            "cpu": float(metric_row["cpu_usage"] or 0),
            "memory": float(metric_row["memory_usage"] or 0),
            "cpu_usage": float(metric_row["cpu_usage"] or 0),
            "memory_usage": float(metric_row["memory_usage"] or 0),
            "memory_total": metric_row["memory_total"],
            "memory_available": metric_row["memory_available"],
            "memory_used": metric_row["memory_used"],
            "timestamp": metric_row["timestamp"]
        }


    # ========================================================
    # CHART HISTORY
    # ========================================================

    for row in history_rows:

        history.append(
            {
                "timestamp": row["timestamp"],
                "cpu": float(row["cpu_usage"] or 0),
                "memory": float(row["memory_usage"] or 0)
            }
        )


    # ========================================================
    # REAL ML ANALYSIS
    # ========================================================

    security_analysis = {
        "status": "insufficient_data",
        "anomaly_detected": False,
        "anomaly_score": None,
        "risk_score": 0,
        "severity": "Normal",
        "message": "Not enough monitoring data for ML analysis.",
        "records_analyzed": 0
    }


    try:

        analysis = analyze_database_metrics(limit=500)

        if analysis["status"] == "success":

            latest = analysis["latest"]

            cpu_usage = float(latest["cpu"])
            memory_usage = float(latest["memory"])
            anomaly_detected = bool(latest["anomaly"])
            anomaly_score = float(latest["score"])

            risk = calculate_risk(
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                anomaly_detected=anomaly_detected,
                anomaly_score=anomaly_score
            )

            security_analysis = {
                "status": "success",
                "anomaly_detected": anomaly_detected,
                "anomaly_score": anomaly_score,
                "risk_score": risk["risk_score"],
                "severity": risk["severity"],
                "reasons": risk["reasons"],
                "records_analyzed": analysis["records_analyzed"],
                "latest": {
                    "id": latest["id"],
                    "agent_id": latest["agent_id"],
                    "timestamp": latest["timestamp"],
                    "cpu": cpu_usage,
                    "memory": memory_usage,
                    "anomaly": anomaly_detected,
                    "score": anomaly_score
                }
            }

    except Exception as error:

        security_analysis = {
            "status": "error",
            "anomaly_detected": False,
            "anomaly_score": None,
            "risk_score": 0,
            "severity": "Normal",
            "message": f"ML analysis error: {error}",
            "records_analyzed": 0
        }


    # ========================================================
    # LATEST ALERT
    # ========================================================

    if alert_row:

        latest_alert = {
            "id": alert_row["id"],
            "agent_id": alert_row["agent_id"],
            "timestamp": alert_row["timestamp"],
            "cpu_usage": alert_row["cpu_usage"],
            "memory_usage": alert_row["memory_usage"],
            "anomaly_detected": bool(alert_row["anomaly_detected"]),
            "anomaly_score": alert_row["anomaly_score"],
            "risk_score": alert_row["risk_score"],
            "severity": alert_row["severity"],
            "message": alert_row["message"],
            "reasons": alert_row["reasons"]
        }


    # ========================================================
    # RESPONSE
    # ========================================================

    return jsonify(
        {
            "service": "SentinelNet Security Console API",
            "status": "running",
            "success": True,

            "agent": agent_data,

            "metrics": metrics_data,

            "system_info": system_info,

            "security_analysis": security_analysis,

            "latest_alert": latest_alert,

            "history": history
        }
    )


# ============================================================
# AGENT DATA RECEIVING ENDPOINT
# ============================================================

@api.route("/api/agent/data", methods=["POST"])
def receive_agent_data():

    data = request.get_json(silent=True)

    if not data:

        return jsonify(
            {
                "success": False,
                "error": "No JSON data received."
            }
        ), 400


    required_fields = [
        "agent_id",
        "agent_name",
        "timestamp",
        "system_info",
        "metrics",
        "processes",
        "network_connections"
    ]


    missing_fields = [
        field
        for field in required_fields
        if field not in data
    ]


    if missing_fields:

        return jsonify(
            {
                "success": False,
                "error": "Missing required fields.",
                "missing_fields": missing_fields
            }
        ), 400


    agent_id = data["agent_id"]
    agent_name = data["agent_name"]
    timestamp = data["timestamp"]
    system_info = data["system_info"]
    metrics = data["metrics"]
    processes = data["processes"]
    network_connections = data["network_connections"]
    received_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cpu_usage = float(metrics.get("cpu", 0))
    memory_usage = float(metrics.get("memory", 0))


    connection = get_connection()


    try:

        cursor = connection.cursor()


        # ====================================================
        # STORE / UPDATE AGENT
        # ====================================================

        cursor.execute(
            """
            SELECT id
            FROM agents
            WHERE agent_id = ?
            """,
            (agent_id,)
        )

        existing_agent = cursor.fetchone()


        if existing_agent:

            cursor.execute (
                """
                UPDATE agents
                SET
                    agent_name = ?,
                    hostname = ?,
                    operating_system = ?,
                    operating_system_version = ?,
                    operating_system_release = ?,
                    machine = ?,
                    processor = ?,
                    logical_cpu_count = ?,
                    physical_cpu_count = ?,
                    boot_time = ?,
                    last_seen = ?
                WHERE agent_id = ?
                """,
                (
                    agent_name,
                    system_info.get("hostname"),
                    system_info.get("operating_system"),
                    system_info.get("operating_system_version"),
                    system_info.get("operating_system_release"),
                    system_info.get("machine"),
                    system_info.get("processor"),
                    system_info.get("logical_cpu_count"),
                    system_info.get("physical_cpu_count"),
                    system_info.get("boot_time"),
                    received_at,
                    agent_id
                )
            )

        else:

            cursor.execute(
                """
                INSERT INTO agents (
                    agent_id,
                    agent_name,
                    hostname,
                    operating_system,
                    operating_system_version,
                    operating_system_release,
                    machine,
                    processor,
                    logical_cpu_count,
                    physical_cpu_count,
                    boot_time,
                    first_seen,
                    last_seen
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    agent_id,
                    agent_name,
                    system_info.get("hostname"),
                    system_info.get("operating_system"),
                    system_info.get("operating_system_version"),
                    system_info.get("operating_system_release"),
                    system_info.get("machine"),
                    system_info.get("processor"),
                    system_info.get("logical_cpu_count"),
                    system_info.get("physical_cpu_count"),
                    system_info.get("boot_time"),
                    timestamp,
                    received_at
                )
            )
        

        # ====================================================
        # STORE SYSTEM METRICS
        # ====================================================

        cursor.execute(
            """
            INSERT INTO system_metrics (
                agent_id,
                timestamp,
                cpu_usage,
                memory_usage,
                memory_total,
                memory_available,
                memory_used
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                agent_id,
                timestamp,
                cpu_usage,
                memory_usage,
                metrics.get("memory_total"),
                metrics.get("memory_available"),
                metrics.get("memory_used")
            )
        )


        # ====================================================
        # STORE PROCESS SNAPSHOTS
        # ====================================================

        for process in processes:

            try:

                cursor.execute(
                    """
                    INSERT INTO process_snapshots (
                        agent_id,
                        timestamp,
                        pid,
                        process_name,
                        status,
                        cpu_percent,
                        memory_percent,
                        username
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        agent_id,
                        timestamp,
                        process.get("pid"),
                        process.get("name"),
                        process.get("status"),
                        process.get("cpu_percent"),
                        process.get("memory_percent"),
                        process.get("username")
                    )
                )

            except Exception:
                continue


        # ====================================================
        # STORE NETWORK SNAPSHOTS
        # ====================================================

        for connection_data in network_connections:

            try:

                cursor.execute(
                    """
                    INSERT INTO network_snapshots (
                        agent_id,
                        timestamp,
                        pid,
                        process_name,
                        protocol,
                        local_ip,
                        local_port,
                        remote_ip,
                        remote_port,
                        status
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        agent_id,
                        timestamp,
                        connection_data.get("pid"),
                        connection_data.get("process_name"),
                        connection_data.get("protocol"),
                        connection_data.get("local_ip"),
                        connection_data.get("local_port"),
                        connection_data.get("remote_ip"),
                        connection_data.get("remote_port"),
                        connection_data.get("status")
                    )
                )

            except Exception:
                continue


        connection.commit()


    except Exception as error:

        connection.rollback()

        return jsonify(
            {
                "success": False,
                "error": f"Database error: {error}"
            }
        ), 500

    finally:

        connection.close()


    # ========================================================
    # REAL ML ANALYSIS
    # ========================================================

    try:

        analysis = analyze_database_metrics(limit=500)

        if analysis["status"] == "success":

            latest = analysis["latest"]

            anomaly_detected = bool(latest["anomaly"])
            anomaly_score = float(latest["score"])

            risk = calculate_risk(
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                anomaly_detected=anomaly_detected,
                anomaly_score=anomaly_score
            )

        else:

            anomaly_detected = False
            anomaly_score = 0.0

            risk = calculate_risk(
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                anomaly_detected=False,
                anomaly_score=0.0
            )


    except Exception:

        anomaly_detected = False
        anomaly_score = 0.0

        risk = calculate_risk(
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            anomaly_detected=False,
            anomaly_score=0.0
        )


    # ========================================================
    # ALERT MANAGEMENT
    # ========================================================

    alert = create_alert(
        agent_id=agent_id,
        timestamp=timestamp,
        cpu_usage=cpu_usage,
        memory_usage=memory_usage,
        anomaly_detected=anomaly_detected,
        anomaly_score=anomaly_score,
        risk_score=risk["risk_score"],
        severity=risk["severity"],
        reasons=risk["reasons"]
    )


    alert["message"] = get_alert_message(alert)


    alert_created = False


    if should_create_alert(alert):

        connection = get_connection()

        try:

            cursor = connection.cursor()

            reasons_text = "; ".join(
                alert["reasons"]
            )

            cursor.execute(
                """
                INSERT INTO alerts (
                    agent_id,
                    timestamp,
                    cpu_usage,
                    memory_usage,
                    anomaly_detected,
                    anomaly_score,
                    risk_score,
                    severity,
                    message,
                    reasons
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    alert["agent_id"],
                    alert["timestamp"],
                    alert["cpu_usage"],
                    alert["memory_usage"],
                    int(alert["anomaly_detected"]),
                    alert["anomaly_score"],
                    alert["risk_score"],
                    alert["severity"],
                    alert["message"],
                    reasons_text
                )
            )

            connection.commit()

            alert_created = True

        finally:

            connection.close()


    # ========================================================
    # FINAL RESPONSE TO AGENT
    # ========================================================

    return jsonify(
        {
            "success": True,
            "message": "Monitoring data received successfully.",

            "agent_id": agent_id,

            "stored": {
                "processes": len(processes),
                "network_connections": len(network_connections)
            },

            "security_analysis": {
                "anomaly_detected": anomaly_detected,
                "anomaly_score": anomaly_score,
                "risk_score": risk["risk_score"],
                "severity": risk["severity"],
                "reasons": risk["reasons"],
                "alert_created": alert_created
            }
        }
    ), 200

# ============================================================
# PROCESS MONITORING API
# ============================================================

@api.route("/api/processes", methods=["GET"])
def get_processes():

    connection = get_connection()

    try:

        cursor = connection.cursor()

        # ----------------------------------------------------
        # Find the latest monitoring timestamp
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT timestamp
            FROM process_snapshots
            ORDER BY id DESC
            LIMIT 1
            """
        )

        latest_row = cursor.fetchone()


        if not latest_row:

            return jsonify(
                {
                    "success": True,
                    "processes": [],
                    "count": 0
                }
            )


        latest_timestamp = latest_row["timestamp"]


        # ----------------------------------------------------
        # Get processes from the latest snapshot
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                pid,
                process_name,
                status,
                cpu_percent,
                memory_percent,
                username
            FROM process_snapshots
            WHERE timestamp = ?
            ORDER BY cpu_percent DESC
            """,
            (latest_timestamp,)
        )

        rows = cursor.fetchall()


        processes = []


        for row in rows:

            processes.append(
                {
                    "pid": row["pid"],
                    "process_name": row["process_name"],
                    "status": row["status"],
                    "cpu_percent": float(
                        row["cpu_percent"] or 0
                    ),
                    "memory_percent": float(
                        row["memory_percent"] or 0
                    ),
                    "username": row["username"]
                }
            )


        return jsonify(
            {
                "success": True,
                "timestamp": latest_timestamp,
                "processes": processes,
                "count": len(processes)
            }
        )


    except Exception as error:

        return jsonify(
            {
                "success": False,
                "error": str(error),
                "processes": [],
                "count": 0
            }
        ), 500


    finally:

        connection.close()

# ============================================================
# NETWORK MONITORING API
# ============================================================

@api.route("/api/network", methods=["GET"])
def get_network_data():

    connection = get_connection()

    try:

        cursor = connection.cursor()

        # ----------------------------------------------------
        # Find the latest network snapshot
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT timestamp
            FROM network_snapshots
            ORDER BY id DESC
            LIMIT 1
            """
        )

        latest_row = cursor.fetchone()

        if not latest_row:

            return jsonify(
                {
                    "success": True,
                    "network_connections": [],
                    "count": 0
                }
            )

        latest_timestamp = latest_row["timestamp"]

        # ----------------------------------------------------
        # Get network connections from latest snapshot
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                pid,
                process_name,
                protocol,
                local_ip,
                local_port,
                remote_ip,
                remote_port,
                status
            FROM network_snapshots
            WHERE timestamp = ?
            ORDER BY process_name ASC
            """,
            (latest_timestamp,)
        )

        rows = cursor.fetchall()

        network_connections = []

        for row in rows:

            network_connections.append(
                {
                    "pid": row["pid"],
                    "process_name": row["process_name"],
                    "protocol": row["protocol"],
                    "local_ip": row["local_ip"],
                    "local_port": row["local_port"],
                    "remote_ip": row["remote_ip"],
                    "remote_port": row["remote_port"],
                    "status": row["status"]
                }
            )

        return jsonify(
            {
                "success": True,
                "timestamp": latest_timestamp,
                "network_connections": network_connections,
                "count": len(network_connections)
            }
        )

    except Exception as error:

        return jsonify(
            {
                "success": False,
                "error": str(error),
                "network_connections": [],
                "count": 0
            }
        ), 500

    finally:

        connection.close()

# ============================================================
# NETWORK ANALYSIS API
# ============================================================

@api.route("/api/network/analysis", methods=["GET"])
def network_analysis():

    connection = get_connection()

    try:

        cursor = connection.cursor()

        # ----------------------------------------------------
        # Find the latest network snapshot
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT timestamp
            FROM network_snapshots
            ORDER BY id DESC
            LIMIT 1
            """
        )

        latest_row = cursor.fetchone()

        if not latest_row:

            return jsonify(
                {
                    "success": True,
                    "message": "No network data available.",
                    "analysis": {
                        "total": 0,
                        "tcp": 0,
                        "udp": 0,
                        "listen": 0,
                        "established": 0,
                        "syn_sent": 0,
                        "close_wait": 0,
                        "external_established": 0
                    }
                }
            )


        latest_timestamp = latest_row["timestamp"]


        # ----------------------------------------------------
        # Get latest network snapshot
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                protocol,
                local_ip,
                remote_ip,
                status
            FROM network_snapshots
            WHERE timestamp = ?
            """,
            (latest_timestamp,)
        )

        rows = cursor.fetchall()


        # ----------------------------------------------------
        # Initialize counters
        # ----------------------------------------------------

        total = len(rows)

        tcp = 0
        udp = 0

        listen = 0
        established = 0
        syn_sent = 0
        close_wait = 0

        external_established = 0


        # ----------------------------------------------------
        # Analyze connections
        # ----------------------------------------------------

        for row in rows:

            protocol = row["protocol"]
            local_ip = row["local_ip"]
            remote_ip = row["remote_ip"]
            status = row["status"]


            # Protocol counts

            if protocol == "TCP":
                tcp += 1

            elif protocol == "UDP":
                udp += 1


            # Connection state counts

            if status == "LISTEN":
                listen += 1

            elif status == "ESTABLISHED":
                established += 1

            elif status == "SYN_SENT":
                syn_sent += 1

            elif status == "CLOSE_WAIT":
                close_wait += 1


            # ------------------------------------------------
            # External established connections
            # ------------------------------------------------
            #
            # Localhost connections such as:
            # 127.0.0.1
            # ::1
            #
            # are not counted as external.
            #

            if (
                status == "ESTABLISHED"
                and remote_ip
                and remote_ip not in (
                    "127.0.0.1",
                    "::1",
                    "0.0.0.0",
                    "::"
                )
            ):

                external_established += 1


        # ----------------------------------------------------
        # Build analysis result
        # ----------------------------------------------------

        analysis = {

            "total": total,

            "tcp": tcp,

            "udp": udp,

            "listen": listen,

            "established": established,

            "syn_sent": syn_sent,

            "close_wait": close_wait,

            "external_established":
                external_established,

            "timestamp":
                latest_timestamp
        }


        return jsonify(
            {
                "success": True,
                "analysis": analysis
            }
        )


    except Exception as error:

        return jsonify(
            {
                "success": False,
                "error": str(error)
            }
        ), 500


    finally:

        connection.close()
        # ============================================================
# NETWORK RISK ANALYSIS API
# ============================================================

@api.route("/api/network/risk", methods=["GET"])
def network_risk_analysis():

    connection = get_connection()

    try:

        cursor = connection.cursor()

        # ----------------------------------------------------
        # Find latest network snapshot
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT timestamp
            FROM network_snapshots
            ORDER BY id DESC
            LIMIT 1
            """
        )

        latest_row = cursor.fetchone()

        if not latest_row:

            return jsonify(
                {
                    "success": True,
                    "risk": {
                        "status": "Normal",
                        "score": 0,
                        "reasons": [
                            "No network data available."
                        ]
                    }
                }
            )


        latest_timestamp = latest_row["timestamp"]


        # ----------------------------------------------------
        # Get latest snapshot
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                protocol,
                remote_ip,
                status
            FROM network_snapshots
            WHERE timestamp = ?
            """,
            (latest_timestamp,)
        )

        rows = cursor.fetchall()


        # ----------------------------------------------------
        # Count network indicators
        # ----------------------------------------------------

        total = len(rows)

        established = 0
        external_established = 0
        syn_sent = 0
        close_wait = 0


        for row in rows:

            status = row["status"]
            remote_ip = row["remote_ip"]


            if status == "ESTABLISHED":

                established += 1


                if (
                    remote_ip
                    and remote_ip not in (
                        "127.0.0.1",
                        "::1",
                        "0.0.0.0",
                        "::"
                    )
                ):

                    external_established += 1


            elif status == "SYN_SENT":

                syn_sent += 1


            elif status == "CLOSE_WAIT":

                close_wait += 1


        # ----------------------------------------------------
        # Calculate network activity score
        # ----------------------------------------------------

        score = 0

        reasons = []


        if external_established >= 30:

            score += 40

            reasons.append(
                "Large number of external established connections."
            )

        elif external_established >= 15:

            score += 25

            reasons.append(
                "Elevated number of external established connections."
            )

        elif external_established >= 5:

            score += 10

            reasons.append(
                "Multiple external established connections detected."
            )


        if syn_sent >= 20:

            score += 30

            reasons.append(
                "Large number of outbound connection attempts."
            )

        elif syn_sent >= 10:

            score += 20

            reasons.append(
                "Elevated outbound connection attempts."
            )

        elif syn_sent >= 5:

            score += 10

            reasons.append(
                "Several outbound connection attempts detected."
            )


        if close_wait >= 20:

            score += 20

            reasons.append(
                "Large number of connections waiting to close."
            )

        elif close_wait >= 10:

            score += 10

            reasons.append(
                "Elevated number of connections waiting to close."
            )


        # ----------------------------------------------------
        # Limit score
        # ----------------------------------------------------

        score = min(score, 100)


        # ----------------------------------------------------
        # Determine status
        # ----------------------------------------------------

        if score >= 60:

            status = "High"

        elif score >= 30:

            status = "Elevated"

        else:

            status = "Normal"


        if not reasons:

            reasons.append(
                "No significant network activity indicators detected."
            )


        # ----------------------------------------------------
        # Return result
        # ----------------------------------------------------

        return jsonify(
            {
                "success": True,

                "risk": {

                    "status": status,

                    "score": score,

                    "total_connections": total,

                    "established":
                        established,

                    "external_established":
                        external_established,

                    "syn_sent":
                        syn_sent,

                    "close_wait":
                        close_wait,

                    "timestamp":
                        latest_timestamp,

                    "reasons":
                        reasons
                }
            }
        )


    except Exception as error:

        return jsonify(
            {
                "success": False,
                "error": str(error)
            }
        ), 500


    finally:
        connection.close()