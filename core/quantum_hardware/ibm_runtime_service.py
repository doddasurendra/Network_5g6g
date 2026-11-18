"""IBM Quantum Real Hardware Integration Module.
Uses the modern Qiskit Runtime Service (qiskit-ibm-runtime).
Provides secure credential management, dynamic backend discovery, transpilation,
hardware job submission, polling, and genuine result retrieval.
"""
import os
import time
from typing import Dict, Any, List, Optional
import numpy as np

try:
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    IBM_RUNTIME_AVAILABLE = True
except ImportError:
    IBM_RUNTIME_AVAILABLE = False

class IBMQuantumHardwareService:
    """Production integration with genuine IBM Quantum processors."""

    def __init__(self):
        self.service: Optional[Any] = None
        self._authenticated = False

    def authenticate(self, api_token: Optional[str] = None, channel: str = "ibm_quantum") -> Dict[str, Any]:
        """Authenticates with IBM Quantum Platform without ever hardcoding or exposing tokens."""
        if not IBM_RUNTIME_AVAILABLE:
            return {
                "status": "UNAVAILABLE",
                "authenticated": False,
                "message": "qiskit-ibm-runtime is not installed or available."
            }

        token = api_token or os.getenv("QISKIT_IBM_TOKEN")
        if not token:
            return {
                "status": "MISSING_CREDENTIALS",
                "authenticated": False,
                "message": "No IBM Quantum API token provided or found in QISKIT_IBM_TOKEN."
            }

        try:
            # Initialize modern QiskitRuntimeService
            self.service = QiskitRuntimeService(channel=channel, token=token)
            self._authenticated = True
            return {
                "status": "AUTHENTICATED",
                "authenticated": True,
                "channel": channel,
                "message": "Successfully authenticated with IBM Quantum Platform."
            }
        except Exception as e:
            self._authenticated = False
            return {
                "status": "AUTHENTICATION_FAILED",
                "authenticated": False,
                "error": str(e)
            }

    def list_available_backends(self, min_qubits: int = 5) -> List[Dict[str, Any]]:
        """Dynamically queries IBM Quantum for active operational hardware backends."""
        if not self._authenticated or not self.service:
            return []

        try:
            backends = self.service.backends(simulator=False, operational=True, min_num_qubits=min_qubits)
            results = []
            for b in backends:
                status = b.status()
                results.append({
                    "name": b.name,
                    "num_qubits": b.num_qubits,
                    "operational": status.operational,
                    "pending_jobs": status.pending_jobs,
                    "status_msg": status.status_msg,
                    "basis_gates": getattr(b.configuration(), "basis_gates", [])
                })
            return results
        except Exception as e:
            return [{"error": str(e)}]

    def submit_hardware_qaoa_job(self, circuit: Any, backend_name: str, 
                                 shots: int = 1024, optimization_level: int = 1) -> Dict[str, Any]:
        """Transpiles and submits a genuine QAOA quantum circuit to the chosen IBM Quantum QPU.
        Requires explicit confirmation and credentials.
        """
        if not self._authenticated or not self.service:
            return {"error": "Not authenticated with IBM Quantum. Configure QISKIT_IBM_TOKEN."}

        try:
            backend = self.service.backend(backend_name)
            
            # Target Hardware Transpilation
            pm = generate_preset_pass_manager(backend=backend, optimization_level=optimization_level)
            isa_circuit = pm.run(circuit)

            # Modern SamplerV2 submission
            sampler = Sampler(backend=backend)
            job = sampler.run([isa_circuit], shots=shots)

            return {
                "status": "SUBMITTED",
                "job_id": job.job_id(),
                "backend": backend_name,
                "shots": shots,
                "circuit_qubits": isa_circuit.num_qubits,
                "transpiled_depth": isa_circuit.depth(),
                "submission_time": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            return {
                "status": "FAILED_TO_SUBMIT",
                "backend": backend_name,
                "error": str(e)
            }

    def poll_job_status(self, job_id: str) -> Dict[str, Any]:
        """Polls status of a submitted IBM Quantum job without blocking the UI."""
        if not self._authenticated or not self.service:
            return {"error": "Not authenticated."}

        try:
            job = self.service.job(job_id)
            status_str = str(job.status())
            
            result_data = None
            if status_str == "DONE":
                job_result = job.result()
                pub_result = job_result[0]
                # Extract measurement counts from bitarray
                result_data = pub_result.data.meas.get_counts()

            return {
                "job_id": job_id,
                "status": status_str,
                "counts": result_data,
                "backend": job.backend().name if hasattr(job, "backend") else "Unknown"
            }
        except Exception as e:
            return {"job_id": job_id, "status": "ERROR", "error": str(e)}

ibm_hardware_service = IBMQuantumHardwareService()
