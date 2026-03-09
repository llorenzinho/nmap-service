# ----------------------------------------------------------------------
# Demo
# ----------------------------------------------------------------------
from nmap_service.cmd.nmap import NmapRunner
from nmap_service.cmd.run import CommandRunner
from nmap_service.config.runner import NmapCfg, RunnerCfg

if __name__ == "__main__":
    # --- CommandRunner generico ---
    runner = CommandRunner(cfg=RunnerCfg(timeout=10))
    res = runner.run("echo 'Hello from CommandRunner'")
    print("=== CommandRunner ===")
    print(f"stdout    : {res.stdout.strip()}")
    print(f"returncode: {res.returncode}")
    print(f"success   : {res.success}")
    print(f"model_dump: {res.model_dump()}\n")

    # # --- Validazione NmapScanConfig ---
    # print("=== NmapScanConfig validation ===")
    # try:
    #     NmapScanConfig(target="10.0.0.1", ports="abc-invalid", timeout=300)
    # except Exception as e:
    #     print(f"Errore atteso (ports non valide): {e}\n")

    # try:
    #     NmapScanConfig(target="10.0.0.1", extra_flags="-oX output.xml")
    # except Exception as e:
    #     print(f"Errore atteso (-oX in extra_flags): {e}\n")

    # --- NmapRunner ---
    # NOTA: richiede nmap installato e permessi adeguati.
    nmap = NmapRunner(cfg=NmapCfg(timeout=30))
    result = nmap.scan("scanme.nmap.org", ports="22,80,443", extra_flags="-sV")
    for host in result.hosts:
        print(f"{host.ip}: {[p.model_dump() for p in host.open_ports]}")
        # 45.33.32.156: [{'port': 22, 'protocol': 'tcp', 'service': 'ssh'}, {'port': 80, 'protocol': 'tcp', 'service': 'http'}]
